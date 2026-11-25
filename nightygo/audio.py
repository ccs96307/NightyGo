"""Low-latency user interface sounds."""

import logging
from pathlib import Path
from typing import ClassVar

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect

logger = logging.getLogger(__name__)


class StonePlacementSound:
    """Preloads several placement sounds and plays the selected effect."""

    SOUND_FILES: ClassVar[dict[str, str]] = {
        "Go stone · wooden board 1": "go_stone_01.wav",
        "Go stone · wooden board 2": "go_stone_02.wav",
        "Go stone · wooden board 3": "go_stone_03.wav",
        "Go stone · thin board 1": "go_stone_04.wav",
        "Go stone · thin board 2": "go_stone_05.wav",
    }

    def __init__(self, parent=None):
        self._effects = {}
        self._pending_play = set()
        self._selected_sound = next(iter(self.SOUND_FILES))
        assets = Path(__file__).parent / "assets"
        for name, filename in self.SOUND_FILES.items():
            effect = QSoundEffect(parent)
            self._effects[name] = effect
            effect.setVolume(0.45)
            effect.statusChanged.connect(
                lambda sound_name=name: self._on_status_changed(sound_name)
            )
            source_path = assets / filename
            effect.setSource(QUrl.fromLocalFile(str(source_path)))

    @classmethod
    def available_sounds(cls):
        """Return sound names suitable for a settings selector."""
        return tuple(cls.SOUND_FILES)

    def set_sound(self, name):
        """Select the sound to play on the next stone placement."""
        if name in self._effects:
            self._selected_sound = name
        else:
            logger.warning("Unknown placement sound %r; keeping %r", name, self._selected_sound)

    @property
    def selected_sound(self):
        return self._selected_sound

    def play(self, name=None):
        """Play the selected sound, queueing one play while it loads."""
        sound_name = name or self._selected_sound
        effect = self._effects.get(sound_name)
        if effect is None:
            logger.warning("Ignoring request for unknown placement sound %r", sound_name)
            return
        status = effect.status()
        if status == QSoundEffect.Status.Ready:
            effect.play()
        elif status == QSoundEffect.Status.Loading:
            self._pending_play.add(sound_name)

    def _on_status_changed(self, name):
        effect = self._effects.get(name)
        if effect is None:
            logger.error("Received a sound status update for unknown sound %r", name)
            return
        status = effect.status()
        if status == QSoundEffect.Status.Ready and name in self._pending_play:
            self._pending_play.discard(name)
            effect.play()
        elif status == QSoundEffect.Status.Error:
            self._pending_play.discard(name)
            logger.error("Could not load placement sound %r from %s", name, effect.source().toString())


class StoneCaptureSound:
    """Play a short Go-stone pickup pattern sized to the captured group."""

    SOUND_FILES: ClassVar[dict[str, str]] = {
        "single": "capture_single.wav",
        "small_group": "capture_small_group.wav",
        "group": "capture_group.wav",
        "large_group": "capture_large_group.wav",
    }

    def __init__(self, parent=None):
        self._effects = {}
        self._pending_play: set[str] = set()
        assets = Path(__file__).parent / "assets"
        for band, filename in self.SOUND_FILES.items():
            effect = QSoundEffect(parent)
            self._effects[band] = effect
            effect.setVolume(0.52)
            effect.statusChanged.connect(lambda name=band: self._on_status_changed(name))
            effect.setSource(QUrl.fromLocalFile(str(assets / filename)))

    @staticmethod
    def band_for_count(count: int) -> str | None:
        """Map a captured group size to one of four audible patterns."""
        if count <= 0:
            return None
        if count == 1:
            return "single"
        if count <= 3:
            return "small_group"
        if count <= 7:
            return "group"
        return "large_group"

    @classmethod
    def available_sounds(cls) -> tuple[str, ...]:
        return tuple(cls.SOUND_FILES)

    def play(self, captured_count: int) -> None:
        band = self.band_for_count(captured_count)
        effect = self._effects.get(band)
        if effect is None:
            return
        if effect.status() == QSoundEffect.Status.Ready:
            effect.play()
        elif effect.status() == QSoundEffect.Status.Loading:
            self._pending_play.add(band)

    def _on_status_changed(self, band: str) -> None:
        effect = self._effects.get(band)
        if effect is None:
            return
        if effect.status() == QSoundEffect.Status.Ready and band in self._pending_play:
            self._pending_play.discard(band)
            effect.play()
        elif effect.status() == QSoundEffect.Status.Error:
            self._pending_play.discard(band)
            logger.error("Could not load capture sound %s from %s", band, effect.source().toString())
