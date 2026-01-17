# Project info
PROJECT_NAME = "Ziro.ai"
PROJECT_DESCRIPTION = "Automated Subtitle Generation Application"
PROJECT_VERSION = "1.4.0"
PROJECT_LICENSE = "Copyright (C) 2025  Aref Daei - AGPL-3.0"
PROJECT_AUTHOR = "Aref Daei"
PROJECT_AUTHOR_EMAIL = "aref.daei@outlook.com"
PROJECT_URL = "https://github.com/aref-daei/ziro.ai"
PROJECT_LATEST_RELEASE_URL = "https://github.com/aref-daei/ziro.ai/releases/latest"

# If DEBUG is False, disable logging completely
DEBUG = False

# Translate settings
MAX_TRANSLATION_LENGTH = 512
BATCH_SIZE = 8

# FFmpeg settings
AUDIO_FORMAT = "wav"
AUDIO_CODEC = "pcm_s16le"
AUDIO_RATE = 16000

# Subtitle settings
SRT_ENCODING = "utf-8"
MAX_SUBTITLE_LENGTH = 42  # Maximum character in a line
