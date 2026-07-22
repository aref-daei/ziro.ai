from __future__ import annotations

import qtawesome as qta
from PySide6.QtCore import Qt
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

from .panel import Panel

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
    def __init__(self, title: str, min_width: int = None, max_width: int = None):
        Panel.__init__(self, title, min_width, max_width)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("panelTitle")
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

        self._apply_style()

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

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            #InspectorRow {
                background-color: #3E3F3E;
                border-radius: 10px;
            }
            #InspectorLabel, #InspectorCheckboxLabel {
                color: #dddddd;
                font-size: 13px;
            }
            #InspectorArrow {
                color: #888888;
                font-size: 14px;
            }
            #InspectorPillCombo {
                background-color: #f0f2f0;
                color: #3E3F3E;
                border: none;
                border-radius: 12px;
                padding: 6px 14px;
                font-size: 13px;
            }
            #InspectorPillCombo::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right;
                width: 28px;
                border-top-right-radius: 12px;
                border-bottom-right-radius: 12px;
                background-color: #54C750;
            }
            #InspectorPillCombo::down-arrow {
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 6px;
            }
            #InspectorPillCombo QAbstractItemView {
                background-color: #2a2a2a;
                color: #eeeeee;
                selection-background-color: #2ecc71;
                border: 1px solid #3a3a3a;
                outline: none;
            }
            #InspectorKeyInput {
                background-color: #F0F2F0;
                color: #1e1e1e;
                border: none;
                border-radius: 8px;
                padding: 6px 10px;
                min-width: 120px;
            }
            #InspectorCheckbox {
                background-color: transparent;
                border: 2px solid #54C750;
                border-radius: 6px;
            }
            #InspectorCheckbox:checked {
                background-color: #54C750;
                border: none;
            }
            """
        )
