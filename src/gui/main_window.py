from pathlib import Path

from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QSplitter, QMessageBox,
)

from src.core.app_checker import AppChecker
from src.core.app_config import AppConfig
from src.core.paths import PATHS
from src.workers.processing_worker import ProcessingWorker
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
    process_started = Signal()
    process_finished = Signal()

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
        inspector = InspectorPanel(self, "Properties", 320, 420)
        splitter.addWidget(inspector)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)

        content_layout.addWidget(splitter)

        # =====================================================
        # Queue / Progress
        # =====================================================

        self.queue = QueuePanel("Queue / Progress")
        self.queue.setFixedHeight(160)

        content_layout.addWidget(self.queue)

        # =====================================================
        # Bottom Toolbar
        # =====================================================

        self.bottom = BottomBar(self)

        content_layout.addWidget(self.bottom)

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

        self.app_checker.internet_checked.connect(self._on_internet_checked)
        self.app_checker.ffmpeg_checked.connect(self._on_ffmpeg_checked)

        sidebar.file_selected.connect(preview.load_video)

        inspector.start_processing.connect(
            lambda app_config: self._on_start_processing(app_config, sidebar.selected_files())
        )

        self.worker = None
        self.bottom.stop_requested.connect(self._on_stop_requested)

        # Notification ========================================
        self.is_there_problems = (False, "")
        self.app_checker.check_for_ffmpeg()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.app_checker.check_for_internet)
        self.timer.start(1000)

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
        if not found:
            self.notification.emit("FFmpeg not found")
            self.is_there_problems = (True, "FFmpeg not found")

    def _on_internet_checked(self, has_access: bool) -> None:
        if not has_access:
            self.notification.emit("No internet access")
            self.is_there_problems = (True, "No internet access")
        else:
            if "FFmpeg" not in self.is_there_problems[1]:
                self.notification.emit("")
                self.is_there_problems = (False, "")

    def _on_stop_requested(self) -> None:
        if self.worker is not None:
            self.worker.request_stop()

    def _on_start_processing(self, config: AppConfig, selected_files: list[str]) -> None:
        if self.is_there_problems[0]:
            QMessageBox.information(self, "There is a Problem!", self.is_there_problems[1] + ".")
            return

        self.thread = QThread()
        self.worker = ProcessingWorker(config, selected_files)
        self.worker.moveToThread(self.thread)

        self.queue.start_queue(selected_files)

        self.thread.started.connect(self.worker.run)

        self.worker.process_started.connect(lambda: self.process_started.emit())
        self.worker.status.connect(lambda video_path, status: self.queue.set_status(video_path, status))
        self.worker.progress.connect(lambda video_path, progress: self.queue.set_progress(video_path, progress))
        self.worker.process_finished.connect(lambda: self.process_finished.emit())

        self.worker.process_finished.connect(self.thread.quit)
        self.worker.process_finished.connect(self.worker.deleteLater)
        self.worker.process_finished.connect(self._on_worker_finished)

        self.worker.process_finished.connect(self.thread.deleteLater)

        self.thread.start()

    def _on_worker_finished(self) -> None:
        self.worker = None
