from __future__ import annotations

import qtawesome as qta
import torch
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QMouseEvent, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QWidget,
    QMenu,
    QFileDialog,
    QMessageBox, QLayout,
)

from core.constants import PROJECT_NAME, PROJECT_DESCRIPTION, PROJECT_VERSION, PROJECT_LICENSE, PROJECT_URL
from core.paths import PATHS

ICONS_COLOR = "#F0F2F0"
VIDEO_FILE_FILTER = "Video Files (*.mp4 *.mkv *.mov *.avi *.webm *.flv *.wmv)"


class TitleBar(QFrame):
    # File menu: emits the paths chosen via "Open File..." / "Open Folder..."
    open_file_requested = Signal(list)
    open_folder_requested = Signal(str)

    # Edit menu: no real preferences system yet, just a hook for later
    preferences_requested = Signal()

    # Help menu: the actual update check needs network access, so it's left
    # to whoever connects this signal (MainWindow / an update-checker module)
    check_updates_requested = Signal()

    def __init__(self, window: QWidget):
        super().__init__()

        self._window = window
        self._drag_pos: QPoint | None = None

        self.setObjectName("TitleBar")
        self.setFixedHeight(42)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._build_ui()

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.logo_label = QLabel()
        self.logo_label.setObjectName("LogoLabel")
        self.logo_label.setPixmap(QPixmap(str(PATHS["icons"] / "Ziro.ico")))

        self.file_menu_btn = QPushButton("File")
        self.file_menu_btn.setObjectName("MenuButton")
        self._build_file_menu()

        self.edit_menu_btn = QPushButton("Edit")
        self.edit_menu_btn.setObjectName("MenuButton")
        self._build_edit_menu()

        self.help_menu_btn = QPushButton("Help")
        self.help_menu_btn.setObjectName("MenuButton")
        self._build_help_menu()

        self._window.notification.connect(self._on_notification)
        self.notice_label = QLabel()
        self.notice_label.setObjectName("Notice")
        self.notice_label.hide()

        self.device_label = QLabel()
        self.device_label.setObjectName("DeviceLabel")
        self.device_label.setText("Device: " + ("CUDA" if torch.cuda.is_available() else "CPU"))

        self.min_btn = QPushButton()
        self.min_btn.setObjectName("MinButton")
        self.min_btn.setIcon(qta.icon("mdi6.window-minimize", color=ICONS_COLOR))

        self.max_btn = QPushButton()
        self.max_btn.setObjectName("MaxButton")
        self.max_btn.setIcon(qta.icon("mdi6.window-maximize", color=ICONS_COLOR))

        self.close_btn = QPushButton()
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setIcon(qta.icon("mdi6.close", color=ICONS_COLOR))

        for btn in (self.min_btn, self.max_btn, self.close_btn):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        for btn in (self.min_btn, self.max_btn, self.close_btn):
            btn.setFixedSize(48, 42)

        self.min_btn.clicked.connect(self._window.showMinimized)
        self.max_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self._window.close)

        layout.addWidget(self.logo_label)
        for btn in (self.file_menu_btn, self.edit_menu_btn, self.help_menu_btn):
            layout.addWidget(btn)
        layout.addStretch()
        layout.addWidget(self.notice_label)
        layout.addWidget(self.device_label)
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

    # ------------------------------------------------------------------ Menus

    def _build_file_menu(self) -> None:
        menu = QMenu(self)
        menu.addAction("Open File...", self._on_open_file)
        menu.addAction("Open Folder...", self._on_open_folder)
        self.file_menu_btn.setMenu(menu)

    def _build_edit_menu(self) -> None:
        menu = QMenu(self)
        menu.addAction("Preferences...", self.preferences_requested.emit)
        self.edit_menu_btn.setMenu(menu)

    def _build_help_menu(self) -> None:
        menu = QMenu(self)
        menu.addAction("Check for Updates...", self.check_updates_requested.emit)
        menu.addAction("About", self._show_about_dialog)
        self.help_menu_btn.setMenu(menu)

    def _on_open_file(self) -> None:
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Open Video Files", "", VIDEO_FILE_FILTER
        )
        if file_paths:
            self.open_file_requested.emit(file_paths)

    def _on_open_folder(self) -> None:
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder_path:
            self.open_folder_requested.emit(folder_path)

    def _show_about_dialog(self) -> None:
        msg = QMessageBox(self)
        msg.setObjectName("About")
        msg.setWindowTitle(f"About {PROJECT_NAME}")

        msg.setText(f"""
            <div align="center">
                <h2>{PROJECT_NAME}</h2>
                <p><b>Version {PROJECT_VERSION}</b></p>
                <p>{PROJECT_DESCRIPTION}</p>
                <p>Built with ❤️ using PySide6</p>
                <p>Licensed under {PROJECT_LICENSE}</p>
                <p>
                    <b>Source Code</b><br>
                    <a href="{PROJECT_URL}">{PROJECT_URL}</a>
                </p>
            </div>
        """)

        msg.setTextFormat(Qt.RichText)
        msg.setTextInteractionFlags(Qt.TextBrowserInteraction)

        label = msg.findChild(QLabel)
        if label:
            label.setOpenExternalLinks(True)

        msg.exec()

    # ------------------------------------------------------------- Behavior

    def toggle_maximize(self) -> None:
        if self._window.isMaximized():
            self._window.showNormal()
            self.max_btn.setIcon(qta.icon("mdi6.window-maximize", color=ICONS_COLOR))
        else:
            self._window.showMaximized()
            self.max_btn.setIcon(qta.icon("mdi6.window-restore", color=ICONS_COLOR))

    # -------------------------------------------------- Moving with the mouse

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            window_handle = self._window.windowHandle()
            if window_handle is not None:
                window_handle.startSystemMove()
            event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_maximize()
            event.accept()

    def _on_notification(self, message: str) -> None:
        if message != "":
            self.notice_label.setText(message)
            self.notice_label.show()
        else:
            self.notice_label.hide()
