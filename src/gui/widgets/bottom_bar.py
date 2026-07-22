from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton

from src.core.paths import PATHS


class BottomBar(QFrame):
    # Emitted when the user clicks Stop. The actual worker/thread running the
    # subtitle-generation process should connect to this and cancel itself.
    stop_requested = Signal()

    def __init__(self):
        super().__init__()

        self.setFixedHeight(50)

        bottom_layout = QHBoxLayout(self)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("Stop")
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.setEnabled(False)  # nothing is running at startup
        self.stop_btn.clicked.connect(self.stop_requested.emit)

        self.output_btn = QPushButton("Open Output")
        self.output_btn.setObjectName("OpenOutput")
        self.output_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.output_btn.clicked.connect(self._open_output_folder)

        self.logs_btn = QPushButton("Logs")
        self.logs_btn.setObjectName("Logs")
        self.logs_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logs_btn.clicked.connect(self._open_logs_folder)

        bottom_layout.addWidget(self.stop_btn)
        bottom_layout.addWidget(self.output_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.logs_btn)

    # ------------------------------------------------------------ processing state

    def set_processing(self, is_processing: bool) -> None:
        """Call this when the subtitle-generation process starts/stops, so
        Stop is only clickable while something is actually running."""
        self.stop_btn.setEnabled(is_processing)

    # ------------------------------------------------------------ actions

    def _open_output_folder(self) -> None:
        # Uses the OS's native file explorer (Explorer/Finder/etc.) rather
        # than a Windows-only call, so this keeps working if the app ever
        # runs on macOS/Linux too.
        output_dir = PATHS["output"]
        output_dir.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(output_dir)))

    def _open_logs_folder(self) -> None:
        logs_dir = PATHS["logs"]
        logs_dir.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(logs_dir)))