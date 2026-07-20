from PySide6.QtWidgets import QVBoxLayout, QLabel

from .panel import Panel


class QueuePanel(Panel):
    def __init__(self, title: str, min_width: int = None, max_width: int = None):
        Panel.__init__(self, title, min_width, max_width)

        layout = QVBoxLayout(self)

        title_label = QLabel(title)
        title_label.setObjectName("panelTitle")

        layout.addWidget(title_label)
        layout.addStretch()
