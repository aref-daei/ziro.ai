from __future__ import annotations

import os

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QProgressBar,
    QScrollArea,
    QWidget,
)

from src.core.queue_status import QueueStatus
from .panel import Panel


class QueueRow(QFrame):
    """One card in the queue: file name, progress bar, and current status."""

    def __init__(self, file_path: str, parent: QWidget | None = None):
        super().__init__(parent)

        self.file_path = file_path
        self._status = QueueStatus.QUEUED

        # Same row background as InspectorPanel/SidebarPanel for a consistent look
        self.setObjectName("InspectorRow")
        self.setFixedWidth(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        self.name_label = QLabel()
        self.name_label.setObjectName("InspectorLabel")
        self.name_label.setToolTip(file_path)
        self._set_elided_name(os.path.basename(file_path))

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("QueueProgressBar")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)

        status_row = QHBoxLayout()
        status_row.setSpacing(6)

        self.status_icon = QLabel()
        self.status_icon.setFixedSize(14, 14)

        self.status_text = QLabel()
        self.status_text.setObjectName("QueueStatusLabel")

        status_row.addWidget(self.status_icon)
        status_row.addWidget(self.status_text)
        status_row.addStretch()

        layout.addWidget(self.name_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(status_row)

        self.set_status(QueueStatus.QUEUED)

    def _set_elided_name(self, name: str) -> None:
        # Fixed-width card, so long file names need to be elided rather than
        # stretching the card or wrapping to a second line.
        metrics = self.name_label.fontMetrics()
        elided = metrics.elidedText(name, Qt.TextElideMode.ElideMiddle, 180)
        self.name_label.setText(elided)

    def set_progress(self, percent: int) -> None:
        percent = max(0, min(100, percent))
        self.progress_bar.setValue(percent)
        if self._status == QueueStatus.PROCESSING:
            self.status_text.setText(f"Processing {percent}%")

    def set_status(self, status: QueueStatus) -> None:
        self._status = status

        icon_by_status = {
            QueueStatus.QUEUED: ("mdi6.clock-outline", "#999999", "Queued"),
            QueueStatus.PROCESSING: (
                "mdi6.progress-clock",
                "#54C750",
                f"Processing {self.progress_bar.value()}%",
            ),
            QueueStatus.DONE: ("mdi6.check-circle", "#54C750", "Done"),
            QueueStatus.FAILED: ("mdi6.alert-circle", "#e05c5c", "Failed"),
            QueueStatus.CANCELLED: (
                "mdi6.cancel",
                "#F0AD4E",
                "Cancelled",
            ),
        }
        icon_name, color, text = icon_by_status[status]

        self.status_icon.setPixmap(qta.icon(icon_name, color=color).pixmap(14, 14))
        self.status_text.setText(text)
        self.status_text.setStyleSheet(f"color: {color};")


class QueuePanel(Panel):
    def __init__(self, title: str, min_width: int = None, max_width: int = None):
        Panel.__init__(self, title, min_width, max_width)

        self._rows: dict[str, QueueRow] = {}

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("PanelTitle")
        layout.addWidget(title_label)

        self._list_container = QWidget()
        self._list_container.setObjectName("ListContainer")
        self._list_layout = QHBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(8)
        # Trailing stretch keeps cards packed to the left as they're added
        self._list_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setObjectName("QueueScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(self._list_container)

        layout.addWidget(scroll_area)

    # ------------------------------------------------------------ public API

    def start_queue(self, file_paths: list[str]) -> None:
        """Reset the queue and add one card per file, all starting as 'queued'.

        Call this when the subtitle-generation process starts, passing
        SidebarPanel.selected_files().
        """
        self.clear_queue()
        for file_path in file_paths:
            row = QueueRow(file_path)
            self._rows[file_path] = row
            self._list_layout.insertWidget(self._list_layout.count() - 1, row)

    def clear_queue(self) -> None:
        for row in self._rows.values():
            self._list_layout.removeWidget(row)
            row.deleteLater()
        self._rows.clear()

    def set_progress(self, file_path: str, percent: int) -> None:
        """Update one file's progress bar (0-100). Call this repeatedly as
        that file's subtitle generation advances."""
        row = self._rows.get(file_path)
        if row is not None:
            row.set_progress(percent)

    def set_status(self, file_path: str, status: QueueStatus) -> None:
        """Move one file to a new status (queued/processing/done/failed)."""
        row = self._rows.get(file_path)
        if row is not None:
            row.set_status(status)
