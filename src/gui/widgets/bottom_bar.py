from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton


class BottomBar(QFrame):
    def __init__(self):
        super().__init__()

        self.setFixedHeight(50)

        bottom_layout = QHBoxLayout(self)

        self.start_btn = QPushButton("Start")
        self.start_btn.setObjectName("Start")

        self.output_btn = QPushButton("Open Output")
        self.output_btn.setObjectName("OpenOutput")

        self.logs_btn = QPushButton("Logs")
        self.logs_btn.setObjectName("Logs")

        bottom_layout.addWidget(self.start_btn)
        bottom_layout.addWidget(self.output_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.logs_btn)
