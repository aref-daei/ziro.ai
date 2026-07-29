from __future__ import annotations

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication, QWidget


class FramelessResizeMixin:

    _RESIZE_BORDER = 6

    _CURSOR_MAP = {
        Qt.Edge.LeftEdge: Qt.CursorShape.SizeHorCursor,
        Qt.Edge.RightEdge: Qt.CursorShape.SizeHorCursor,
        Qt.Edge.TopEdge: Qt.CursorShape.SizeVerCursor,
        Qt.Edge.BottomEdge: Qt.CursorShape.SizeVerCursor,
        Qt.Edge.LeftEdge | Qt.Edge.TopEdge: Qt.CursorShape.SizeFDiagCursor,
        Qt.Edge.RightEdge | Qt.Edge.BottomEdge: Qt.CursorShape.SizeFDiagCursor,
        Qt.Edge.RightEdge | Qt.Edge.TopEdge: Qt.CursorShape.SizeBDiagCursor,
        Qt.Edge.LeftEdge | Qt.Edge.BottomEdge: Qt.CursorShape.SizeBDiagCursor,
    }

    def enable_frameless_resize(self) -> None:
        QApplication.instance().installEventFilter(self)
        self._enable_mouse_tracking_recursive(self)

    # -------------------------------------------------------------- Auxiliary

    @staticmethod
    def _enable_mouse_tracking_recursive(widget: QWidget) -> None:
        widget.setMouseTracking(True)
        for child in widget.findChildren(QWidget):
            child.setMouseTracking(True)

    def _edge_at_cursor(self) -> Qt.Edge | None:
        pos = self.mapFromGlobal(QCursor.pos())
        rect = self.rect()
        b = self._RESIZE_BORDER

        left = pos.x() <= b
        right = pos.x() >= rect.width() - b
        top = pos.y() <= b
        bottom = pos.y() >= rect.height() - b

        if not (left or right or top or bottom):
            return None

        edges = Qt.Edge(0)
        if left:
            edges |= Qt.Edge.LeftEdge
        if right:
            edges |= Qt.Edge.RightEdge
        if top:
            edges |= Qt.Edge.TopEdge
        if bottom:
            edges |= Qt.Edge.BottomEdge
        return edges

    def _update_resize_cursor(self) -> None:
        if self.isMaximized() or self.isFullScreen():
            self.unsetCursor()
            return

        edges = self._edge_at_cursor()
        if edges is None:
            self.unsetCursor()
            return

        self.setCursor(self._CURSOR_MAP.get(edges, Qt.CursorShape.ArrowCursor))

    def _try_start_resize(self) -> bool:
        if self.isMaximized() or self.isFullScreen():
            return False

        edges = self._edge_at_cursor()
        if edges is None:
            return False

        window_handle = self.windowHandle()
        if window_handle is None:
            return False

        return window_handle.startSystemResize(edges)

    # -------------------------------------------------------- event filter

    def eventFilter(self, watched, event) -> bool:
        if self.isActiveWindow():
            if event.type() == QEvent.Type.MouseMove:
                self._update_resize_cursor()
            elif event.type() == QEvent.Type.MouseButtonPress:
                if self._try_start_resize():
                    return True
        return super().eventFilter(watched, event)
