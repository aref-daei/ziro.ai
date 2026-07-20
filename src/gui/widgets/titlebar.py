from __future__ import annotations

from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QFrame, QWidget, QSizePolicy


class TitleBar(QFrame):

    theme_toggle_requested = Signal()

    def __init__(self, window: QWidget, title: str = "Ziro", parent: QWidget | None = None):
        super().__init__(parent)

        self._window = window
        self._drag_pos: QPoint | None = None

        self.setObjectName("TitleBar")
        self.setFixedHeight(42)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._build_ui(title)
        self._apply_styles()

    # ------------------------------------------------------------------ UI

    def _build_ui(self, title: str) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(8)

        self.logo_label = QLabel("Z")
        self.logo_label.setObjectName("LogoLabel")

        self.title_label = QLabel(title)
        self.title_label.setObjectName("TitleLabel")

        self.theme_btn = QPushButton("Theme")
        self.theme_btn.setObjectName("ThemeButton")

        self.min_btn = QPushButton("─")
        self.min_btn.setObjectName("MinButton")

        self.max_btn = QPushButton("□")
        self.max_btn.setObjectName("MaxButton")

        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("CloseButton")

        for btn in (self.theme_btn, self.min_btn, self.max_btn, self.close_btn):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # دکمه‌های کنترل پنجره اندازه ثابت دارند، دکمه‌ی تم می‌تواند متن‌محور بماند
        for btn in (self.min_btn, self.max_btn, self.close_btn):
            btn.setFixedSize(40, 32)

        self.theme_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.min_btn.clicked.connect(self._window.showMinimized)
        self.max_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self._window.close)
        self.theme_btn.clicked.connect(self.theme_toggle_requested.emit)

        layout.addWidget(self.logo_label)
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.theme_btn)
        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            #TitleBar {
                background-color: #1e1e1e;
                border-bottom: 1px solid #2d2d2d;
            }
            #LogoLabel {
                color: #ffffff;
                font-weight: bold;
                font-size: 16px;
                padding-right: 4px;
            }
            #TitleLabel {
                color: #d4d4d4;
                font-size: 13px;
            }
            QPushButton {
                background: transparent;
                border: none;
                color: #d4d4d4;
                font-size: 13px;
            }
            #ThemeButton {
                padding: 4px 10px;
                border-radius: 4px;
            }
            #ThemeButton:hover {
                background-color: #3a3a3a;
            }
            #MinButton:hover, #MaxButton:hover {
                background-color: #3a3a3a;
            }
            #CloseButton:hover {
                background-color: #e81123;
                color: #ffffff;
            }
            """
        )

    # ------------------------------------------------------------- رفتار

    def toggle_maximize(self) -> None:
        """بین حالت maximize و normal جابه‌جا می‌شود و آیکن دکمه را به‌روزرسانی می‌کند."""
        if self._window.isMaximized():
            self._window.showNormal()
            self.max_btn.setText("□")
        else:
            self._window.showMaximized()
            self.max_btn.setText("❐")

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

