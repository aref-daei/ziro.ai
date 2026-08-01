import subprocess
import sys

if sys.platform == "win32":
    _original_popen_init = subprocess.Popen.__init__


    def _no_window_popen_init(self, *args, **kwargs):
        kwargs.setdefault("creationflags", 0)
        kwargs["creationflags"] |= subprocess.CREATE_NO_WINDOW
        _original_popen_init(self, *args, **kwargs)


    subprocess.Popen.__init__ = _no_window_popen_init
