#!/usr/bin/env python3

"""
Ziro.ai - Automated Subtitle Generation Application
Version: 1.0.0
"""

import sys
from pathlib import Path

from settings import PROJECT_NAME

# Add project path to PYTHON_PATH
sys.path.insert(0, str(Path(__file__).parent))

from ui.main_window import MainWindow
from utils.logger import Logger
from utils.validators import Validators


def check_requirements():
    """Check requirements"""
    logger = Logger()

    # Check ffmpeg
    if not Validators.check_ffmpeg_installed():
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
        app = MainWindow()
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
