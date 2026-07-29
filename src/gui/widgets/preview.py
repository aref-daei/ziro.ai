from __future__ import annotations

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


def _format_ms(ms: int) -> str:
    """Format a millisecond duration as mm:ss for the time label."""
    total_seconds = max(ms, 0) // 1000
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"


class PreviewPanel(Panel):
    def __init__(self, title: str, min_width: int = None, max_width: int = None):
        Panel.__init__(self, min_width, max_width)

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
        self.play_btn.setEnabled(False)
        self._set_play_icon(playing=False)

        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setObjectName("PreviewSlider")
        self.position_slider.setRange(0, 0)
        self.position_slider.setEnabled(False)
        self.position_slider.sliderMoved.connect(self.player.setPosition)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setObjectName("PreviewTimeLabel")

        controls_row.addWidget(self.play_btn)
        controls_row.addWidget(self.position_slider, 1)
        controls_row.addWidget(self.time_label)

        layout.addLayout(controls_row)

    # ------------------------------------------------------------ public API

    def load_video(self, file_path: str) -> None:
        self.empty_label.hide()
        self.video_widget.show()

        self.player.setSource(QUrl.fromLocalFile(file_path))
        self.play_btn.setEnabled(True)
        self.position_slider.setEnabled(True)

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
        if not self.position_slider.isSliderDown():
            self.position_slider.setValue(position)
        self._update_time_label(position, self.player.duration())

    def _on_duration_changed(self, duration: int) -> None:
        self.position_slider.setRange(0, duration)
        self._update_time_label(self.player.position(), duration)

    def _update_time_label(self, position: int, duration: int) -> None:
        self.time_label.setText(f"{_format_ms(position)} / {_format_ms(duration)}")
