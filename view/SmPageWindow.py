# -*- coding: utf-8 -*-

import PyQt5.QtCore
import PyQt5


class SmPageWindow(PyQt5.QtWidgets.QMainWindow):
    gotoSignal = PyQt5.QtCore.pyqtSignal(str)

    def goto(self, name):
        self.gotoSignal.emit(name)
