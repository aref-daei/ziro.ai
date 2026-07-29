from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path

from src.core.paths import PATHS

_INSTALL_DIR = PATHS["ffmpeg"]


def find_ffmpeg() -> Path | None:
    """
    Checks system PATH first, then this app's own install directory
    (from a previous FFDownloader run).
    """
    system_path = shutil.which("ffmpeg")
    if system_path is not None:
        return Path(system_path)

    if not _INSTALL_DIR.exists():
        return None

    binary_name = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
    matches = list(_INSTALL_DIR.rglob(binary_name))
    return matches[0] if matches else None


def register_ffmpeg_in_env(binary_path: Path) -> None:
    """Prepends ffmpeg's folder to this process's PATH."""
    binary_dir = str(binary_path.parent)
    current_path = os.environ.get("PATH", "")
    if binary_dir not in current_path.split(os.pathsep):
        os.environ["PATH"] = binary_dir + os.pathsep + current_path


def ensure_ffmpeg_available() -> bool:
    """
    Synchronous startup check. Returns True if ffmpeg is already available
    (and registers it in PATH). Returns False only when a download is
    needed - that's when FFDownloader needs to run on a QThread.
    """
    binary_path = find_ffmpeg()
    if binary_path is None:
        return False

    register_ffmpeg_in_env(binary_path)
    return True
