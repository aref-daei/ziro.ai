#!/usr/bin/env python3

"""
Ziro.ai - Automated Subtitle Generation Application
Version 1.2.0
Copyright (C) 2025  Aref Daei

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

import sys, shutil, time
from pathlib import Path
from tkinter import messagebox

from adapters.ui.splash import Splash
from utils.logger import Logger

# Add project path to PYTHON_PATH
sys.path.insert(0, str(Path(__file__).parent))


def main():
    logger = Logger()

    splash = Splash()

    # Check FFmpeg
    if shutil.which("ffmpeg") is None:
        logger.error("FFmpeg not found!")
        messagebox.showerror(
            "Error FFmpeg",
            "FFmpeg is not installed!\n\nPlease install FFmpeg and then run the program again.",
        )
        sys.exit(1)
    time.sleep(1)

    try:
        # Loading modules
        modules = [
            "torch",
            "torchvision",
            "whisper",
            "transformers",
            "customtkinter",
            "sentencepiece",
            "huggingface_hub",
            "hf_xet",
            "googletrans",
            "deepl",
            "ffmpeg",
        ]

        splash.loading_modules(modules)

        logger.info(f"Starting application")
        splash.status_label.configure(text=f"Starting application")
        splash.update()

        from adapters.ui.app import App

        splash.destroy()

        app = App()
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
