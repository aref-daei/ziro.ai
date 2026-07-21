from __future__ import annotations

import qtawesome as qta
import torch
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QFrame, QWidget

from src.core.checker import Checker
from src.core.paths import PATHS

ICONS_COLOR = "#F0F2F0"


class TitleBar(QFrame):

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

        self.menu_btn = QPushButton()
        self.menu_btn.setObjectName("MenuButton")
        self.menu_btn.setIcon(qta.icon("mdi6.menu", color=ICONS_COLOR))

        self.exists_ffmpeg = Checker.exists_ffmpeg()
        if not self.exists_ffmpeg:
            self.notice_label = QLabel()
            self.notice_label.setObjectName("Notice")
            self.notice_label.setText("⚠ FFmpeg not found!")

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

        # دکمه‌های کنترل پنجره اندازه ثابت دارند، دکمه‌ی تم می‌تواند متن‌محور بماند
        for btn in (self.min_btn, self.max_btn, self.close_btn):
            btn.setFixedSize(48, 42)

        self.min_btn.clicked.connect(self._window.showMinimized)
        self.max_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self._window.close)

        layout.addWidget(self.logo_label)
        layout.addWidget(self.menu_btn)
        layout.addStretch()
        if not self.exists_ffmpeg:
            layout.addWidget(self.notice_label)
        layout.addWidget(self.device_label)
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

    # ------------------------------------------------------------- رفتار

    def toggle_maximize(self) -> None:
        """بین حالت maximize و normal جابه‌جا می‌شود و آیکن دکمه را به‌روزرسانی می‌کند."""
        if self._window.isMaximized():
            self._window.showNormal()
            self.max_btn.setIcon(qta.icon("mdi6.window-maximize", color=ICONS_COLOR))
        else:
            self._window.showMaximized()
            self.max_btn.setIcon(qta.icon("mdi6.window-restore", color=ICONS_COLOR))

    # -------------------------------------------------- جابه‌جایی با ماوس

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            # اگر پنجره maximize بود، قبل از drag آن را به حالت normal برگردان
            if self._window.isMaximized():
                self.toggle_maximize()
                # موقعیت drag را متناسب با اندازه‌ی جدید بازتنظیم کن
                self._drag_pos = event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
            self._window.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos = None
        event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_maximize()
            event.accept()
