# Ziro.ai 🎬

**Automatically add Persian & English subtitles to your English videos.**

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![License](https://img.shields.io/badge/license-AGPL-orange.svg)

[Persian](README.fa.md) | [How It Works](#how-it-works) - [Prerequisites](#prerequisites) - [Quick Start](#quick-start) - [Offline Model Setup](#offline-model-setup) - [Future Development](#future-development) - [License](#license)

This tool uses advanced AI to handle the entire process, from transcription and translation to generating the final subtitled video.

## How It Works

Our automated pipeline:

1. **Transcribes** speech from your video using OpenAI's Whisper.
2. **Translates** the text into Persian using the M2M100 model.
3. **Generates & syncs** perfectly timed bilingual subtitles.
4. **Renders** the final video with subtitles burned in or as a separate file.

## Prerequisites

Before you begin, make sure you have the following installed:

- Python 3.11 or higher
- FFmpeg
- 8GB RAM (16GB recommended)
- GPU with CUDA support recommended for faster performance

## Quick Start

1. Run `python main.py`
2. Select video file
3. Adjust options
4. Click "Start Processing"

## Offline Model Setup

> **Warning:** The download size of the M2M100 (418M parameters) model exceeds **1.4 GB**. Please ensure you have enough storage space and a stable internet connection before starting the download.
> _The M2M100 (1.2B parameters) model is over **4.7 GB**. [Learn more](model_sizes.md)_

To run the translation models completely offline and prevent any connection attempts to HuggingFace servers, follow these steps:

### 1. Download the model manually

Run this command in your terminal:

```
huggingface-cli download facebook/m2m100_418M --local-dir ./models/m2m100 --local-dir-use-symlinks False
```

### 2. Disable online access in code

Add these lines before loading your tokenizer or model:

```
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
```

### 3. Load models only from local files

```
self.tokenizer = M2M100Tokenizer.from_pretrained("./models/m2m100", local_files_only=True)
self.model = M2M100ForConditionalGeneration.from_pretrained("./models/m2m100", local_files_only=True)
```

## Future Development

- Upgrade to PyQt 6 and UI improvements

## License

This project is licensed under the AGPL-3.0 License - see the [LICENSE](LICENSE) file for details.
