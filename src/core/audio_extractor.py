from pathlib import Path

import ffmpeg

from settings import AUDIO_FORMAT, AUDIO_CODEC, AUDIO_RATE, TEMP_DIR
from exceptions.audio_extractor_exc import *


class AudioExtractor:
    """Extract audio from video with ffmpeg"""

    @staticmethod
    def extract(video_path: str) -> str:
        """Extract audio from video"""
        try:
            audio_path = TEMP_DIR / f"{Path(video_path).stem}_audio.{AUDIO_FORMAT}"
            audio_path = str(audio_path)

            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream,
                audio_path,
                acodec=AUDIO_CODEC,
                ac=1,  # Convert to mono
                ar=AUDIO_RATE,
                loglevel="error"
            )
            ffmpeg.run(stream, overwrite_output=True, capture_stderr=True)

            return audio_path

        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            raise AudioExtractionError(f"Error extracting audio: {error_message}")

    @staticmethod
    def get_video_duration(video_path: str) -> float:
        """Get video length in seconds"""
        try:
            probe = ffmpeg.probe(video_path)
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            raise VideoProbeError(f"Error reading video information: {e}")
