from PyQt5 import QtWidgets, QtCore

from view.SmPageWindow import SmPageWindow
from view.SmSearchWindow import SmSearchWindow
from view.SmVizWindow import SmVizWindow


class SmWindows(SmPageWindow):
    """
    Pyqt Main Window helper to allow multipage
    """
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.resize(600, 300)
        # self.showMaximized()
        self.model = model
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.m_pages = {}

        # self.register(SmLoginWindow(), "login")
        self.register(SmSearchWindow(self.model), "search")
        self.register(SmVizWindow(self.model), "viz")

        self.goto("search")

    def register(self, widget, name):
        self.m_pages[name] = widget
        self.stacked_widget.addWidget(widget)
        if isinstance(widget, SmPageWindow):
            widget.gotoSignal.connect(self.goto)

    @QtCore.pyqtSlot(str)
    def goto(self, name):
        if name in self.m_pages:
            widget = self.m_pages[name]
            if self.model.reload_ui: widget.show_ui()
            self.model.reload_ui = True
            self.stacked_widget.setCurrentWidget(widget)
            self.setWindowTitle(widget.windowTitle())
