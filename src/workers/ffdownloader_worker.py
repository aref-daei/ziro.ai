from __future__ import annotations

import platform
import shutil
import stat
import subprocess
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlparse

import requests
from PySide6.QtCore import QObject, Signal, Slot

from core.ffmpeg_locator import find_ffmpeg, register_ffmpeg_in_env
from core.paths import PATHS
from logger import Logger

# Third-party static-build host; no checksums provided, so HTTPS + archive
# validation below are our only integrity checks.
FFBINARIES_API_URL = "https://ffbinaries.com/api/v1/version/latest"

# (platform.system(), platform.machine()) -> ffbinaries platform key.
# No Apple Silicon build; osx-64 runs via Rosetta 2 on arm64 Macs.
_PLATFORM_MAP = {
    ("Windows", "AMD64"): "windows-64",
    ("Windows", "x86_64"): "windows-64",
    ("Darwin", "x86_64"): "osx-64",
    ("Darwin", "arm64"): "osx-64",
    ("Linux", "x86_64"): "linux-64",
    ("Linux", "aarch64"): "linux-arm64",
    ("Linux", "armv7l"): "linux-armhf",
}


class _DownloadFailed(Exception):
    """Expected, user-facing failure (unsupported platform, bad API
    response, missing binary after extraction, ...)."""


class FFDownloader(QObject):
    """
    Downloads ffmpeg for the current OS/arch, installs it under
    PATHS["ffmpeg"], and prepends its folder to this process's PATH.

    Run like ProcessingWorker: create it, moveToThread it, connect
    QThread.started to run().
    """

    download_started = Signal()
    progress = Signal(int)  # 0-100
    finished = Signal(bool, str)  # (success, message)

    def __init__(self):
        super().__init__()
        self.logger = Logger()
        self.install_dir = PATHS["ffmpeg"]

    @Slot()
    def run(self) -> None:
        self.download_started.emit()

        try:
            existing_binary = find_ffmpeg()
            if existing_binary is not None:
                register_ffmpeg_in_env(existing_binary)
                self.progress.emit(100)
                self.finished.emit(True, "FFmpeg already installed.")
                return

            platform_key = self._detect_platform_key()
            download_url = self._get_download_url(platform_key)
            self.install_dir.mkdir(parents=True, exist_ok=True)

            # Extract into a scratch dir; only copied into install_dir on
            # full success, so a failed run can't leave a broken installation.
            with tempfile.TemporaryDirectory(prefix="ffmpeg_install_") as scratch:
                scratch_dir = Path(scratch)
                zip_path = scratch_dir / "ffmpeg.zip"

                self._download_file(download_url, zip_path)
                self._safe_extract_zip(zip_path, scratch_dir)
                zip_path.unlink(missing_ok=True)

                self._install_from_scratch(scratch_dir)

            binary_path = find_ffmpeg()
            if binary_path is None:
                raise _DownloadFailed(
                    "Downloaded FFmpeg archive did not contain a recognizable executable."
                )

            self._make_executable(binary_path)
            self._remove_macos_quarantine(binary_path)
            register_ffmpeg_in_env(binary_path)

            self.progress.emit(100)
            self.finished.emit(True, "FFmpeg downloaded and installed successfully.")

        except _DownloadFailed as e:
            self.logger.error(f"FFDownloader failed: {e}")
            self._cleanup_partial_install()
            self.finished.emit(False, str(e))

        except requests.RequestException as e:
            self.logger.error(f"FFDownloader network error: {e}")
            self._cleanup_partial_install()
            self.finished.emit(False, "Network error while downloading FFmpeg.")

        except Exception as e:
            self.logger.error(f"FFDownloader unexpected error: {e}")
            self._cleanup_partial_install()
            self.finished.emit(False, f"Unexpected error: {e}")

    # ------------------------------------------------------------ platform detection

    def _detect_platform_key(self) -> str:
        system = platform.system()
        machine = platform.machine()

        key = _PLATFORM_MAP.get((system, machine))
        if key is None:
            raise _DownloadFailed(
                f"No automatic FFmpeg download is available for {system} {machine}. "
                "Please install FFmpeg manually and make sure it's on your PATH."
            )
        return key

    def _get_download_url(self, platform_key: str) -> str:
        response = requests.get(FFBINARIES_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        bin_entry = data.get("bin", {}).get(platform_key)
        if not bin_entry or "ffmpeg" not in bin_entry:
            raise _DownloadFailed(f"No FFmpeg build is listed for platform '{platform_key}'.")

        url = bin_entry["ffmpeg"]
        if urlparse(url).scheme != "https":
            raise _DownloadFailed("Refusing to download FFmpeg over a non-HTTPS URL.")

        return url

    # ------------------------------------------------------------ download / extract

    def _download_file(self, url: str, destination: Path) -> None:
        with requests.get(url, stream=True, timeout=30) as response:
            response.raise_for_status()
            total_size = int(response.headers.get("Content-Length", 0))
            downloaded = 0

            with open(destination, "wb") as f:
                for chunk in response.iter_content(chunk_size=256 * 1024):
                    if not chunk:
                        continue
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total_size > 0:
                        # 0-90% reserved for the download; the rest is for
                        # extraction/setup.
                        percent = min(int(downloaded / total_size * 90), 90)
                        self.progress.emit(percent)

    def _safe_extract_zip(self, zip_path: Path, destination: Path) -> None:
        """Extracts a zip, rejecting any member path that would escape
        `destination` (zip-slip)."""
        destination = destination.resolve()
        with zipfile.ZipFile(zip_path, "r") as zf:
            for member in zf.infolist():
                member_path = (destination / member.filename).resolve()
                if destination not in member_path.parents and member_path != destination:
                    raise _DownloadFailed(
                        "Downloaded archive contains an unsafe file path and was rejected."
                    )
            zf.extractall(destination)

    def _install_from_scratch(self, scratch_dir: Path) -> None:
        """Copies the verified binary from scratch into the real install dir."""
        binary_name = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
        found = next(scratch_dir.rglob(binary_name), None)
        if found is None:
            raise _DownloadFailed(
                "Downloaded FFmpeg archive did not contain a recognizable executable."
            )

        self.install_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(found, self.install_dir / binary_name)

    def _cleanup_partial_install(self) -> None:
        # Remove a partial/corrupt install so it's not mistaken for a working one.
        binary_name = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
        if self.install_dir.exists() and not (self.install_dir / binary_name).exists():
            shutil.rmtree(self.install_dir, ignore_errors=True)

    # ------------------------------------------------------------ post-install

    def _make_executable(self, binary_path: Path) -> None:
        # zipfile doesn't restore the Unix executable bit, so set it explicitly.
        if platform.system() == "Windows":
            return
        current_mode = binary_path.stat().st_mode
        binary_path.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def _remove_macos_quarantine(self, binary_path: Path) -> None:
        # Clears Gatekeeper's quarantine flag on network-downloaded files.
        if platform.system() != "Darwin":
            return
        try:
            subprocess.run(
                ["xattr", "-d", "com.apple.quarantine", str(binary_path)],
                check=False,
                capture_output=True,
            )
        except FileNotFoundError:
            pass  # xattr unavailable - nothing more we can do
