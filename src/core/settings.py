import yaml

from core.constants import *
from core.paths import PATHS


DEBUG = False  # If DEBUG is False, disable logging completely

# Translate settings
MAX_TRANSLATION_LENGTH = 512
BATCH_SIZE = 8

# FFmpeg settings
AUDIO_FORMAT = "wav"
AUDIO_RATE = 16000

# Subtitle settings
MAX_SUBTITLE_LENGTH = 42  # Maximum character in a line

config_path = PATHS["config"] / "config.yml"
if config_path.exists():
    with open(config_path) as f:
        data = yaml.safe_load(f)

        DEBUG = data["DEBUG"]
        MAX_TRANSLATION_LENGTH = data["MAX_TRANSLATION_LENGTH"]
        BATCH_SIZE = data["BATCH_SIZE"]
        AUDIO_FORMAT = data["AUDIO_FORMAT"]
        AUDIO_RATE = data["AUDIO_RATE"]
        MAX_SUBTITLE_LENGTH = data["MAX_SUBTITLE_LENGTH"]
