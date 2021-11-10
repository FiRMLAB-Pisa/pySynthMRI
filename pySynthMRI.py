# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 10:01:10 2021

@author: Luca
"""
import sys

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication

from model.SmModel import SmModel
from view.SmWindows import SmWindows

if __name__ == '__main__':
    # Create an instance of QApplication
    app = QApplication(sys.argv)
    # dark style
    # Force the style to be the same on all OSs:
    app.setStyle("Fusion")

    palette = QPalette()
    # palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.Window, QColor("black"))
    palette.setColor(QPalette.WindowText, QColor(170, 172, 191))
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColor("black"))
    palette.setColor(QPalette.ToolTipText, QColor(170, 172, 191))
    palette.setColor(QPalette.Text, QColor(170, 172, 191))
    # palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.Button, QColor(224, 224, 224))
    palette.setColor(QPalette.Disabled, QPalette.Button, QColor("#1F1B24"))
    # palette.setColor(QPalette.Disabled, QPalette.Button, QColor("white"))
    # palette.setColor(QPalette.ButtonText, QColor("white"))
    palette.setColor(QPalette.ButtonText, QColor("black"))
    palette.setColor(QPalette.BrightText, QColor("red"))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor("black"))
    app.setPalette(palette)

    model = SmModel(app)
    # controller = SmController()
    view = SmWindows(model)

    model.view = view
    # controller.view = view
    # controller.model = model

    view.show()

    # Execute calculator's main loop
    sys.exit(app.exec_())

    app.exec_()