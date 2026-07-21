import shutil

import requests
from packaging.version import Version, InvalidVersion

from .constants import PROJECT_LATEST_RELEASE_URL, PROJECT_VERSION


class Checker:
    @staticmethod
    def exists_ffmpeg() -> bool:
        return shutil.which("ffmpeg") is not None

    @staticmethod
    def is_internet_access() -> bool:
        try:
            response = requests.get("https://www.google.com", timeout=3)
            return response.status_code == 200
        except requests.ConnectionError:
            return False

    @staticmethod
    def is_update_available() -> bool:
        try:
            response = requests.get(
                PROJECT_LATEST_RELEASE_URL, allow_redirects=True, timeout=1
            )
            final_url = response.url
            latest_tag = final_url.rstrip("/").split("/")[-1]
            latest_version = latest_tag.lstrip("v")
            return Version(latest_version) > Version(PROJECT_VERSION)
        except (requests.ConnectionError, InvalidVersion):
            return False
