import os
from pathlib import Path


class Validators:
    """Input validation"""

    SUPPORTED_VIDEO_FORMATS = ('.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm')

    @staticmethod
    def validate_video_file(file_path: str) -> bool:
        """Checking the validity of the video file"""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise ValueError(f"Invalid file path: {file_path}")

        ext = path.suffix.lower()
        if ext not in Validators.SUPPORTED_VIDEO_FORMATS:
            raise ValueError(
                f"Unsupported video format: {ext}\n"
                f"Supported formats: {', '.join(Validators.SUPPORTED_VIDEO_FORMATS)}"
            )

        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"Cannot read file: {file_path}")

        return True

    @staticmethod
    def validate_file_size(file_path: str, max_size_mb: int = 2000) -> bool:
        """Check file size"""
        size_mb = os.path.getsize(file_path) / (1024 * 1024)

        if size_mb > max_size_mb:
            raise ValueError(
                f"File size exceeds the limit: {size_mb:.2f} MB\n"
                f"Maximum allowed: {max_size_mb} MB"
            )

        return True

    @staticmethod
    def check_ffmpeg_installed() -> bool:
        """Check if ffmpeg is installed"""
        import shutil
        return shutil.which("ffmpeg") is not None
