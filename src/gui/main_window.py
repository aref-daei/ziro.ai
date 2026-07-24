from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QSplitter,
)

from src.core.paths import PATHS
from .widgets import (
    TitleBar,
    FramelessResizeMixin,
    SidebarPanel,
    PreviewPanel,
    InspectorPanel,
    QueuePanel,
    BottomBar
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

        # ------------------------------------------- Title Bar
        title_bar = TitleBar(self)
        root_layout.addWidget(title_bar)

        # title_bar.open_file_requested.connect(lambda paths: [sidebar._add_file(p) for p in paths])
        # title_bar.open_folder_requested.connect(lambda folder: ...)  # اسکن پوشه برای ویدیوها
        # title_bar.check_updates_requested.connect(Checker.is_update_available())

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
        # Queue / Progress
        # =====================================================

        queue = QueuePanel("Queue / Progress")
        queue.setFixedHeight(160)

        content_layout.addWidget(queue)

        # =====================================================
        # Bottom Toolbar
        # =====================================================

        bottom = BottomBar()

        content_layout.addWidget(bottom)

        # =====================================================
        # Connects
        # =====================================================

        sidebar.file_selected.connect(preview.load_video)

        inspector.start_processing.connect(
            lambda app_config: queue.start_queue(sidebar.selected_files())
        )

        # =====================================================
        # Apply StyleCheat & Frameless Resize
        # =====================================================

        self._apply_theme()
        self.enable_frameless_resize()

    def _apply_theme(self, theme: str = "dark") -> None:
        theme_dir = PATHS["styles"] / theme
        if not theme_dir.exists():
            return

        style_sheets = []
        for stylesheet_path in theme_dir.glob("*.qss"):
            with open(stylesheet_path, encoding="utf-8") as f:
                style_sheets.append(f.read())

        if style_sheets:
            self.setStyleSheet("\n".join(style_sheets))

    def center_on_screen(self, screen_geometry) -> None:
        self.move(
            screen_geometry.center().x() - self.width() // 2,
            screen_geometry.center().y() - self.height() // 2,
        )
