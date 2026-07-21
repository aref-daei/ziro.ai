#!/usr/bin/env python3

"""
Ziro.ai - Automated Subtitle Generation Application
Version 1.4.2
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

import shutil
import sys
import time
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from gui_old import Splash
from core.constants import PROJECT_NAME
from logger import Logger

# Add project path to PYTHON_PATH
sys.path.insert(0, str(Path(__file__).parent))


def main():
    logger = Logger()

    root = ctk.CTk()
    root.withdraw()

    splash = Splash(root)

    # Check FFmpeg
    if shutil.which("ffmpeg") is None:
        logger.error("FFmpeg not found!")
        messagebox.showerror(
            "FFmpeg not found",
            f"{PROJECT_NAME} requires FFmpeg to process audio files.\nPlease install FFmpeg and restart the application.",
        )
        sys.exit(1)
    time.sleep(1)

    try:
        # Loading modules
        modules = [
            "torch",
            "whisper",
            "googletrans",
            "deepl",
            "ffmpeg",
        ]

        splash.loading_modules(modules)

        logger.info(f"Starting application")
        splash.status_label.configure(text=f"Starting application")
        splash.update()

        from gui_old import App

        splash.withdraw()

        app = App()
        app.protocol(
            "WM_DELETE_WINDOW",
            lambda: (splash.destroy(), app.destroy(), root.destroy()),
        )
        logger.info("User interface loaded")
        app.mainloop()

    except ImportError as e:
        try:
            splash.destroy()
        except Exception:
            pass
        logger.error(f"Error loading: {e}")
        messagebox.showerror(
            "Error loading",
            str(e),
        )
        sys.exit(1)

    except Exception as e:
        try:
            splash.destroy()
        except Exception:
            pass
        logger.error(f"General error: {e}")
        messagebox.showerror(
            "Error",
            f"General error: {e}",
        )
        sys.exit(1)

    finally:
        logger.info("Application closed")


if __name__ == "__main__":
    main()
