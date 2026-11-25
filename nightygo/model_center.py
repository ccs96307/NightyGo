"""Live KataGo model catalogue, hardware advice, and atomic downloads."""

from __future__ import annotations

from collections.abc import Sequence
import csv
import json
import logging
import os
import platform
import re
import shutil
import subprocess
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from PySide6 import QtCore, QtNetwork, QtWidgets


logger = logging.getLogger(__name__)
CATALOG_URL = "https://katagotraining.org/networks/"
LICENSE_URL = "https://katagotraining.org/network_license/"
MODEL_HOST = "media.katagotraining.org"
MODEL_ROLE = QtCore.Qt.ItemDataRole.UserRole


@dataclass(frozen=True)
class HardwareProfile:
    """Current host memory and detected NVIDIA GPU memory."""

    total_ram_bytes: int = 0
    available_ram_bytes: int = 0
    gpu_name: str = ""
    gpu_total_bytes: int = 0
    gpu_available_bytes: int = 0

    @property
    def total_ram_gib(self) -> float:
        return self.total_ram_bytes / (1024**3)

    @property
    def available_ram_gib(self) -> float:
        return self.available_ram_bytes / (1024**3)

    @property
    def gpu_available_gib(self) -> float:
        return self.gpu_available_bytes / (1024**3)

    @classmethod
    def detect(cls) -> HardwareProfile:
        total = available = 0
        system = platform.system()
        try:
            if system == "Linux":
                values = {}
                for line in Path("/proc/meminfo").read_text().splitlines():
                    key, value = line.split(":", 1)
                    if key in ("MemTotal", "MemAvailable"):
                        values[key] = int(value.strip().split()[0]) * 1024
                total, available = values.get("MemTotal", 0), values.get("MemAvailable", 0)
            elif system == "Windows":
                import ctypes

                class MemoryStatus(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]

                status = MemoryStatus()
                status.dwLength = ctypes.sizeof(status)
                if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                    total, available = status.ullTotalPhys, status.ullAvailPhys
            elif system == "Darwin":
                page_size = os.sysconf("SC_PAGE_SIZE")
                total = os.sysconf("SC_PHYS_PAGES") * page_size
                page_counts = subprocess.run(
                    ["vm_stat"], capture_output=True, text=True, timeout=2, check=False
                ).stdout
                free_pages = sum(
                    int(match.group(1))
                    for line in page_counts.splitlines()
                    if (match := re.search(r"(?:Pages free|Pages inactive|Pages speculative):\s+(\d+)", line))
                )
                available = free_pages * page_size
        except (OSError, ValueError, subprocess.SubprocessError):
            logger.exception("Could not detect system memory")

        gpu_name = ""
        gpu_total = gpu_available = 0
        if shutil.which("nvidia-smi"):
            try:
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name,memory.total,memory.free", "--format=csv,noheader,nounits"],
                    capture_output=True, text=True, timeout=2, check=False,
                )
                rows = list(csv.reader(result.stdout.splitlines(), skipinitialspace=True))
                if result.returncode == 0 and rows:
                    gpu_name = rows[0][0].strip()
                    gpu_total = int(rows[0][1]) * 1024**2
                    gpu_available = int(rows[0][2]) * 1024**2
                    if len(rows) > 1:
                        gpu_name += f" (+{len(rows) - 1} GPU(s))"
            except (OSError, ValueError, subprocess.SubprocessError):
                logger.info("NVIDIA GPU memory query was unavailable", exc_info=True)
        return cls(total, available, gpu_name, gpu_total, gpu_available)


@dataclass(frozen=True)
class ModelRecord:
    name: str
    download_url: str
    uploaded_at: str = ""
    rating: str = ""
    tier: str = "balanced"

    @property
    def filename(self) -> str:
        return self.name + ".bin.gz"


