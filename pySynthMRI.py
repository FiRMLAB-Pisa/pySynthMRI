# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 10:01:10 2021

@author: Luca
"""
import sys
import logging

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication

from controller.psCanvasController import PsCanvasController
from controller.psController import PsController
from model.psModel import PsModel
from view.psMainWindow import PsMainWindow

DEBUG = False

logging.basicConfig(level=logging.DEBUG)

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
    palette.setColor(QPalette.Disabled, QPalette.Button, QColor("#1F1B24")) #Very dark (mostly black) violet.
    # palette.setColor(QPalette.Disabled, QPalette.Button, QColor("white"))
    # palette.setColor(QPalette.ButtonText, QColor("white"))
    palette.setColor(QPalette.ButtonText, QColor("black"))
    palette.setColor(QPalette.BrightText, QColor("red"))
    palette.setColor(QPalette.Link, QColor("red")) # QColor(42, 130, 218)
    palette.setColor(QPalette.Highlight, QColor("red")) # QColor(42, 130, 218)
    palette.setColor(QPalette.HighlightedText, QColor("black"))
    app.setPalette(palette)

    model = PsModel(app)

    view = PsMainWindow(model)
    general_controller = PsController(model, view)
    canvas_controller = PsCanvasController(model, view)  ## TODO rimettere
    view.showMaximized()
    if DEBUG:
        model.update_qmap_path("T1", 'C:/Users/Luca/OneDrive - University of Pisa/dicom_mrf_example/newTree/niftii/T1_subMRF3D007_ex12724_qmap_T1.nii', "niftii")
        model.update_qmap_path("T2", 'C:/Users/Luca/OneDrive - University of Pisa/dicom_mrf_example/newTree/niftii/T2_subMRF3D007_ex12724_qmap_T2.nii', "niftii")
        model.update_qmap_path("PD", 'C:/Users/Luca/OneDrive - University of Pisa/dicom_mrf_example/newTree/niftii/PD_subMRF3D007_ex12724_qmap_pd.nii', "niftii")

        # model.update_qmap_path("T1", "C:/Users/Luca/OneDrive - University of Pisa/dicom_mrf_example/newTree/T1", "dicom")
        # model.update_qmap_path("T2", "C:/Users/Luca/OneDrive - University of Pisa/dicom_mrf_example/newTree/T2", "dicom")
        # model.update_qmap_path("PD", "C:/Users/Luca/OneDrive - University of Pisa/dicom_mrf_example/newTree/PD", "dicom")

        view.tool_bar.synth_images_buttons["GRE"].clicked.emit()
        view.tool_bar.synth_images_buttons["GRE"].setChecked(True)
    sys.exit(app.exec_())

    app.exec_()
