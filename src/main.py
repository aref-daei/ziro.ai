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

import core.no_console_patch

import sys

from PySide6.QtCore import QLoggingCategory
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from core.constants import PROJECT_NAME
from gui.splash_screen import SplashScreen
from logger import Logger

import assets.assets_rc

LOADING_STEPS = [
    ("Loading Torch module...", lambda: __import__("torch")),
    ("Loading Whisper module...", lambda: __import__("whisper")),
    ("Loading FFmpeg module...", lambda: __import__("ffmpeg")),
    ("Loading GoogleTrans module...", lambda: __import__("googletrans")),
    ("Loading DeepL module...", lambda: __import__("deepl")),
    ("Preparing UI...", lambda: None),
]

QLoggingCategory.setFilterRules("""
qt.multimedia.*=false
qt.multimedia.ffmpeg=false
""")


def main():
    logger = Logger()

    logger.info("Starting application...")
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icons/Ziro.png"))
    screen_geometry = app.primaryScreen().geometry()

    logger.info("Showing splash screen...")
    splash = SplashScreen(PROJECT_NAME, len(LOADING_STEPS))
    splash.center_on_screen(screen_geometry)
    splash.show()
    app.processEvents()

    logger.info("Loading application modules...")
    for i, (message, loader) in enumerate(LOADING_STEPS, start=1):
        splash.set_progress(i, message)
        app.processEvents()
        loader()

    logger.info("Loading main window...")
    from gui.main_window import MainWindow

    logger.info("Creating main window...")
    window = MainWindow()
    window.center_on_screen(screen_geometry)
    window.show()
    splash.close()

    logger.info("Application started.")

    exit_code = app.exec()

    logger.info("Application exited.")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
