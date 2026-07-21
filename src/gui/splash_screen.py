from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar


class SplashScreen(QWidget):
    def __init__(self, title: str, total_steps: int = 1):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.SplashScreen
        )
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedSize(420, 220)

        self.setObjectName("SplashScreen")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addStretch()

        self.title_label = QLabel(title)
        self.title_label.setObjectName("SplashTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("Preparing...")
        self.status_label.setObjectName("SplashStatus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("SplashProgress")
        self.progress_bar.setRange(0, total_steps)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)

        layout.addWidget(self.title_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addStretch()

        self._apply_style()

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            #SplashScreen {
                background-color: #060C06;
                border: 1px solid #2D2D2D;
                border-radius: 6px;
            }
            #SplashTitle {
                color: #F0F2F0;
                font-size: 22px;
                font-weight: 600;
                margin-bottom: 14px;
            }
            #SplashStatus {
                color: #9A9A9A;
                font-size: 12px;
            }
            #SplashProgress {
                background-color: #2D2D2D;
                border: none;
                border-radius: 2px;
            }
            #SplashProgress::chunk {
                background-color: #54C750;
                border-radius: 2px;
            }
            """
        )

    def center_on_screen(self, screen_geometry) -> None:
        self.move(
            screen_geometry.center().x() - self.width() // 2,
            screen_geometry.center().y() - self.height() // 2,
        )

    def set_progress(self, value: int, message: str) -> None:
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
