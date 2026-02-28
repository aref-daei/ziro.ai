import sys
import os
from pathlib import Path
import platform

from core.settings import PROJECT_NAME


def _get_app_paths():
    if getattr(sys, "frozen", False):
        # PyInstaller mode
        base_dir = Path(sys._MEIPASS)  # type: ignore

        if platform.system() == "Windows":
            app_data = Path(os.getenv("APPDATA")) / PROJECT_NAME  # type: ignore
            output = Path.home() / "Videos" / PROJECT_NAME
        elif platform.system() == "Darwin":  # macOS
            app_data = Path.home() / "Library" / "Application Support" / PROJECT_NAME
            output = Path.home() / "Videos" / PROJECT_NAME
        else:  # Linux/Unix
            app_data = Path.home() / f".{PROJECT_NAME.lower()}"
            output = Path.home() / "Videos" / PROJECT_NAME
    else:
        # Development mode
        base_dir = Path(__file__).parent.parent
        app_data = base_dir.parent / "Data"
        output = app_data / "output"

    paths = {
        "base": base_dir,
        "app_data": app_data,
        "config": app_data / "config",
        "models": app_data / "models",
        "logs": app_data / "logs",
        "temp": app_data / "temp",
        "output": output,
    }

    for key in ["config", "models", "logs", "temp", "output"]:
        paths[key].mkdir(parents=True, exist_ok=True)

    return paths


PATHS = _get_app_paths()
