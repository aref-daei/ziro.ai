import yaml

from .paths import PATHS

# Default settings
DEBUG = False
MAX_TRANSLATION_LENGTH = 512
BATCH_SIZE = 8
MAX_WORKERS = 3
AUDIO_FORMAT = "wav"
AUDIO_RATE = 16000
MAX_SUBTITLE_LENGTH = 42

_DEFAULTS = {
    "DEBUG": DEBUG,
    "MAX_TRANSLATION_LENGTH": MAX_TRANSLATION_LENGTH,
    "BATCH_SIZE": BATCH_SIZE,
    "MAX_WORKERS": MAX_WORKERS,
    "AUDIO_FORMAT": AUDIO_FORMAT,
    "AUDIO_RATE": AUDIO_RATE,
    "MAX_SUBTITLE_LENGTH": MAX_SUBTITLE_LENGTH,
}

config_path = PATHS["config"] / "config.yml"

if config_path.exists():
    with open(config_path) as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError:
            data = {}

    DEBUG                  = data.get("DEBUG",                  DEBUG)
    MAX_TRANSLATION_LENGTH = data.get("MAX_TRANSLATION_LENGTH", MAX_TRANSLATION_LENGTH)
    BATCH_SIZE             = data.get("BATCH_SIZE",             BATCH_SIZE)
    MAX_WORKERS            = data.get("MAX_WORKERS",            MAX_WORKERS)
    AUDIO_FORMAT           = data.get("AUDIO_FORMAT",           AUDIO_FORMAT)
    AUDIO_RATE             = data.get("AUDIO_RATE",             AUDIO_RATE)
    MAX_SUBTITLE_LENGTH    = data.get("MAX_SUBTITLE_LENGTH",    MAX_SUBTITLE_LENGTH)

else:
    with open(config_path, "w") as f:
        yaml.dump(_DEFAULTS, f)
