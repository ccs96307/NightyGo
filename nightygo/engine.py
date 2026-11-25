"""Asynchronous GTP engine process and KataGo analysis parsing."""

from __future__ import annotations

import logging
import re
from collections import deque
from dataclasses import dataclass

from PySide6 import QtCore


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EngineConfig:
    """Executable and launch options for a GTP-compatible engine."""

    program: str
    arguments: tuple[str, ...] = ()
    working_directory: str = ""


@dataclass(frozen=True)
class AnalysisMove:
    """One KataGo candidate move and its current analysis values."""

    vertex: str
    visits: int = 0
    winrate: float | None = None
    score_lead: float | None = None
    principal_variation: tuple[str, ...] = ()
    order: int | None = None


@dataclass(frozen=True)
class AnalysisRoot:
    """Current-position aggregate metrics reported by KataGo."""

    visits: int = 0
    winrate: float | None = None
    score_lead: float | None = None


@dataclass(frozen=True)
class _Command:
    command_id: int
    text: str
    tag: str = ""


_INFO_MOVE = re.compile(
    r"(?:^|\s)info\s+move\s+(\S+)(.*?)(?=\s+info\s+(?:move|rootInfo|ownership|ownershipStdev|movesOwnership|movesOwnershipStdev)\b|$)"
)
_ROOT_INFO = re.compile(
    r"(?:^|\s)info\s+rootInfo(.*?)(?=\s+ownership(?:Stdev)?\b|$)"
)
_OWNERSHIP = re.compile(
    r"(?:^|\s)ownership\s+((?:[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?\s*)+)(?=\s+info\s|\s+ownershipStdev\b|$)"
)


def parse_katago_info(line: str) -> AnalysisMove | None:
    """Parse one candidate from KataGo's whitespace-delimited info output."""
    matches = parse_katago_info_lines(line)
    return matches[0] if matches else None


def parse_katago_info_lines(line: str) -> tuple[AnalysisMove, ...]:
    """Parse all candidates from a KataGo output line."""
    analyses = []
    for match in _INFO_MOVE.finditer(line.strip()):
        analysis = _parse_info_move(*match.groups())
        if analysis is not None:
            analyses.append(analysis)
    return tuple(analyses)


def _parse_info_move(vertex: str, payload: str) -> AnalysisMove | None:
    if not vertex:
        return None
    parts = payload.strip().split()
    values: dict[str, str] = {}
    index = 0
    while index < len(parts):
        key = parts[index]
        index += 1
        if key == "pv":
            values[key] = " ".join(parts[index:])
            break
        if index < len(parts):
            values[key] = parts[index]
            index += 1
    try:
        visits = int(values.get("visits", "0"))
        winrate = float(values["winrate"]) if "winrate" in values else None
        score_lead = float(values["scoreLead"]) if "scoreLead" in values else None
        order = int(values["order"]) if "order" in values else None
    except ValueError:
        return None
    if winrate is not None and winrate > 1.0 and winrate <= 10000:
        winrate /= 10000.0
    return AnalysisMove(
        vertex=vertex,
        visits=visits,
        winrate=winrate,
        score_lead=score_lead,
        principal_variation=tuple(values.get("pv", "").split()),
        order=order,
    )


def parse_katago_root_info(line: str) -> AnalysisRoot | None:
    """Parse aggregate root metrics from a KataGo analysis line."""
    match = _ROOT_INFO.search(line.strip())
    if match is None:
        return None
    parts = match.group(1).split()
    values: dict[str, str] = {}
    for index in range(0, len(parts) - 1, 2):
        values[parts[index]] = parts[index + 1]
    try:
        visits = int(values.get("visits", "0"))
        winrate = float(values["winrate"]) if "winrate" in values else None
        score_value = values.get("scoreLead") or values.get("scoreMean")
        score = float(score_value) if score_value is not None else None
    except ValueError:
        return None
    if winrate is not None and winrate > 1.0 and winrate <= 10000:
        winrate /= 10000.0
    return AnalysisRoot(visits, winrate, score)


