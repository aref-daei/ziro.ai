import os
import platform
import shutil
import subprocess
from pathlib import Path

from core.paths import PATHS


class FileHandler:
    """File management utilities"""

    @staticmethod
    def open_path(path: Path):
        """Open path"""
        system = platform.system()
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    @staticmethod
    def get_file_size(file_path: str | Path) -> int:
        """Get file size in bytes"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        return path.stat().st_size

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format file size to human-readable string"""
        if size_bytes == 0:
            return "0 B"

        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = float(size_bytes)

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        return f"{size:.2f} {units[unit_index]}"

    @staticmethod
    def clean_temp_files() -> int:
        """Clear all temporary files and directories"""
        if not PATHS["temp"].exists():
            return 0

        deleted_count = 0
        for item in PATHS["temp"].glob("*"):
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
                deleted_count += 1
            except Exception as e:
                raise RuntimeError(f"Error deleting {item}: {e}")

        return deleted_count

    @staticmethod
    def ensure_directory(path: str | Path) -> Path:
        """Ensure directory exists, create if it doesn't"""
        path_obj = Path(path)
        path_obj.mkdir(parents=True, exist_ok=True)
        return path_obj

    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """Remove illegal characters from filename for cross-platform compatibility"""
        # Remove illegal characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')

        # Ensure filename is not empty
        if not filename:
            filename = 'unnamed_file'

        return filename

    @staticmethod
    def list_files(directory: str | Path, pattern: str = "*") -> list[Path]:
        """List files in directory matching pattern"""
        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        return list(dir_path.glob(pattern))

    @staticmethod
    def copy_with_safe_name(source: str | Path, destination_dir: str | Path) -> Path:
        """Copy file to destination with safe filename"""
        source_path = Path(source)
        dest_dir = Path(destination_dir)

        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source}")

        # Create safe filename
        safe_name = FileHandler.get_safe_filename(source_path.name)
        dest_path = dest_dir / safe_name

        # Ensure destination directory exists
        FileHandler.ensure_directory(dest_dir)

        # Copy file
        shutil.copy2(source_path, dest_path)
        return dest_path
