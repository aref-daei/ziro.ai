# Ziro.ai 🎬

**Automatically add any language subtitles to your favorite videos.**

![License](https://img.shields.io/badge/license-AGPL-white.svg)
![Version](https://img.shields.io/badge/version-2.0-green.svg)

[Persian](/docs/README.fa.md)

[How It Works](#how-it-works) - [Prerequisites](#prerequisites) - [Installation Guide](#installation-guide) - [Future Development](#future-development) - [Contributing](#contributing) - [License](#license)

Ziro is an all-in-one subtitle automation tool powered by advanced AI. It seamlessly handles the entire workflow - from accurately transcribing speech in your favorite videos and translating it into any language, to synchronizing the text and burning the final subtitles directly onto your video - delivering a ready-to-share, subtitled file in just a few clicks.

## How It Works

Our automated pipeline:

1. **Transcribes** speech from your video using OpenAI's Whisper.
2. **Translates** the text into Persian using Google Translate and DeepL.
3. **Generates & syncs** perfectly timed subtitles.
4. **Renders** the final video with subtitles burned in or as a separate file.

## Prerequisites

Before you begin, make sure your system meets the following requirements:

- Dual-core CPU (Quad-core recommended)
- 8 GB RAM (16 GB recommended)
- A CUDA-compatible GPU is recommended for faster performance

## Installation Guide

Getting started with Ziro is quick and straightforward. Follow the steps below based on your operating system.

### Windows Installation

1. **Download the Installer**  
   Download the latest version of Ziro (`.exe` file) from the [latest release](https://github.com/aref-daei/ziro.ai/releases/latest) page.

2. **Run as Administrator**  
   Right-click the downloaded file and select **“Run as administrator”**.

3. **Install for All Users**  
   When prompted, choose **“Install for all users”** and proceed by clicking **Next** until the installation is complete.

4. **You're All Set!**  
   After installation, Ziro will launch automatically, and you can start generating subtitles for your favorite videos in any language with just a few clicks.

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
| :-----------------: |:--------------:|
|        Tiny         |     70 MB      |
|        Base         |     140 MB     |
|        Small        |     460 MB     |
|       Medium        |     1.4 GB     |
|        Large        |     2.8 GB     |

| Translation Model | Size (approx.) |
| :---------------: | :------------: |
| Google Translate  |    *online*    |
|       DeepL       |    *online*    |

⚠️ **Note 3: Processing Complete**  
Once processing is complete, click **Open Output** to automatically open the folder containing your subtitled video.

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](/CONTRIBUTING.md) to learn how you can help improve Ziro.ai.

## License

This project is licensed under the AGPL-3.0 License - see the [LICENSE](/LICENSE) file for details.
