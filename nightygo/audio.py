"""Low-latency user interface sounds."""

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect


class StonePlacementSound:
    """Preloads several placement sounds and plays the selected effect."""

    SOUND_FILES = {
        "NightyGo original": "stone_placed.wav",
        "Piece Place · wood": "piece_place.wav",
        "Soft Click": "soft_click.wav",
        "Menu Select": "menu_select.wav",
        "Mouse Click": "mouse_click.wav",
    }

    def __init__(self, parent=None):
        self._effects = {}
        self._pending_play = set()
        self._selected_sound = "NightyGo original"
        assets = Path(__file__).parent / "assets"
        for name, filename in self.SOUND_FILES.items():
            effect = QSoundEffect(parent)
            effect.setVolume(0.45)
            effect.statusChanged.connect(
                lambda sound_name=name: self._on_status_changed(sound_name)
            )
            effect.setSource(QUrl.fromLocalFile(str(assets / filename)))
            self._effects[name] = effect

    @classmethod
    def available_sounds(cls):
        """Return sound names suitable for a settings selector."""
        return tuple(cls.SOUND_FILES)

    def set_sound(self, name):
        """Select the sound to play on the next stone placement."""
        if name in self._effects:
            self._selected_sound = name

    @property
    def selected_sound(self):
        return self._selected_sound

    def play(self):
        """Play the selected sound, queueing one play while it loads."""
        effect = self._effects[self._selected_sound]
        status = effect.status()
        if status == QSoundEffect.Status.Ready:
            effect.play()
        elif status == QSoundEffect.Status.Loading:
            self._pending_play.add(self._selected_sound)

    def _on_status_changed(self, name):
        effect = self._effects[name]
        status = effect.status()
        if status == QSoundEffect.Status.Ready and name in self._pending_play:
            self._pending_play.discard(name)
            effect.play()
        elif status == QSoundEffect.Status.Error:
            self._pending_play.discard(name)
