from PySide6.QtWidgets import QFrame


class Panel(QFrame):
    def __init__(self, title: str, min_width: int = None, max_width: int = None):
        super().__init__()

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("panel")

        if min_width is not None:
            self.setMinimumWidth(min_width)
        if max_width is not None:
            self.setMaximumWidth(max_width)
