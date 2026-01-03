#!/usr/bin/env python3

"""
Ziro.ai - Automated Subtitle Generation Application
Version 1.1.0
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

import customtkinter as ctk

from core.config import PROJECT_NAME
from utils.logger import Logger

# Add project path to PYTHON_PATH
sys.path.insert(0, str(Path(__file__).parent))


def show_startup_splash():
    splash = ctk.CTk()
    splash.overrideredirect(True)

    # Window settings
    width, height = 300, 120
    scaling = ctk.ScalingTracker.get_window_scaling(splash)
    x = (splash.winfo_screenwidth() - width) * scaling / 2
    y = (splash.winfo_screenheight() - height) * scaling / 2
    splash.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

    # Theme
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("green")

    splash.update_idletasks()

    ctk.CTkLabel(
        splash, text=f"{PROJECT_NAME}", font=ctk.CTkFont(size=24, weight="bold")
    ).pack(pady=20)

    status_label = ctk.CTkLabel(
        splash, text="Start loading...", wraplength=250, font=ctk.CTkFont(size=12)
    )
    status_label.pack(pady=2)

    progress = ctk.CTkProgressBar(splash, width=250)
    progress.pack(pady=2)
    progress.set(0)

    splash.update()
    return splash, status_label, progress


def main():
    logger = Logger()

    splash, status_label, progress = show_startup_splash()

    # Check FFmpeg
    if shutil.which("ffmpeg") is None:
        logger.error("FFmpeg not found!")
        messagebox.showerror(
            "Error",
            "FFmpeg is not installed!\n\nPlease install FFmpeg and then run the program again.",
        )
        sys.exit(1)
    logger.info("FFmpeg found ✓")
    time.sleep(1)

    try:
        # Check Python modules
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

        for i, module in enumerate(modules):
            try:
                status_label.configure(text=f"Module {module} is loading...")
                splash.update()
                __import__(module)
                logger.info(f"Module {module} found ✓")
                progress.set((i + 1) / len(modules))
                splash.update()
            except ImportError:
                logger.error(f"Module {module} not found!")
                messagebox.showerror(
                    "Error",
                    f"Error loading module {module}",
                )
                sys.exit(1)

        logger.info(f"Starting {PROJECT_NAME} application")
        status_label.configure(text=f"Starting {PROJECT_NAME} application")
        splash.update()

        from adapters.ui.app import App

        splash.destroy()

        app = App()
        logger.info("User interface loaded")
        app.mainloop()

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


if __name__ == "__main__":
    main()
