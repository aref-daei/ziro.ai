from pathlib import Path

import ffmpeg

from core.config import AUDIO_FORMAT, AUDIO_CODEC, AUDIO_RATE
from core.paths import PATHS


class AudioExtractorService:
    """Extract audio from video with ffmpeg"""

    def extract(self, video_path: str) -> str:
        """Extract audio from video"""
        try:
            audio_path = PATHS["temp"] / f"{Path(video_path).stem}_audio.{AUDIO_FORMAT}"
            audio_path = str(audio_path)

            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream,
                audio_path,
                acodec=AUDIO_CODEC,
                ac=1,  # Convert to mono
                ar=AUDIO_RATE,
                loglevel="error",
            )
            ffmpeg.run(stream, overwrite_output=True, capture_stderr=True)

            return audio_path

        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            raise RuntimeError(f"Error extracting audio: {error_message}")
