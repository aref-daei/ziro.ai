import sys
import os
from pathlib import Path
import platform

from core.config import PROJECT_NAME


def _get_app_paths():
    if getattr(sys, "frozen", False):
        # PyInstaller mode
        base_dir = Path(sys.executable).parent
        is_portable = False

        if "--portable" in sys.argv:
            is_portable = True
            app_data = base_dir / "Data"
        else:
            if platform.system() == "Windows":
                app_data = Path(os.getenv("APPDATA")) / PROJECT_NAME  # type: ignore
            elif platform.system() == "Darwin":  # macOS
                app_data = (
                    Path.home() / "Library" / "Application Support" / PROJECT_NAME
                )
            else:  # Linux/Unix
                app_data = Path.home() / f".{PROJECT_NAME.lower()}"
    else:
        # Development mode
        base_dir = Path(__file__).parent.parent.parent
        app_data = base_dir / "Data"
        is_portable = True

    paths = {
        "base": base_dir,
        "app_data": app_data,
        "temp": app_data / "Temp",
        "logs": app_data / "Logs",
        "output": app_data / "Output",
        "config": app_data / "Config",
        "cache": app_data / "Cache",
        "is_portable": is_portable,
    }

    for key in ["temp", "logs", "output", "config", "cache"]:
        paths[key].mkdir(parents=True, exist_ok=True)

    return paths


PATHS = _get_app_paths()
