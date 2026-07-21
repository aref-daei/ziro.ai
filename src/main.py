#!/usr/bin/env python3

"""
Ziro.ai - Desktop AI Media Processing Platform
Version 2.0.0
Copyright (C) 2025-2026  Aref Daei

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: aref.daei@outlook.com
"""

import sys

from PySide6.QtWidgets import QApplication

from core.constants import PROJECT_NAME
from gui import SplashScreen

LOADING_STEPS = [
    ("Loading Torch module...", lambda: __import__("torch")),
    ("Loading Whisper module...", lambda: __import__("whisper")),
    ("Loading FFmpeg module...", lambda: __import__("ffmpeg")),
    ("Loading GoogleTrans module...", lambda: __import__("googletrans")),
    ("Loading DeepL module...", lambda: __import__("deepl")),
    ("Preparing UI...", lambda: None),
]


def main():
    app = QApplication(sys.argv)
    screen_geometry = app.primaryScreen().geometry()

    splash = SplashScreen(PROJECT_NAME, len(LOADING_STEPS))
    splash.center_on_screen(screen_geometry)
    splash.show()
    app.processEvents()

    for i, (message, loader) in enumerate(LOADING_STEPS, start=1):
        splash.set_progress(i, message)
        app.processEvents()
        loader()

    from gui import MainWindow

    window = MainWindow()
    window.center_on_screen(screen_geometry)
    window.show()
    splash.close()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
