from PySide6.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QPushButton

from .panel import Panel


class SidebarPanel(Panel):
    def __init__(self, title: str, min_width: int = None, max_width: int = None):
        Panel.__init__(self, title, min_width, max_width)

        layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("panelTitle")
        add_button = QPushButton("Add")
        add_button.setObjectName("addButton")

        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(add_button)
        layout.addLayout(top_layout)
        layout.addStretch()
