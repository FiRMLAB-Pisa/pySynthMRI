import functools

import cv2
import numpy as np
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QDropEvent, QCursor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QMenu, QAction

from model.MRIImage import Colormap


class QMapCommunicate(QObject):
    drop_event = pyqtSignal(QDropEvent)
    colormap_changed_signal = pyqtSignal(str)
    invert_relaxation_map_signal = pyqtSignal(bool)

class PsQMapWidget(QWidget):
    def __init__(self, qmap, model=None):
        super(PsQMapWidget, self).__init__()
        self.qmap = qmap
        self.model = model
        self.setAcceptDrops(True)
        self.c = QMapCommunicate()
        self.canvas = QLabel()
        # self.canvas.setMaximumSize(400, 400)
        sp = self.canvas.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Expanding)
        sp.setVerticalPolicy(QSizePolicy.Expanding)
        self.canvas.setSizePolicy(sp)
        self.setContentsMargins(0,0,0,0)
        self.canvas.setMinimumSize(20, 20)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        self.setLayout(vbox)

        # self.setStyleSheet("""
        #                         border: 1px solid red;
        #                         padding: 0px;
        #                         border-radius: 8px;
        #                         margin: 0px;
        #         """)
        # title
        self.image_info_label = QLabel(parent=self.canvas)
        self.image_info_label.setText(self.qmap.map_type) #background-color: rgba(31, 27, 36, .7);
        self.image_info_label.setStyleSheet("""
                                background-color: rgba(31, 27, 36, .7);
                                padding: 4px;
                                border-radius: 4px;
                                margin: 1px;
                                font-weight: bold;
                """)

    def get_affine_cv(self, scale_center, rot, scale, translate):
        sin_theta = np.sin(rot)
        cos_theta = np.cos(rot)

        a_11 = scale * cos_theta
        a_21 = -scale * sin_theta

        a_12 = scale * sin_theta
        a_22 = scale * cos_theta

        a_13 = scale_center.x() * (1 - scale * cos_theta) - scale * sin_theta * scale_center.x() + translate.x()
        a_23 = scale_center.y() * (1 - scale * cos_theta) + scale * sin_theta * scale_center.y() + translate.y()

        return np.array([[a_11, a_12, a_13],
                         [a_21, a_22, a_23]], dtype=float)

    def update(self):
        np_matrix_2d = self.qmap.get_matrix(dim=2)

        # typically initial resize
        if np_matrix_2d is None:
            return

        if self.qmap.get_inverted():
            np_matrix_2d = 1./np_matrix_2d
            np_matrix_2d[np_matrix_2d==np.inf] = 0
            np_matrix_2d = np_matrix_2d * 10000

        img_2d_cp = np_matrix_2d.astype(np.uint16)

        # scale over min max of all slices
        m_max = self.qmap.get_max_value()
        m_min = self.qmap.get_min_value()

        if self.qmap.get_inverted():
            m_max = np_matrix_2d.max()
            m_min = np_matrix_2d.min()

        cv_image = (255 * ((img_2d_cp - m_min) / (m_max - m_min))).astype(np.uint8)  # .copy()
        # scale over min max of single slice
        # cv_image = (255 * ((img_2d_cp - img_2d_cp.min()) / img_2d_cp.ptp())).astype(np.uint8)  # .copy()
        mask = cv_image == 0
        cv_colormap = self.get_cv_colormap(self.qmap.get_colormap())
        cv_image = cv2.applyColorMap(cv_image, cv_colormap) # COLORMAP_HOT
        cv_image[mask] = [0,0,0]
        cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB, cv_image)
        height, width, rgb = cv_image.shape
        q_img = QImage(cv_image.data, width, height, QImage.Format.Format_RGB888)

        q_pix_map = QPixmap(q_img)
        q_pix_map = q_pix_map.scaled(self.canvas.size(), Qt.KeepAspectRatio)
        self.canvas.setAlignment(Qt.AlignCenter)
        self.canvas.setPixmap(q_pix_map)

    def get_cv_colormap(self, colormap):
        if colormap == "HOT":
            return cv2.COLORMAP_HOT
        elif colormap == "WINTER":
            return cv2.COLORMAP_WINTER
        elif colormap == "BONE":
            return cv2.COLORMAP_BONE
        elif colormap == "JET":
            return cv2.COLORMAP_JET
        elif colormap == "HSV":
            return cv2.COLORMAP_HSV
        else:
            return cv2.COLORMAP_HOT

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        self.c.drop_event.emit(event)
        # text = event.mimeData().text()
        # print(text)

    def contextMenuEvent(self, event):

        context_menu = QMenu(self)
        colormap_menu = QMenu("Change Colormap", self)
        for c in Colormap.COLOR_LIST:
            hot_action = QAction(c, self)
            hot_action.triggered.connect(functools.partial(self.change_colormap, c))
            colormap_menu.addAction(hot_action)
        context_menu.addMenu(colormap_menu)

        inverse_menu = QMenu("Invert values", self)
        action1 = QAction(self.qmap.get_map_type(), self)
        action1.triggered.connect(functools.partial(self.invert_relaxation_map, False))
        inverse_menu.addAction(action1)
        action2 = QAction(f"1/{self.qmap.get_map_type()}", self)
        action2.triggered.connect(functools.partial(self.invert_relaxation_map, True))
        inverse_menu.addAction(action2)
        context_menu.addMenu(inverse_menu)

        context_menu.popup(QCursor.pos())

    def change_colormap(self, colormap):
        self.c.colormap_changed_signal.emit(colormap)

    def invert_relaxation_map(self, inverted):
        self.c.invert_relaxation_map_signal.emit(inverted)
