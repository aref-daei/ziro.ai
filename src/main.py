#!/usr/bin/env python3

"""
Ziro.ai - Automated Subtitle Generation Application
Version 1.1.0-RC
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

import shutil
import sys
from pathlib import Path

from core.config import PROJECT_NAME

# Add project path to PYTHON_PATH
sys.path.insert(0, str(Path(__file__).parent))

from adapters.ui.app import App
from utils.logger import Logger


def check_requirements():
    """Check requirements"""
    logger = Logger()

    # Check ffmpeg
    if shutil.which("ffmpeg") is None:
        logger.error("ffmpeg is not installed!")
        print("\n" + "=" * 60)
        print("Error: ffmpeg not found!")
        print("Please install ffmpeg:")
        print("  Windows: https://ffmpeg.org/download.html")
        print("  Linux: sudo apt install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("=" * 60 + "\n")
        return False

    logger.info("ffmpeg found ✓")

    # Check Python modules
    required_modules = [
        'whisper',
        'transformers',
        'customtkinter',
        'torch',
        'ffmpeg'
    ]

    missing = []
    for module in required_modules:
        try:
            __import__(module)
            logger.info(f"Module {module} found ✓")
        except ImportError:
            missing.append(module)
            logger.error(f"Module {module} not found!")

    if missing:
        print("\n" + "=" * 60)
        print("Error: Some Python modules were not found:")
        print("Please install with the following command:")
        print(f"  pip install {' '.join(missing)}")
        print("=" * 60 + "\n")
        return False

    return True


def main():
    """Main function"""
    logger = Logger()
    logger.info(f"Starting {PROJECT_NAME} application")

    # Check requirements
    if not check_requirements():
        logger.error("Requirements not met")
        input("\nPress Enter to exit ...")
        sys.exit(1)

    try:
        # Run application
        app = App()
        logger.info("User interface loaded")
        app.mainloop()

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\nGeneral error: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)

    finally:
        logger.info("Application closed")


if __name__ == "__main__":
    main()
