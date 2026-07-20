from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QSizePolicy,
)
from gui.widgets import TitleBar, FramelessResizeMixin


class Panel(QFrame):
    def __init__(self, title: str):
        super().__init__()

        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("panel")

        layout = QVBoxLayout(self)

        title_label = QLabel(title)
        title_label.setObjectName("panelTitle")

        layout.addWidget(title_label)
        layout.addStretch()


class MainWindow(FramelessResizeMixin, QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ziro.ai")
        self.resize(1270, 720)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.title_bar = TitleBar(self)
        root_layout.addWidget(self.title_bar)

        # محتوای اصلی در یک ویجت جدا با margin دلخواه
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(8)
        root_layout.addWidget(content)

        # =====================================================
        # Toolbar
        # =====================================================

        # toolbar = QFrame()
        # toolbar.setFixedHeight(52)

        # toolbar_layout = QHBoxLayout(toolbar)

        # toolbar_layout.addWidget(QPushButton("Open"))
        # toolbar_layout.addWidget(QPushButton("Add Files"))
        # toolbar_layout.addWidget(QPushButton("Clear Queue"))

        # toolbar_layout.addStretch()

        # toolbar_layout.addWidget(QPushButton("Settings"))

        # content_layout.addWidget(toolbar)

        # =====================================================
        # Main Area
        # =====================================================

        splitter = QSplitter(Qt.Horizontal)

        # ---------- Left ----------
        sidebar = Panel("Files")

        sidebar.setMinimumWidth(260)
        sidebar.setMaximumWidth(350)

        # ---------- Center ----------
        center = Panel("Preview")

        # ---------- Right ----------
        inspector = Panel("Properties")

        inspector.setMinimumWidth(320)
        inspector.setMaximumWidth(420)

        splitter.addWidget(sidebar)
        splitter.addWidget(center)
        splitter.addWidget(inspector)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)

        content_layout.addWidget(splitter)

        # =====================================================
        # Bottom Queue
        # =====================================================

        queue = Panel("Queue / Progress")
        queue.setFixedHeight(180)

        content_layout.addWidget(queue)

        # =====================================================
        # Bottom Toolbar
        # =====================================================

        bottom = QFrame()
        bottom.setFixedHeight(55)

        bottom_layout = QHBoxLayout(bottom)

        bottom_layout.addWidget(QPushButton("Convert"))
        bottom_layout.addWidget(QPushButton("Stop"))
        bottom_layout.addWidget(QPushButton("Open Output"))

        bottom_layout.addStretch()

        bottom_layout.addWidget(QPushButton("Logs"))

        content_layout.addWidget(bottom)

        self.apply_style()

        self.enable_frameless_resize()

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background: #202124;
            }

            QFrame#panel {
                background: #2b2d31;
                border: 1px solid #3b3d42;
                border-radius: 8px;
            }

            QLabel#panelTitle {
                color: white;
                font-size: 15px;
                font-weight: bold;
            }

            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }

            QPushButton:hover {
                background: #4f8ef7;
            }
        """)


"""
┌─────────────────────────────────────────────────────────────────────┐
│ Toolbar                                                     ⚙ Theme │
├───────────────┬──────────────────────────────┬──────────────────────┤
│               │                              │                      │
│   Sidebar     │          Preview             │      Inspector       │
│   Files       │                              │   Whisper Model      │
│   Queue       │                              │   Device             │
│               │                              │   Languages          │
├───────────────┴──────────────────────────────┴──────────────────────┤
│ Queue / Progress                                                75% │
├─────────────────────────────────────────────────────────────────────┤
│ Convert      Stop      Open Output      Logs                        │
└─────────────────────────────────────────────────────────────────────┘
"""
