from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton


class BottomBar(QFrame):
    def __init__(self):
        super().__init__()

        self.setFixedHeight(50)

        bottom_layout = QHBoxLayout(self)

        bottom_layout.addWidget(QPushButton("Convert"))
        bottom_layout.addWidget(QPushButton("Stop"))
        bottom_layout.addWidget(QPushButton("Open Output"))

        bottom_layout.addStretch()

        bottom_layout.addWidget(QPushButton("Logs"))
