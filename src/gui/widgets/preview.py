from __future__ import annotations

import os
import sys
from contextlib import contextmanager

import qtawesome as qta
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSizePolicy,
)

from .panel import Panel


@contextmanager
def _suppress_native_stderr():
    """Temporarily redirect the process's real stderr (file descriptor 2)
    to devnull.

    Needed specifically because the FFmpeg backend behind QMediaPlayer calls
    av_dump_format(), which writes straight to the OS-level stderr fd -
    bypassing sys.stderr and Qt's own logging system entirely. Nothing short
    of a raw fd redirect can silence it.
    """
    stderr_fd = sys.stderr.fileno()
    saved_fd = os.dup(stderr_fd)
    devnull_fd = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(devnull_fd, stderr_fd)
        yield
    finally:
        os.dup2(saved_fd, stderr_fd)
        os.close(devnull_fd)
        os.close(saved_fd)


def _format_ms(ms: int) -> str:
    """Format a millisecond duration as mm:ss for the time label."""
    total_seconds = max(ms, 0) // 1000
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"


class PreviewPanel(Panel):
    def __init__(self, title: str, min_width: int = None, max_width: int = None):
        Panel.__init__(self, title, min_width, max_width)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("PanelTitle")
        layout.addWidget(title_label)

        # -------- Video surface --------
        self.video_widget = QVideoWidget()
        self.video_widget.setObjectName("PreviewVideoWidget")
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_widget.hide()  # hidden until a video is actually loaded
        layout.addWidget(self.video_widget, 1)

        # Placeholder shown before any video has been picked in the sidebar
        self.empty_label = QLabel("Select a video from the list to preview it")
        self.empty_label.setObjectName("PreviewEmptyLabel")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.empty_label, 1)

        # -------- Media player backend --------
        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)

        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_playback_state_changed)

        # -------- Controls row: play/pause, seek slider, time label --------
        controls_row = QHBoxLayout()
        controls_row.setSpacing(10)

        self.play_btn = QPushButton()
        self.play_btn.setObjectName("PreviewPlayButton")
        self.play_btn.setFixedSize(32, 32)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.clicked.connect(self._toggle_playback)
        self._set_play_icon(playing=False)

        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setObjectName("PreviewSlider")
        self.position_slider.setRange(0, 0)
        # setPosition only on release/drag, not continuously, to avoid fighting playback
        self.position_slider.sliderMoved.connect(self.player.setPosition)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setObjectName("PreviewTimeLabel")

        controls_row.addWidget(self.play_btn)
        controls_row.addWidget(self.position_slider, 1)
        controls_row.addWidget(self.time_label)

        layout.addLayout(controls_row)

    # ------------------------------------------------------------ public API

    def load_video(self, file_path: str) -> None:
        """Load the given file and start playing it. Meant to be connected
        to SidebarPanel.file_selected."""
        self.empty_label.hide()
        self.video_widget.show()

        with _suppress_native_stderr():
            self.player.setSource(QUrl.fromLocalFile(file_path))
            self.player.play()

    # ------------------------------------------------------------ playback control

    def _toggle_playback(self) -> None:
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def _on_playback_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        self._set_play_icon(playing=state == QMediaPlayer.PlaybackState.PlayingState)

    def _set_play_icon(self, playing: bool) -> None:
        icon_name = "mdi6.pause" if playing else "mdi6.play"
        self.play_btn.setIcon(qta.icon(icon_name, color="#f0f2f0"))

    # ------------------------------------------------------------ slider/time sync

    def _on_position_changed(self, position: int) -> None:
        # Don't override the slider's value while the user is dragging it themselves
        if not self.position_slider.isSliderDown():
            self.position_slider.setValue(position)
        self._update_time_label(position, self.player.duration())

    def _on_duration_changed(self, duration: int) -> None:
        self.position_slider.setRange(0, duration)
        self._update_time_label(self.player.position(), duration)

    def _update_time_label(self, position: int, duration: int) -> None:
        self.time_label.setText(f"{_format_ms(position)} / {_format_ms(duration)}")
