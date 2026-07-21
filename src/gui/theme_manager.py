from PySide6.QtWidgets import QWidget

from src.core.paths import PATHS


class ThemeManager:
    def __init__(self, window: QWidget):
        self._window = window
        self._theme = "dark"

    def set_theme(self, theme: str):
        self._theme = theme
        with open(
                PATHS["styles"] / f"{theme}.qss",
                encoding="utf-8"
        ) as f:
            self._window.setStyleSheet(f.read())

    def set_custom_stylesheet(self, stylesheet: str):
        self._window.setStyleSheet(stylesheet)

    def toggle_theme(self):
        self.set_theme(
            "light" if self._theme == "dark" else "dark"
        )

    def current_theme(self):
        return self._theme
