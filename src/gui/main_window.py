from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QFrame,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
)

from .widgets import (
    TitleBar,
    FramelessResizeMixin,
    SidebarPanel,
    PreviewPanel,
    InspectorPanel,
    QueuePanel
)


class MainWindow(FramelessResizeMixin, QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ziro.ai")
        self.resize(1280, 720)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        # =====================================================
        # Stage
        # =====================================================

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # -------- Title Bar --------
        self.title_bar = TitleBar(self)
        root_layout.addWidget(self.title_bar)

        # =====================================================
        # Main Area
        # =====================================================

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(8)
        root_layout.addWidget(content)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ---------- Left ----------
        sidebar = SidebarPanel("Files", 260, 360)
        splitter.addWidget(sidebar)

        # ---------- Center ----------
        preview = PreviewPanel("Preview")
        splitter.addWidget(preview)

        # ---------- Right ----------
        inspector = InspectorPanel("Properties", 320, 420)
        splitter.addWidget(inspector)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)

        content_layout.addWidget(splitter)

        # =====================================================
        # Bottom Queue
        # =====================================================

        queue = QueuePanel("Queue / Progress")
        queue.setFixedHeight(160)

        content_layout.addWidget(queue)

        # =====================================================
        # Bottom Toolbar
        # =====================================================

        bottom = QFrame()
        bottom.setFixedHeight(50)

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
            QSplitter::handle {
                background: transparent;
            }
        """)