def parse_katago_ownership(line: str) -> tuple[float, ...] | None:
    """Parse the optional row-major ownership values from KataGo."""
    match = _OWNERSHIP.search(line.strip())
    if match is None:
        return None
    try:
        return tuple(float(value) for value in match.group(1).split())
    except ValueError:
        return None


class GtpEngine(QtCore.QObject):
    """Manage a GTP engine asynchronously without blocking the UI thread."""

    statusChanged = QtCore.Signal(str)
    ready = QtCore.Signal(str, str)
    responseReceived = QtCore.Signal(int, str, str)
    analysisUpdated = QtCore.Signal(object)
    rootInfoUpdated = QtCore.Signal(object)
    ownershipUpdated = QtCore.Signal(object)
    errorOccurred = QtCore.Signal(str)
    outputReceived = QtCore.Signal(str)

    STOPPED = "Stopped"
    STARTING = "Starting"
    READY = "Ready"
    ANALYZING = "Analyzing"
    ERROR = "Error"

    _RESPONSE = re.compile(r"^([=?])\s*(\d+)?\s*(.*)$")

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._process = QtCore.QProcess(self)
        self._process.setProcessChannelMode(QtCore.QProcess.ProcessChannelMode.SeparateChannels)
        self._process.started.connect(self._on_started)
        self._process.readyReadStandardOutput.connect(self._read_stdout)
        self._process.readyReadStandardError.connect(self._read_stderr)
        self._process.errorOccurred.connect(self._on_process_error)
        self._process.finished.connect(self._on_finished)
        self._status = self.STOPPED
        self._next_id = 1
        self._queue: deque[_Command] = deque()
        self._inflight: dict[int, _Command] = {}
        self._active_id: int | None = None
        self._response_lines: list[str] = []
        self._stdout_buffer = ""
        self._stderr_buffer = ""
        self._name = ""
        self._version = ""
        self._pending_config: EngineConfig | None = None
        self._stopping = False

    @property
    def status(self) -> str:
        return self._status

    @property
    def is_running(self) -> bool:
        return self._process.state() != QtCore.QProcess.ProcessState.NotRunning

    def start(self, config: EngineConfig) -> None:
        """Start an engine process and perform the GTP handshake."""
        if self.is_running:
            self._pending_config = config
            self.stop()
            return
        self._launch(config)

    def _launch(self, config: EngineConfig) -> None:
        if not config.program.strip():
            self._fail("Select a GTP engine executable first")
            return
        self._pending_config = None
        self._stopping = False
        self._queue.clear()
        self._inflight.clear()
        self._active_id = None
        self._response_lines.clear()
        self._stdout_buffer = ""
        self._stderr_buffer = ""
        self._name = ""
        self._version = ""
        self._set_status(self.STARTING)
        self._process.setProgram(config.program)
        self._process.setArguments(list(config.arguments))
        if config.working_directory:
            self._process.setWorkingDirectory(config.working_directory)
        self._process.start()

    def stop(self) -> None:
        """Ask the process to quit, then terminate it if it does not exit."""
        if not self.is_running:
            self._set_status(self.STOPPED)
            return
        self._stopping = True
        self._process.write(b"quit\n")
        QtCore.QTimer.singleShot(900, self._terminate_if_running)

    def send_command(self, command: str) -> int | None:
        """Queue one GTP command and return its protocol ID."""
        if self._status not in (self.READY, self.ANALYZING):
            self.errorOccurred.emit("The GTP engine is not ready")
            return None
        if not command.strip() or "\n" in command or "\r" in command:
            self.errorOccurred.emit("Invalid GTP command")
            return None
        return self._enqueue(command.strip())

    def set_position(self, board_size: int, komi: float) -> None:
        """Clear the engine board and apply board size and komi."""
        if not 2 <= board_size <= 25:
            self.errorOccurred.emit(f"Unsupported board size: {board_size}")
            return
        for command in (f"boardsize {board_size}", "clear_board", f"komi {komi:g}"):
            self.send_command(command)

    def set_stones(self, black: tuple[str, ...], white: tuple[str, ...]) -> int | None:
        """Set an arbitrary current board position using KataGo's GTP extension."""
        arguments = [f"B {vertex}" for vertex in black]
        arguments.extend(f"W {vertex}" for vertex in white)
        return self.send_command("set_position" + (" " + " ".join(arguments) if arguments else ""))

    def play_move(self, color: str, vertex: str) -> int | None:
        """Send a move to the engine."""
        normalized = color.lower()
        if normalized not in ("b", "w"):
            self.errorOccurred.emit(f"Invalid GTP color: {color}")
            return None
        return self.send_command(f"play {normalized} {vertex}")

    def request_genmove(self, color: str) -> int | None:
        """Ask the engine to generate a move for black or white."""
        normalized = color.lower()
        if normalized not in ("b", "w"):
            self.errorOccurred.emit(f"Invalid GTP color: {color}")
            return None
        return self.send_command(f"genmove {normalized}")

    def start_analysis(self, color: str = "B", interval_ms: int = 500) -> int | None:
        """Start KataGo's streaming analysis command."""
        if self._status != self.READY:
            self.errorOccurred.emit("The GTP engine is not ready for analysis")
            return None
        normalized = color.upper()
        if normalized not in ("B", "W"):
            self.errorOccurred.emit(f"Invalid analysis color: {color}")
            return None
        self._set_status(self.ANALYZING)
        return self._enqueue(
            f"kata-analyze {normalized} {max(5, interval_ms // 10)} rootInfo true ownership true",
            tag="analysis",
        )

    def stop_analysis(self) -> None:
        """Interrupt a KataGo analysis without waiting for it to finish first."""
        if self._status != self.ANALYZING or not self.is_running:
            return
        command = self._new_command("stop", "stop_analysis")
        self._inflight[command.command_id] = command
        self._process.write(f"{command.command_id} stop\n".encode("ascii"))

    def _on_started(self) -> None:
        logger.info("GTP process started: %s", self._process.program())
        self._enqueue("protocol_version", tag="handshake_protocol")

    def _enqueue(self, text: str, tag: str = "") -> int:
        command = self._new_command(text, tag)
        self._queue.append(command)
        self._send_next()
        return command.command_id

    def _new_command(self, text: str, tag: str) -> _Command:
        command = _Command(self._next_id, text, tag)
        self._next_id += 1
        return command

    def _send_next(self) -> None:
        if self._active_id is not None or not self._queue or not self.is_running:
            return
        command = self._queue.popleft()
        self._active_id = command.command_id
        self._inflight[command.command_id] = command
        payload = f"{command.command_id} {command.text}\n".encode("utf-8")
        logger.debug("GTP -> %s", command.text)
        self._process.write(payload)

    def _read_stdout(self) -> None:
        self._stdout_buffer += bytes(self._process.readAllStandardOutput()).decode(
            "utf-8", errors="replace"
        )
        while "\n" in self._stdout_buffer:
            line, self._stdout_buffer = self._stdout_buffer.split("\n", 1)
            line = line.rstrip("\r")
            if line.startswith("info "):
                analyses = parse_katago_info_lines(line)
                for analysis in analyses:
                    self.analysisUpdated.emit(analysis)
                root = parse_katago_root_info(line)
                if root is not None:
                    self.rootInfoUpdated.emit(root)
                ownership = parse_katago_ownership(line)
                if ownership is not None:
                    self.ownershipUpdated.emit(ownership)
                if not analyses and root is None and ownership is None:
                    self.outputReceived.emit(line)
                continue
            if line.startswith(("=", "?")):
                self._response_lines = [line]
            elif not line and self._response_lines:
                self._finish_response()
            elif self._response_lines:
                self._response_lines.append(line)
            elif line.strip():
                self.outputReceived.emit(line)

    def _finish_response(self) -> None:
        match = self._RESPONSE.match(self._response_lines[0])
        lines = self._response_lines
        self._response_lines = []
        if match is None:
            self.outputReceived.emit("\n".join(lines))
            return
        success, raw_id, first_line = match.groups()
        command_id = int(raw_id) if raw_id else self._active_id
        if command_id is None:
            self.outputReceived.emit("\n".join(lines))
            return
        command = self._inflight.pop(command_id, None)
        if command_id == self._active_id:
            self._active_id = None
        response_body = "\n".join(([first_line] if first_line else []) + lines[1:]).strip()
        logger.debug("GTP <- id=%d success=%s %s", command_id, success == "=", response_body)
        self.responseReceived.emit(command_id, command.text if command else "", response_body)
        self._handle_command_response(command, success == "=", response_body)
        self._send_next()

    def _handle_command_response(
        self, command: _Command | None, success: bool, response: str
    ) -> None:
        if command is None:
            return
        if not success:
            message = response or f"Engine rejected command: {command.text}"
            logger.warning("GTP command failed: %s: %s", command.text, message)
            self.errorOccurred.emit(message)
            if command.tag.startswith("handshake"):
                self._fail(f"GTP handshake failed: {message}")
            return
        if command.tag == "handshake_protocol":
            self._enqueue("name", tag="handshake_name")
        elif command.tag == "handshake_name":
            self._name = response
            self._enqueue("version", tag="handshake_version")
        elif command.tag == "handshake_version":
            self._version = response
            self._set_status(self.READY)
            self.ready.emit(self._name, self._version)
            logger.info("GTP engine ready: %s %s", self._name, self._version)
        elif command.tag == "analysis":
            self._set_status(self.READY)
        elif command.tag == "stop_analysis":
            self._set_status(self.READY)

    def _read_stderr(self) -> None:
        self._stderr_buffer += bytes(self._process.readAllStandardError()).decode(
            "utf-8", errors="replace"
        )
        lines = self._stderr_buffer.splitlines(keepends=True)
        self._stderr_buffer = ""
        if lines and not lines[-1].endswith(("\n", "\r")):
            self._stderr_buffer = lines.pop()
        for line in lines:
            line = line.rstrip("\r\n")
            if line:
                logger.info("GTP stderr: %s", line)
                self.outputReceived.emit(line)

    def _on_process_error(self, error: QtCore.QProcess.ProcessError) -> None:
        if error == QtCore.QProcess.ProcessError.FailedToStart:
            self._fail(self._process.errorString())
        else:
            logger.warning("GTP process error (%s): %s", error, self._process.errorString())

    def _on_finished(self, exit_code: int, _exit_status: QtCore.QProcess.ExitStatus) -> None:
        logger.info("GTP process exited with status %d", exit_code)
        failed_early = not self._stopping and exit_code != 0 and self._status in (
            self.STARTING, self.READY, self.ANALYZING
        )
        diagnostic = self._stderr_buffer.strip()
        if failed_early:
            message = f"KataGo exited with code {exit_code}"
            if diagnostic:
                message += f": {diagnostic}"
            logger.error("%s", message)
            self.errorOccurred.emit(message)
        self._queue.clear()
        self._inflight.clear()
        self._active_id = None
        self._stopping = False
        self._set_status(self.ERROR if failed_early else self.STOPPED)
        if self._pending_config is not None:
            config = self._pending_config
            QtCore.QTimer.singleShot(0, lambda: self._launch(config))

    def _terminate_if_running(self) -> None:
        if self.is_running:
            self._process.terminate()
            QtCore.QTimer.singleShot(900, self._kill_if_running)

    def _kill_if_running(self) -> None:
        if self.is_running:
            self._process.kill()

    def _fail(self, message: str) -> None:
        logger.error("GTP engine error: %s", message)
        self._set_status(self.ERROR)
        self.errorOccurred.emit(message)

    def _set_status(self, status: str) -> None:
        if self._status != status:
            self._status = status
            self.statusChanged.emit(status)
