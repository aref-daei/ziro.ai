from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton

from src.core.paths import PATHS


class BottomBar(QFrame):
    stop_requested = Signal()

    def __init__(self):
        super().__init__()

        self.setFixedHeight(50)

        bottom_layout = QHBoxLayout(self)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("Stop")
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_requested.emit)

        self.output_btn = QPushButton("Open Output")
        self.output_btn.setObjectName("OpenOutput")
        self.output_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.output_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(PATHS["output"])))
        )

        self.logs_btn = QPushButton("Logs")
        self.logs_btn.setObjectName("Logs")
        self.logs_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logs_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(PATHS["logs"])))
        )

        bottom_layout.addWidget(self.stop_btn)
        bottom_layout.addWidget(self.output_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.logs_btn)

    # ------------------------------------------------------------ processing state

    def set_processing(self, is_processing: bool) -> None:
        """Call this when the subtitle-generation process starts/stops, so
        Stop is only clickable while something is actually running."""
        self.stop_btn.setEnabled(is_processing)
