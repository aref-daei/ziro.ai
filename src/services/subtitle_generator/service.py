from pathlib import Path

from core.config import SRT_ENCODING


class SubtitleGeneratorService:
    """Generating SRT files"""

    def generate_srt(self, segments: list[dict], output_path: Path) -> Path:
        """Generate SRT file"""
        rtl, end = "\u202b", "\u202c"

        srt_content = []

        for i, segment in enumerate(segments, start=1):
            # Subtitle number
            srt_content.append(str(i))

            # Scheduling
            start_time = self._format_timestamp(segment["start"])
            end_time = self._format_timestamp(segment["end"])
            srt_content.append(f"{start_time} --> {end_time}")

            # Text
            srt_content.append(f"{rtl}{segment['text']}{end}")

            # Blank line between subtitles
            srt_content.append("")

        # Writing a file
        with open(output_path, "w", encoding=SRT_ENCODING) as f:
            f.write("\n".join(srt_content))

        return output_path

    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to SRT format: 00:00:00,000"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
