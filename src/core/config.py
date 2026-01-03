from pathlib import Path

# Project info
PROJECT_NAME = "Ziro.ai"
PROJECT_DESCRIPTION = "Automated Subtitle Generation Application"
PROJECT_VERSION = "1.1.0"
PROJECT_LICENSE = "Copyright (C) 2025  Aref Daei - AGPL-3.0"
PROJECT_AUTHOR = "Aref Daei"
PROJECT_AUTHOR_EMAIL = "aref.daei@outlook.com"
PROJECT_URL = "https://github.com/aref-daei/ziro.ai"
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / ".temp"
LOGS_DIR = BASE_DIR / "logs"

# If DEBUG is False, disable logging completely
DEBUG = True

# Translate settings
TRANSLATION_MODEL = "facebook/m2m100_418M"
MAX_TRANSLATION_LENGTH = 512
BATCH_SIZE = 8

# FFmpeg settings
AUDIO_FORMAT = "wav"
AUDIO_CODEC = "pcm_s16le"
AUDIO_RATE = 16000

# Subtitle settings
SRT_ENCODING = "utf-8"
MAX_SUBTITLE_LENGTH = 42  # Maximum character in a line

# Create directories
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
