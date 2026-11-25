"""Low-latency user interface sounds."""

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect


class StonePlacementSound:
    """Preloads and plays the bundled stone-placement sound."""

    def __init__(self, parent=None):
        self._effect = QSoundEffect(parent)
        self._pending_play = False
        self._effect.setVolume(0.35)
        self._effect.statusChanged.connect(self._on_status_changed)
        sound_path = Path(__file__).parent / "assets" / "stone_placed.wav"
        self._effect.setSource(QUrl.fromLocalFile(str(sound_path)))

    def play(self):
        """Play the stone sound, queueing one play while it loads."""
        status = self._effect.status()
        if status == QSoundEffect.Status.Ready:
            self._effect.play()
        elif status == QSoundEffect.Status.Loading:
            self._pending_play = True

    def _on_status_changed(self):
        status = self._effect.status()
        if status == QSoundEffect.Status.Ready and self._pending_play:
            self._pending_play = False
            self._effect.play()
        elif status == QSoundEffect.Status.Error:
            self._pending_play = False
