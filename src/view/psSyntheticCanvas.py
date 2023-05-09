import logging

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QKeyEvent, QFocusEvent
from PyQt5.QtWidgets import QLabel, QSizePolicy

log = logging.getLogger(__name__)


class CanvasCommunicate(QObject):
    mouse_wheel_sgn = pyqtSignal(QWheelEvent)
    mouse_press_sgn = pyqtSignal(QMouseEvent)
    mouse_release_sgn = pyqtSignal(QMouseEvent)
    mouse_move_sgn = pyqtSignal(QMouseEvent)
    keyboard_pressed_sgn = pyqtSignal(QKeyEvent)
    keyboard_released_sgn = pyqtSignal(QKeyEvent)
    focus_in_sgn = pyqtSignal(QFocusEvent)
    focus_out_sgn = pyqtSignal(QFocusEvent)



class PsSyntheticCanvas(QLabel):
    """QLabel for displaying image"""

    def __init__(self, model, parent=None):
        super().__init__()
        self.model = model
        self._parent = parent
        self.c = CanvasCommunicate()

        sp = self.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Expanding)
        sp.setVerticalPolicy(QSizePolicy.Expanding)
        # sp.setHorizontalStretch(1)
        self.setMinimumSize(100, 100)
        self.setSizePolicy(sp)

        self.setContentsMargins(0, 0, 0, 0)

    # event override
    def wheelEvent(self, event):
        """Override built-in event"""
        self.c.mouse_wheel_sgn.emit(event)

    def mousePressEvent(self, event):
        """Override built-in event"""
        self.c.mouse_press_sgn.emit(event)
        return super(PsSyntheticCanvas, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Override built-in event"""
        self.c.mouse_release_sgn.emit(event)
        return super(PsSyntheticCanvas, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """Override built-in event"""
        self.c.mouse_move_sgn.emit(event)
        return super(PsSyntheticCanvas, self).mouseMoveEvent(event)

    def keyPressEvent(self, event):
        """Override built-in event"""
        super(PsSyntheticCanvas, self).keyPressEvent(event)
        self.c.keyboard_pressed_sgn.emit(event)

    def keyReleaseEvent(self, event):
        """Override built-in event"""
        super(PsSyntheticCanvas, self).keyReleaseEvent(event)
        self.c.keyboard_released_sgn.emit(event)

    def focusInEvent(self, event):
        """Override built-in event"""
        super(PsSyntheticCanvas, self).focusInEvent(event)
        self.c.focus_in_sgn.emit(event)
        # self.setStyleSheet("border: 1px solid red;")

    def focusOutEvent(self, event):
        """Override built-in event"""
        super(PsSyntheticCanvas, self).focusOutEvent(event)
        self.c.focus_out_sgn.emit(event)
        # self.setStyleSheet("")