class _NetworkTableParser(HTMLParser):
    """Extract network-file links and the adjacent name/date/rating cells."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.records: list[ModelRecord] = []
        self._row: list[tuple[str, list[str]]] | None = None
        self._cell_text: list[str] | None = None
        self._cell_links: list[str] = []
        self._in_cell = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = dict(attrs)
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell_text, self._cell_links, self._in_cell = [], [], True
        elif tag == "a" and self._in_cell:
            href = attrs_map.get("href") or ""
            if href:
                self._cell_links.append(href)

    def handle_data(self, data: str) -> None:
        if self._in_cell and self._cell_text is not None:
            self._cell_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in ("td", "th") and self._in_cell and self._row is not None:
            self._row.append((" ".join(" ".join(self._cell_text or []).split()), self._cell_links))
            self._in_cell = False
        elif tag == "tr" and self._row is not None:
            self._finish_row(self._row)
            self._row = None

    def _finish_row(self, cells: list[tuple[str, list[str]]]) -> None:
        if len(cells) < 4:
            return
        name = cells[0][0]
        if not name.startswith("kata1-"):
            return
        urls = [url for _text, links in cells for url in links]
        model_url = next((url for url in urls if url.endswith(".bin.gz")), "")
        if not model_url.startswith(f"https://{MODEL_HOST}/"):
            return
        if len(self.records) >= 500:
            return
        self.records.append(ModelRecord(
            name=name,
            download_url=model_url,
            uploaded_at=cells[1][0],
            rating=cells[2][0],
            tier=classify_model(name),
        ))


def classify_model(name: str) -> str:
    """Classify model compute tiers by published KataGo architecture names."""
    if re.search(r"(?:tf3-b11c768|b40c768)", name):
        return "maximum"
    if re.search(r"(?:tf3-b10c512|b28c512|b60c320)", name):
        return "strong"
    if re.search(r"(?:tf2-b10c384|b18c384|b40c256|b20c256)", name):
        return "balanced"
    return "light"


def parse_model_catalog(html: str) -> list[ModelRecord]:
    parser = _NetworkTableParser()
    parser.feed(html)
    return parser.records


def recommend_tier(profile: HardwareProfile) -> str:
    """Return a conservative recommendation using currently free memory."""
    if profile.gpu_name and profile.gpu_available_gib >= 8 and profile.available_ram_gib >= 8:
        return "maximum"
    if profile.gpu_name and profile.gpu_available_gib >= 5 and profile.available_ram_gib >= 6:
        return "strong"
    if profile.gpu_name and profile.gpu_available_gib >= 3 and profile.available_ram_gib >= 4:
        return "balanced"
    if profile.available_ram_gib >= 16:
        return "strong"
    if profile.available_ram_gib >= 8:
        return "balanced"
    return "light"


def apply_model_argument(arguments: Sequence[str], model_path: str) -> tuple[str, ...]:
    """Add or replace KataGo's selected model flag in launch arguments."""
    result = list(arguments)
    if not model_path:
        return tuple(result)
    if "-model" in result:
        index = result.index("-model")
        if index + 1 < len(result):
            result[index + 1] = model_path
        else:
            result.append(model_path)
    else:
        option_index = next(
            (i for i, value in enumerate(result) if value.startswith("-model=")),
            None,
        )
        if option_index is None:
            result.extend(("-model", model_path))
        else:
            result[option_index] = f"-model={model_path}"
    return tuple(result)


_TIER_NAME = {
    "light": "輕量",
    "balanced": "均衡",
    "strong": "高棋力",
    "maximum": "最高棋力",
}
_TIER_ORDER = {"light": 0, "balanced": 1, "strong": 2, "maximum": 3}


