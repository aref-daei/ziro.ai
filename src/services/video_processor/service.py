from pathlib import Path

import ffmpeg

from core.config import OUTPUT_DIR


class VideoProcessorService:
    """Add subtitles to video with ffmpeg"""

    def add_subtitles(
        self, video_path: str, subtitle_paths: dict, output_name: str
    ) -> str:
        """
        Add subtitles to video (soft-sub)

        Args:
            video_path: path to the original video
            subtitle_paths: dictionary {'en': 'path/to/en.srt', 'fa': 'path/to/fa.srt'}
            output_name: output file name

        Returns:
            video path with subtitles
        """
        if output_name is None:
            output_name = f"{Path(video_path).stem}_subtitled.mkv"

        output_path = OUTPUT_DIR / output_name
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Original video and audio
            video = ffmpeg.input(video_path)

            # Add subtitles
            subtitle_inputs = []
            metadata = {}

            for i, (lang, sub_path) in enumerate(
                reversed(list(subtitle_paths.items()))
            ):
                subtitle_inputs.append(ffmpeg.input(sub_path))
                metadata[f"metadata:s:s:{i}"] = f"language={lang}"
                # metadata[f'metadata:s:s:{i}'] = f'title={lang.upper()}'

            # Combine all
            inputs = [video] + subtitle_inputs

            output_args = {
                "c:v": "copy",  # Copy video without re-encoding
                "c:a": "copy",  # Copy audio without re-encoding
                "c:s": "srt",  # Subtitle format
                **metadata,  # Metadata
            }

            stream = ffmpeg.output(*inputs, str(output_path), **output_args)

            # Execute command
            ffmpeg.run(stream, overwrite_output=True, capture_stderr=True)

            return str(output_path)

        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            raise RuntimeError(f"Error adding subtitle: {error_message}")
