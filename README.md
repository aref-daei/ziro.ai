# Ziro.ai 🎬

[Persian](README.fa.md)

**Smart Desktop Application for Automated Bilingual Subtitle Generation**

Convert English videos into fully processed content enriched with both Persian and English subtitles using advanced AI models, providing an automated workflow that handles speech recognition, translation, subtitle generation, and final video rendering with minimal user effort.

![Version](https://img.shields.io/badge/version-1.0.0_rc-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

---

## ✨ Features

- 🎙️ **Speech-to-Text** with OpenAI Whisper
- 🌐 **Auto Translation** to Persian with HuggingFace Transformers
- 📝 Generate separate **SRT** files (English & Persian)
- 🎬 Add subtitles to video (**soft-subtitle**)
- 🖥️ **Graphical UI** with CustomTkinter
- ⚡ Support for **CPU** and **GPU**
- 📦 **Batch** processing of multiple videos

---

## 📋 Prerequisites

- Python 3.12 or higher
- ffmpeg
- 8GB RAM (16GB recommended)
- **GPU with CUDA support recommended for excellent performance**

---

## 📖 Usage

### Graphical Interface (GUI)

1. Run `python main.py`
2. Select video file
3. Adjust options
4. Click "Start Processing"

---

## ⚙️ Offline Model Setup

> ⚠️ **Warning:** The download size of the M2M100 (418M parameters) model exceeds **1.4 GB**. Please ensure you have enough storage space and a stable internet connection before starting the download.
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

---

## 🚀 Future Development

- Upgrade to PyQt 6 and UI improvements

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
