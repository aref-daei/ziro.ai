from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QSplitter, QMessageBox,
)

from src.core.app_checker import AppChecker
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
    notification = Signal(str)

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

        # =====================================================
        # Title Bar
        # =====================================================

        title_bar = TitleBar(self)
        root_layout.addWidget(title_bar)

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

        self.app_checker = AppChecker()

        title_bar.open_file_requested.connect(lambda paths: [sidebar.add_file(p) for p in paths])

        VIDEO_EXTENSIONS = (".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".wmv")
        title_bar.open_folder_requested.connect(
            lambda folder: [sidebar.add_file(str(p))
                            for p in Path(folder).iterdir()
                            if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS]
        )

        title_bar.check_updates_requested.connect(self.app_checker.check_for_update)
        self.app_checker.update_checked.connect(self._on_update_checked)

        self.app_checker.ffmpeg_checked.connect(self._on_ffmpeg_checked)
        self.app_checker.exists_ffmpeg()

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

    def _on_update_checked(self, has_update: bool) -> None:
        if has_update:
            QMessageBox.information(self, "Update Available", "A new version is available!")
        else:
            QMessageBox.information(self, "No Update Available", "No update available.")

    def _on_ffmpeg_checked(self, found: bool) -> None:
        if found:
            self.notification.emit("FFmpeg not found!")