class ModelCenterDialog(QtWidgets.QDialog):
    """Browse official KataGo networks, get a memory fit hint, and install one."""

    modelSelected = QtCore.Signal(str)

    def __init__(self, settings: QtCore.QSettings, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("NightyGo · AI Model Center")
        self.setMinimumSize(850, 610)
        self._settings = settings
        self._profile = HardwareProfile.detect()
        self._manager = QtNetwork.QNetworkAccessManager(self)
        self._catalog_reply: QtNetwork.QNetworkReply | None = None
        self._probe_reply: QtNetwork.QNetworkReply | None = None
        self._download_reply: QtNetwork.QNetworkReply | None = None
        self._save_file: QtCore.QSaveFile | None = None
        self._expected_bytes = 0
        self._download_bytes_written = 0
        self._selected: ModelRecord | None = None
        self._catalog: list[ModelRecord] = []
        self._catalog_cache = "model-center/catalog-html"
        default_download_dir = Path(QtCore.QStandardPaths.writableLocation(
            QtCore.QStandardPaths.StandardLocation.AppDataLocation
        )) / "models"
        self._download_dir = Path(str(settings.value("model-center/download-dir", default_download_dir)))

        self._hardware_label = QtWidgets.QLabel(self)
        self._hardware_label.setWordWrap(True)
        refresh_hardware = QtWidgets.QPushButton("重新偵測", self)
        refresh_hardware.clicked.connect(self._refresh_hardware)
        hardware_row = QtWidgets.QHBoxLayout()
        hardware_row.addWidget(self._hardware_label, 1)
        hardware_row.addWidget(refresh_hardware)

        self._search = QtWidgets.QLineEdit(self)
        self._search.setPlaceholderText("搜尋模型名稱 / 架構")
        self._search.textChanged.connect(self._populate_catalog)
        self._models = QtWidgets.QTreeWidget(self)
        self._models.setHeaderLabels(("模型", "棋力評分", "上傳日期", "記憶體建議"))
        self._models.setRootIsDecorated(False)
        self._models.setAlternatingRowColors(True)
        self._models.currentItemChanged.connect(self._selection_changed)

        self._details = QtWidgets.QLabel("正在讀取 KataGo 官方模型目錄…", self)
        self._details.setWordWrap(True)
        self._details.setMinimumHeight(74)
        self._folder_label = QtWidgets.QLabel(str(self._download_dir), self)
        self._folder_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        folder_button = QtWidgets.QPushButton("選擇資料夾…", self)
        folder_button.clicked.connect(self._choose_download_folder)
        folder_row = QtWidgets.QHBoxLayout()
        folder_row.addWidget(QtWidgets.QLabel("下載位置："), 0)
        folder_row.addWidget(self._folder_label, 1)
        folder_row.addWidget(folder_button)

        self._progress = QtWidgets.QProgressBar(self)
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._status = QtWidgets.QLabel("模型由 katagotraining.org 提供；此頁不會下載或安裝 KataGo 執行檔。", self)
        self._status.setWordWrap(True)
        self._download_button = QtWidgets.QPushButton("下載並設為目前模型", self)
        self._download_button.clicked.connect(self._download_or_use_selected)
        self._download_only_button = QtWidgets.QPushButton("只下載", self)
        self._download_only_button.clicked.connect(lambda: self._begin_download(use_when_done=False))
        self._cancel_button = QtWidgets.QPushButton("取消下載", self)
        self._cancel_button.clicked.connect(self._cancel_download)
        self._cancel_button.setEnabled(False)
        actions = QtWidgets.QHBoxLayout()
        actions.addWidget(self._download_button)
        actions.addWidget(self._download_only_button)
        actions.addWidget(self._cancel_button)

        license_link = QtWidgets.QLabel(
            f'模型授權與來源：<a href="{LICENSE_URL}">KataGo Neural Network License</a>'
            f' · <a href="{CATALOG_URL}">官方模型目錄</a>', self
        )
        license_link.setOpenExternalLinks(True)
        note = QtWidgets.QLabel(
            "記憶體提示是依目前可用 RAM／NVIDIA VRAM 和網路架構計算的保守估計。"
            "KataGo 的搜尋快取也會佔用記憶體，實際需求會隨執行後端、批次大小及快取設定改變。",
            self,
        )
        note.setWordWrap(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(hardware_row)
        layout.addWidget(self._search)
        layout.addWidget(self._models, 1)
        layout.addWidget(self._details)
        layout.addLayout(folder_row)
        layout.addWidget(self._progress)
        layout.addWidget(self._status)
        layout.addLayout(actions)
        layout.addWidget(license_link)
        layout.addWidget(note)
        self._refresh_hardware()
        self._load_cached_catalog()
        self._fetch_catalog()

    def _refresh_hardware(self) -> None:
        self._profile = HardwareProfile.detect()
        ram = f"RAM {self._profile.available_ram_gib:.1f} / {self._profile.total_ram_gib:.1f} GiB 可用 / 總量"
        if self._profile.gpu_name:
            gpu_label = self._profile.gpu_name
            if not gpu_label.casefold().startswith("nvidia"):
                gpu_label = f"NVIDIA {gpu_label}"
            gpu = f"{gpu_label} · VRAM {self._profile.gpu_available_gib:.1f} / {self._profile.gpu_total_bytes / 1024**3:.1f} GiB 可用 / 總量"
        else:
            gpu = "未偵測到可讀取的 GPU VRAM（建議先依系統 RAM 評估）"
        tier = _TIER_NAME[recommend_tier(self._profile)]
        self._hardware_label.setText(f"<b>本機規格</b>　{ram}<br>{gpu}<br><b>建議模型級別：{tier}</b>")
        self._populate_catalog()

    def _fetch_catalog(self) -> None:
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(CATALOG_URL))
        request.setHeader(QtNetwork.QNetworkRequest.KnownHeaders.UserAgentHeader, "NightyGo Model Center")
        request.setTransferTimeout(45_000)
        request.setAttribute(
            QtNetwork.QNetworkRequest.Attribute.RedirectPolicyAttribute,
            QtNetwork.QNetworkRequest.RedirectPolicy.NoLessSafeRedirectPolicy,
        )
        self._catalog_reply = self._manager.get(request)
        self._catalog_reply.finished.connect(self._catalog_finished)

    def _catalog_finished(self) -> None:
        reply = self._catalog_reply
        self._catalog_reply = None
        if reply is None:
            return
        if reply.error() == QtNetwork.QNetworkReply.NetworkError.NoError:
            html = bytes(reply.readAll()).decode("utf-8", errors="replace")
            records = parse_model_catalog(html)
            if records:
                self._settings.setValue(
                    self._catalog_cache,
                    json.dumps(
                        [
                            {
                                "name": model.name,
                                "download_url": model.download_url,
                                "uploaded_at": model.uploaded_at,
                                "rating": model.rating,
                            }
                            for model in records
                        ],
                        ensure_ascii=False,
                    ),
                )
                self._catalog = records
                self._populate_catalog()
                self._status.setText(f"已更新官方模型目錄：{len(records)} 個模型。")
            else:
                self._status.setText("官方目錄格式有變更，保留上次載入的模型清單。")
        else:
            if reply.error() != QtNetwork.QNetworkReply.NetworkError.OperationCanceledError:
                logger.warning("KataGo model catalogue unavailable: %s", reply.errorString())
                self._status.setText("無法連線更新目錄；目前顯示上次快取的模型清單。")
        reply.deleteLater()

    def _load_cached_catalog(self) -> None:
        raw = str(self._settings.value(self._catalog_cache, ""))
        if not raw:
            return
        try:
            entries = json.loads(raw)
            self._catalog = [
                ModelRecord(
                    name=str(entry["name"]),
                    download_url=str(entry["download_url"]),
                    uploaded_at=str(entry.get("uploaded_at", "")),
                    rating=str(entry.get("rating", "")),
                    tier=classify_model(str(entry["name"])),
                )
                for entry in entries
                if isinstance(entry, dict)
                and str(entry.get("download_url", "")).startswith(f"https://{MODEL_HOST}/")
            ]
        except (TypeError, ValueError, KeyError, json.JSONDecodeError):
            logger.warning("Ignoring invalid cached KataGo catalogue")
            self._catalog = []
        self._populate_catalog()

    def _populate_catalog(self, *_args) -> None:
        if not hasattr(self, "_models"):
            return
        query = self._search.text().casefold().strip()
        recommended = recommend_tier(self._profile)
        suggested_order = _TIER_ORDER[recommended]
        previous_name = self._selected.name if self._selected else ""
        self._models.clear()
        for model in self._catalog:
            if query and query not in model.name.casefold():
                continue
            filepath = self._download_dir / model.filename
            label = _TIER_NAME[model.tier]
            if filepath.is_file():
                fit = "已下載" + (" · 目前使用" if str(filepath) == str(self._settings.value("engine_model", "")) else "")
            elif _TIER_ORDER[model.tier] <= suggested_order:
                fit = "建議" if model.tier == recommended else f"可用 · {label}"
            else:
                fit = f"較吃資源 · {label}"
            item = QtWidgets.QTreeWidgetItem((model.name, model.rating, model.uploaded_at, fit))
            item.setData(0, MODEL_ROLE, model)
            self._models.addTopLevelItem(item)
            if model.name == previous_name:
                self._models.setCurrentItem(item)
        self._models.resizeColumnToContents(0)
        if self._models.currentItem() is None and self._models.topLevelItemCount():
            preferred = next(
                (self._models.topLevelItem(i) for i in range(self._models.topLevelItemCount())
                 if self._models.topLevelItem(i).data(0, MODEL_ROLE).tier == recommended),
                self._models.topLevelItem(0),
            )
            self._models.setCurrentItem(preferred)

    def _selection_changed(self, current, _previous) -> None:
        model = current.data(0, MODEL_ROLE) if current else None
        self._selected = model if isinstance(model, ModelRecord) else None
        if self._selected is None:
            return
        model_path = self._download_dir / self._selected.filename
        current_path = str(self._settings.value("engine_model", ""))
        classification = _TIER_NAME[self._selected.tier]
        tier_ok = _TIER_ORDER[self._selected.tier] <= _TIER_ORDER[recommend_tier(self._profile)]
        cpu_state = "RAM 充足" if self._profile.available_ram_gib >= _tier_min_ram(self._selected.tier) else "RAM 可能不足"
        gpu_state = ""
        if self._profile.gpu_name:
            gpu_state = "；" + ("VRAM 充足" if self._profile.gpu_available_gib >= _tier_min_vram(self._selected.tier) else "VRAM 可能不足")
        recommendation = "符合目前建議" if tier_ok else "高於目前建議，可能需要降低搜尋快取"
        installed = f"<br>本機檔案：{model_path}" if model_path.is_file() else ""
        active = "<br><b>目前 KataGo 使用的模型</b>" if str(model_path) == current_path else ""
        self._details.setText(
            f"<b>{self._selected.name}</b> · {classification} · {recommendation}<br>"
            f"{cpu_state}{gpu_state}<br>評分：{self._selected.rating or '尚無評分'} · 上傳：{self._selected.uploaded_at}"
            f"{installed}{active}"
        )
        self._download_button.setText("已下載 · 設為目前模型" if model_path.is_file() else "下載並設為目前模型")
        self._download_only_button.setText("重新下載" if model_path.is_file() else "只下載")

    def _choose_download_folder(self) -> None:
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "模型下載位置", str(self._download_dir))
        if folder:
            self._download_dir = Path(folder)
            self._settings.setValue("model-center/download-dir", folder)
            self._folder_label.setText(folder)
            self._populate_catalog()
            if self._models.currentItem():
                self._selection_changed(self._models.currentItem(), None)

    def _download_or_use_selected(self) -> None:
        if self._selected is None:
            self._status.setText("請先從清單選擇模型。")
            return
        existing = self._download_dir / self._selected.filename
        if existing.is_file():
            self._use_model(existing)
        else:
            self._begin_download(use_when_done=True)

    def _begin_download(self, use_when_done: bool) -> None:
        if self._selected is None:
            self._status.setText("請先從清單選擇模型。")
            return
        self._download_use_when_done = use_when_done
        self._download_dir.mkdir(parents=True, exist_ok=True)
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(self._selected.download_url))
        request.setHeader(QtNetwork.QNetworkRequest.KnownHeaders.UserAgentHeader, "NightyGo Model Center")
        request.setTransferTimeout(45_000)
        request.setAttribute(
            QtNetwork.QNetworkRequest.Attribute.RedirectPolicyAttribute,
            QtNetwork.QNetworkRequest.RedirectPolicy.NoLessSafeRedirectPolicy,
        )
        self._probe_reply = self._manager.head(request)
        self._probe_reply.finished.connect(self._probe_finished)
        self._set_busy(True)
        self._status.setText("正在確認下載大小與磁碟空間…")

    def _probe_finished(self) -> None:
        reply = self._probe_reply
        self._probe_reply = None
        if reply is None:
            return
        if reply.error() != QtNetwork.QNetworkReply.NetworkError.NoError:
            self._status.setText(f"無法取得檔案資訊：{reply.errorString()}")
            self._set_busy(False)
            reply.deleteLater()
            return
        raw_size = bytes(reply.rawHeader("Content-Length"))
        try:
            self._expected_bytes = int(raw_size)
        except ValueError:
            self._expected_bytes = 0
        storage = QtCore.QStorageInfo(str(self._download_dir))
        storage.refresh()
        if self._expected_bytes and storage.bytesAvailable() < int(self._expected_bytes * 1.05):
            self._status.setText("磁碟空間不足；請選擇空間更大的下載位置。")
            self._set_busy(False)
            reply.deleteLater()
            return
        target = self._download_dir / self._selected.filename
        self._save_file = QtCore.QSaveFile(str(target))
        if not self._save_file.open(QtCore.QIODevice.OpenModeFlag.WriteOnly):
            self._status.setText(f"無法建立模型檔案：{self._save_file.errorString()}")
            self._save_file = None
            self._set_busy(False)
            reply.deleteLater()
            return
        self._progress.setValue(0)
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(self._selected.download_url))
        request.setHeader(QtNetwork.QNetworkRequest.KnownHeaders.UserAgentHeader, "NightyGo Model Center")
        request.setTransferTimeout(60_000)
        request.setAttribute(
            QtNetwork.QNetworkRequest.Attribute.RedirectPolicyAttribute,
            QtNetwork.QNetworkRequest.RedirectPolicy.NoLessSafeRedirectPolicy,
        )
        self._download_reply = self._manager.get(request)
        self._download_bytes_written = 0
        self._download_reply.readyRead.connect(self._write_download_chunk)
        self._download_reply.downloadProgress.connect(self._download_progress)
        self._download_reply.finished.connect(self._download_finished)
        self._status.setText("開始從 KataGo 官方儲存站下載模型…")
        reply.deleteLater()

    def _write_download_chunk(self) -> None:
        if self._download_reply is None or self._save_file is None:
            return
        chunk = bytes(self._download_reply.readAll())
        if chunk:
            written = self._save_file.write(chunk)
            if written != len(chunk):
                self._status.setText(f"寫入失敗：{self._save_file.errorString()}")
                self._download_reply.abort()
            else:
                self._download_bytes_written += written

    def _download_progress(self, received: int, total: int) -> None:
        denominator = total or self._expected_bytes
        if denominator > 0:
            self._progress.setValue(min(100, int(received * 100 / denominator)))
            self._status.setText(f"已下載 {received / 1024**2:.1f} / {denominator / 1024**2:.1f} MiB")
        else:
            self._status.setText(f"已下載 {received / 1024**2:.1f} MiB")

    def _download_finished(self) -> None:
        reply = self._download_reply
        if reply is None:
            return
        if reply.isOpen() and reply.error() == QtNetwork.QNetworkReply.NetworkError.NoError:
            self._write_download_chunk()
        self._download_reply = None
        error = reply.error()
        error_text = reply.errorString()
        received = self._download_bytes_written
        reply.deleteLater()
        if error != QtNetwork.QNetworkReply.NetworkError.NoError:
            if self._save_file:
                self._save_file.cancelWriting()
            self._save_file = None
            self._set_busy(False)
            self._status.setText(f"下載未完成，暫存檔已清除：{error_text}")
            return
        if self._expected_bytes and received != self._expected_bytes:
            if self._save_file:
                self._save_file.cancelWriting()
            self._save_file = None
            self._set_busy(False)
            self._status.setText(f"下載大小不符（{received} / {self._expected_bytes} bytes），檔案未安裝。")
            return
        if self._save_file is None or not self._save_file.commit():
            reason = self._save_file.errorString() if self._save_file else "未知寫入錯誤"
            if self._save_file:
                self._save_file.cancelWriting()
            self._save_file = None
            self._set_busy(False)
            self._status.setText(f"模型檔無法完成保存：{reason}")
            return
        path = self._download_dir / self._selected.filename
        self._save_file = None
        self._set_busy(False)
        self._status.setText(f"模型下載完成：{path}")
        self._populate_catalog()
        if self._download_use_when_done:
            self._use_model(path)
        elif self._models.currentItem():
            self._selection_changed(self._models.currentItem(), None)

    def _cancel_download(self) -> None:
        if self._probe_reply is not None:
            self._probe_reply.abort()
        if self._download_reply is not None:
            self._status.setText("正在取消並清除未完成的模型檔…")
            self._download_reply.abort()
        elif self._probe_reply is None:
            self._set_busy(False)

    def _set_busy(self, busy: bool) -> None:
        self._download_button.setEnabled(not busy)
        self._download_only_button.setEnabled(not busy)
        self._cancel_button.setEnabled(busy)

    def _use_model(self, path: Path) -> None:
        self._settings.setValue("engine_model", str(path))
        self._settings.sync()
        self._populate_catalog()
        if self._models.currentItem():
            self._selection_changed(self._models.currentItem(), None)
        self._status.setText(
            f"已設為目前模型。若尚未設定 KataGo 執行檔，請在 Preferences 選取它。"
        )
        self.modelSelected.emit(str(path))

    def closeEvent(self, event) -> None:
        if self._catalog_reply is not None:
            self._catalog_reply.abort()
        if self._probe_reply is not None:
            self._probe_reply.abort()
        if self._download_reply is not None:
            self._download_reply.abort()
        if self._save_file is not None:
            self._save_file.cancelWriting()
        super().closeEvent(event)


def _tier_min_ram(tier: str) -> float:
    return {"light": 3.0, "balanced": 5.0, "strong": 8.0, "maximum": 12.0}[tier]


def _tier_min_vram(tier: str) -> float:
    return {"light": 1.5, "balanced": 3.0, "strong": 5.0, "maximum": 8.0}[tier]
