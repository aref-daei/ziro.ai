from __future__ import annotations

import os

import qtawesome as qta
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QFileDialog,
    QScrollArea,
    QWidget,
    QSizePolicy,
)

from .panel import Panel

VIDEO_FILE_FILTER = "Video Files (*.mp4 *.mkv *.mov *.avi *.webm *.flv *.wmv)"


class FileRow(QFrame):
    """A single row representing one video file in the sidebar's file list.

    Two distinct interactions live here, on purpose:
    - the checkbox toggles whether this video is included in batch processing
      (see is_selected() / SidebarPanel.selected_files())
    - clicking anywhere else on the row previews that video (preview_requested)
    """

    preview_requested = Signal(str)

    def __init__(self, file_path: str, parent: QWidget | None = None):
        super().__init__(parent)

        self.file_path = file_path

        # Reuse the exact same row/checkbox object names (and therefore colors)
        # as InspectorPanel, so the sidebar list matches the rest of the app.
        self.setObjectName("InspectorRow")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        # Selection toggle, same pattern as InspectorPanel's "Add subtitles" checkbox.
        # This marks the video for batch processing, it does NOT trigger preview.
        self.select_toggle = QPushButton()
        self.select_toggle.setObjectName("InspectorCheckbox")
        self.select_toggle.setCheckable(True)
        self.select_toggle.setChecked(True)  # newly added files are selected by default
        self.select_toggle.setFixedSize(20, 20)
        self.select_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.select_toggle.toggled.connect(self._update_icon)
        self._update_icon(self.select_toggle.isChecked())

        # Only the file name is shown; the full path is kept as an attribute
        # and exposed as a tooltip in case the user needs to check it.
        self.name_label = QLabel(os.path.basename(file_path))
        self.name_label.setObjectName("InspectorLabel")
        self.name_label.setToolTip(file_path)
        self.name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # A remove button so the list stays usable, not append-only
        self.remove_btn = QPushButton()
        self.remove_btn.setObjectName("FileRemoveButton")
        self.remove_btn.setIcon(qta.icon("mdi6.close", color="#dddddd"))
        self.remove_btn.setFixedSize(20, 20)
        self.remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addWidget(self.select_toggle)
        layout.addWidget(self.name_label)
        layout.addWidget(self.remove_btn)

    def is_selected(self) -> bool:
        return self.select_toggle.isChecked()

    def set_active(self, active: bool) -> None:
        """Highlight this row as the one currently shown in the preview panel."""
        self.setProperty("active", active)
        # Dynamic properties need a manual re-polish, Qt won't pick up the
        # QSS attribute-selector change on its own.
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        # Only reached for clicks on the row's own background: clicks on the
        # checkbox/remove buttons are consumed by those child widgets first.
        if event.button() == Qt.MouseButton.LeftButton:
            self.preview_requested.emit(self.file_path)
        super().mousePressEvent(event)

    def _update_icon(self, checked: bool) -> None:
        # Same "no icon when unchecked" trick used in InspectorPanel, since
        # the checked look comes entirely from the QSS background-color.
        if checked:
            self.select_toggle.setIcon(qta.icon("mdi6.check-bold", color="#f0f2f0"))
        else:
            self.select_toggle.setIcon(QIcon())


class SidebarPanel(Panel):
    # Emitted with the file path whenever a video should be shown in the preview panel
    file_selected = Signal(str)

    def __init__(self, title: str, min_width: int = None, max_width: int = None):
        Panel.__init__(self, title, min_width, max_width)

        self._active_row: FileRow | None = None

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # -------- Header row: title + Add button --------
        top_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("panelTitle")
        add_button = QPushButton("Add")
        add_button.setObjectName("addButton")
        add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        add_button.clicked.connect(self._on_add_clicked)

        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(add_button)
        layout.addLayout(top_layout)

        # -------- Scrollable file list --------
        self.file_rows: list[FileRow] = []

        self._list_container = QWidget()
        self._list_container.setObjectName("ListContainer")
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(8)
        # Trailing stretch keeps rows pinned to the top as they get added,
        # instead of spreading out to fill the whole scroll area.
        self._list_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setObjectName("SidebarScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidget(self._list_container)

        layout.addWidget(scroll_area)

        self._apply_style()

    # ------------------------------------------------------------ actions

    def _on_add_clicked(self) -> None:
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select video files",
            "",
            VIDEO_FILE_FILTER,
        )
        for file_path in file_paths:
            self._add_file(file_path)

    def _add_file(self, file_path: str) -> None:
        row = FileRow(file_path)
        row.remove_btn.clicked.connect(lambda: self._remove_file(row))
        row.preview_requested.connect(self._on_row_preview_requested)

        # Insert right before the trailing stretch, so new rows always land
        # at the bottom of the list rather than after it.
        self._list_layout.insertWidget(self._list_layout.count() - 1, row)
        self.file_rows.append(row)

        # Nice default: preview the very first video added, instead of
        # requiring an extra click before anything shows up.
        if self._active_row is None:
            self._on_row_preview_requested(file_path, row)

    def _remove_file(self, row: FileRow) -> None:
        self.file_rows.remove(row)
        self._list_layout.removeWidget(row)
        if row is self._active_row:
            self._active_row = None
        row.deleteLater()

    def _on_row_preview_requested(self, file_path: str, row: FileRow | None = None) -> None:
        # row is passed explicitly by _add_file's auto-preview call; when this
        # runs as a Qt signal slot (user clicked a row) it comes from the sender.
        row = row or self.sender()

        if self._active_row is not None:
            self._active_row.set_active(False)
        row.set_active(True)
        self._active_row = row

        self.file_selected.emit(file_path)

    # ------------------------------------------------------------ public API

    def selected_files(self) -> list[str]:
        """Paths of every video currently marked as selected (checkbox on)."""
        return [row.file_path for row in self.file_rows if row.is_selected()]

    def all_files(self) -> list[str]:
        """Paths of every video in the list, regardless of selection state."""
        return [row.file_path for row in self.file_rows]

    # ------------------------------------------------------------ styling

    def _apply_style(self) -> None:
        # Colors match InspectorPanel's palette (#3E3F3E rows, #54C750 accent,
        # #f0f2f0 light text/icon) so the whole app reads as one consistent theme.
        self.setStyleSheet(
            """
            QFrame#InspectorRow {
                background-color: #3E3F3E;
                border-radius: 10px;
                border: 2px solid transparent;
            }
            QFrame#InspectorRow[active="true"] {
                border: 2px solid #54C750;
            }
            #InspectorLabel {
                color: #dddddd;
                font-size: 13px;
            }
            #InspectorCheckbox {
                background-color: transparent;
                border: 2px solid #54C750;
                border-radius: 6px;
            }
            #InspectorCheckbox:checked {
                background-color: #54C750;
                border: none;
            }
            #FileRemoveButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
            }
            #FileRemoveButton:hover {
                background-color: #4a4a4a;
            }
            #SidebarScrollArea {
                background-color: transparent;
                border: none;
            }
            #ListContainer {
                background-color: transparent;
            }
            """
        )