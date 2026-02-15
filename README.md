# Ziro.ai 🎬

**Automatically add any language subtitles to your favorite videos.**

![License](https://img.shields.io/badge/license-AGPL-orange.svg)
![Version](https://img.shields.io/badge/version-1.4.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-yellow.svg)
![FFmpeg](https://img.shields.io/badge/ffmpeg-8.0-green.svg)

[Persian](docs/README.fa.md)

[How It Works](#how-it-works) - [Prerequisites](#prerequisites) - [Installation Guide](#installation-guide) - [Offline Model Setup](#offline-model-setup) - [Future Development](#future-development) - [License](#license)

Ziro is an all-in-one subtitle automation tool powered by advanced AI. It seamlessly handles the entire workflow - from accurately transcribing speech in your favorite videos and translating it into any language, to synchronizing the text and burning the final subtitles directly onto your video - delivering a ready-to-share, subtitled file in just a few clicks.

## How It Works

Our automated pipeline:

1. **Transcribes** speech from your video using OpenAI's Whisper.
2. **Translates** the text into Persian using Google Translate and DeepL.
3. **Generates & syncs** perfectly timed subtitles.
4. **Renders** the final video with subtitles burned in or as a separate file.

## Prerequisites

Before you begin, make sure you have the following installed:

- Python 3.11 or higher **(for development)**
- FFmpeg 8.0
- 8GB RAM (16GB recommended)
- GPU with CUDA support recommended for faster performance

## Installation Guide

Getting started with Ziro is quick and straightforward. Follow the steps below based on your operating system.

### Windows Installation

1. **Download the Installer**  
   Download the latest version of Ziro (`.exe` file) from the [latest release](https://github.com/aref-daei/ziro.ai/releases/latest) page.

2. **Run as Administrator**  
   Right-click the downloaded file and select **“Run as administrator”**.

3. **Install for All Users**  
   When prompted, choose **“Install for all users”** and proceed by clicking **Next** until the installation is complete.

4. **Launch Ziro**  
   After installation, Ziro will launch automatically.  
   - If you already have **FFmpeg** installed, the app will start loading its modules.  
   - If FFmpeg is not installed, Simply run the following command in **Command Prompt** or **PowerShell**:

     ```bash
     winget install "FFmpeg (Essentials Build)"
     ```

     Then restart Ziro.

5. **You’re All Set!**  
   Once the modules are loaded, you can start translating your favorite videos into any language subtitles in just a few clicks.

### Linux & macOS

*Support for Linux and macOS is coming soon.*

### Important Notes Before You Start

⚠️ **Note 1: Internet Connection Required**  
Ziro currently operates in **online mode only**. An active internet connection is required for processing. Interruptions may affect the workflow.

⚠️ **Note 2: Model Selection & Download**  
Before processing, please choose your preferred **Transcription** and **Translation** models carefully.  
On your first run, the selected models will be downloaded **automatically in the background** when you start the processing. Their approximate sizes are:

> **You won’t see a separate download progress bar** – instead, you’ll notice the processing time is longer for the first run as the models are being fetched and installed.

| Transcription Model | Size (approx.) |
| :-----------------: | :------------: |
|        Tiny         |     70 MB      |
|        Base         |   *default*    |
|        Small        |     460 MB     |
|       Medium        |     1.4 GB     |
|        Large        |     2.8 GB     |

| Translation Model | Size (approx.) |
| :---------------: | :------------: |
| Google Translate  |    *online*    |
|       DeepL       |    *online*    |

⚠️ **Note 3: Completion & Output**  
Once processing finishes, you’ll see a success message. Click **OK** to automatically open the folder containing your subtitled video.

## Future Development

- Upgrade to PyQt 6 and UI improvements

## License

This project is licensed under the AGPL-3.0 License - see the [LICENSE](LICENSE) file for details.
