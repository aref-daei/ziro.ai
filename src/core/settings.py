from core.constants import *


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
