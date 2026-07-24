from __future__ import annotations

import qtawesome as qta
import torch
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QComboBox,
    QLineEdit,
    QPushButton,
    QSizePolicy,
)

from src.core.app_config import AppConfig
from .panel import Panel

# LANGUAGES: dict {"Language": ("lang_code", is_rtl: True/False)}
LANGUAGES = {
    "Persian": ("fa", True),
    "English": ("en", False),
    "French": ("fr", False),
    "Chinese": ("zh", False),
    "Hindi": ("hi", False),
    "Spanish": ("es", False),
    "Arabic": ("ar", True),
    "Bengali": ("bn", False),
    "Portuguese": ("pt", False),
    "Russian": ("ru", False),
    "Japanese": ("ja", False)
}


class InspectorPanel(Panel):
    start_processing = Signal(AppConfig)

    def __init__(self, title: str, min_width: int = None, max_width: int = None):
        Panel.__init__(self, title, min_width, max_width)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("PanelTitle")
        layout.addWidget(title_label)

        # -------- Source/Destination Language Row --------
        lang_row = self._make_row()
        lang_row_layout = QHBoxLayout(lang_row)
        lang_row_layout.setContentsMargins(10, 8, 10, 8)
        lang_row_layout.setSpacing(10)

        self.source_lang_combo = self._make_pill_combo(["Auto"] + [*LANGUAGES])
        arrow_label = QLabel("→")
        arrow_label.setObjectName("InspectorArrow")
        arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.target_lang_combo = self._make_pill_combo([*LANGUAGES])

        lang_row_layout.addWidget(self.source_lang_combo, 1)
        lang_row_layout.addWidget(arrow_label)
        lang_row_layout.addWidget(self.target_lang_combo, 1)

        layout.addWidget(lang_row)

        # -------- Transcribe Accuracy --------
        self.accuracy_combo = self._make_pill_combo(["Tiny", "Base", "Small", "Medium", "Large"])
        layout.addWidget(
            self._make_label_row("Transcription accuracy:", self.accuracy_combo)
        )

        # -------- Translate Model --------
        self.translation_combo = self._make_pill_combo(["Google Translate", "DeepL"])
        layout.addWidget(
            self._make_label_row("Translation model:", self.translation_combo)
        )

        # -------- DeepL Key --------
        self.deepl_key_edit = QLineEdit()
        self.deepl_key_edit.setObjectName("InspectorKeyInput")
        self.deepl_key_edit.setPlaceholderText("XXXXXXXX-XXXX-XXXX-XXXX")
        self.deepl_key_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.deepl_key_row = self._make_label_row("Auth key for DeepL:", self.deepl_key_edit)
        layout.addWidget(self.deepl_key_row)

        self.translation_combo.currentTextChanged.connect(self._update_deepl_key_visibility)
        self._update_deepl_key_visibility(self.translation_combo.currentText())

        # -------- Add Subtitles Checkbox --------
        subtitle_row = self._make_row()
        subtitle_row_layout = QHBoxLayout(subtitle_row)
        subtitle_row_layout.setContentsMargins(10, 10, 10, 10)
        subtitle_row_layout.setSpacing(10)

        self.subtitle_toggle = QPushButton()
        self.subtitle_toggle.setObjectName("InspectorCheckbox")
        self.subtitle_toggle.setCheckable(True)
        self.subtitle_toggle.setChecked(True)
        self.subtitle_toggle.setFixedSize(24, 24)
        self.subtitle_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.subtitle_toggle.toggled.connect(self._update_checkbox_icon)
        self._update_checkbox_icon(self.subtitle_toggle.isChecked())

        subtitle_label = QLabel("Add subtitles to video")
        subtitle_label.setObjectName("InspectorCheckboxLabel")

        subtitle_row_layout.addStretch()
        subtitle_row_layout.addWidget(self.subtitle_toggle)
        subtitle_row_layout.addWidget(subtitle_label)
        subtitle_row_layout.addStretch()

        layout.addWidget(subtitle_row)

        layout.addStretch()

        # -------- Start Button --------
        self.start_button = QPushButton("Start Processing")
        self.start_button.setObjectName("InspectorStartButton")
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.setFixedHeight(42)
        layout.addWidget(self.start_button)

        self.start_button.clicked.connect(self._on_start_clicked)

    def _make_row(self) -> QFrame:
        row = QFrame()
        row.setObjectName("InspectorRow")
        return row

    def _make_label_row(self, text: str, control: QComboBox | QLineEdit) -> QFrame:
        row = self._make_row()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(10, 8, 10, 8)
        row_layout.setSpacing(10)

        label = QLabel(text)
        label.setObjectName("InspectorLabel")

        row_layout.addWidget(label)
        row_layout.addStretch()
        row_layout.addWidget(control)
        return row

    def _make_pill_combo(self, items: list[str]) -> QComboBox:
        combo = QComboBox()
        combo.setObjectName("InspectorPillCombo")
        combo.addItems(items)
        combo.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        combo.setCursor(Qt.CursorShape.PointingHandCursor)
        return combo

    def _update_deepl_key_visibility(self, model_name: str) -> None:
        self.deepl_key_row.setVisible(model_name == "DeepL")

    def _update_checkbox_icon(self, checked: bool):
        if checked:
            self.subtitle_toggle.setIcon(
                qta.icon("mdi6.check-bold", color="#f0f2f0")
            )
        else:
            self.subtitle_toggle.setIcon(QIcon())

    def _on_start_clicked(self):
        app_config = AppConfig(
            LANGUAGES[self.source_lang_combo.currentText()]
            if self.source_lang_combo.currentText() != "Auto"
            else ("", False),
            LANGUAGES[self.target_lang_combo.currentText()],
            ("whisper", self.accuracy_combo.currentText().lower()),
            (
                self.translation_combo.currentText().lower().split()[0],
                self.deepl_key_edit.text(),
            ),
            "cuda" if torch.cuda.is_available() else "cpu",
            self.subtitle_toggle.isChecked(),
        )

        self.start_processing.emit(app_config)
