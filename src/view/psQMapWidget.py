import functools

import cv2
import numpy as np
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QDropEvent, QCursor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QMenu, QAction
import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from src.model.MRIImage import Colormap


class QMapCommunicate(QObject):
    drop_event = pyqtSignal(QDropEvent)
    colormap_changed_signal = pyqtSignal(str)
    invert_relaxation_map_signal = pyqtSignal(bool)
    colorbar_toggled_signal = pyqtSignal()

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
        self.setContentsMargins(0, 0, 0, 0)
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
        self.image_info_label.setText(self.qmap.map_type)  # background-color: rgba(31, 27, 36, .7);
        self.image_info_label.setStyleSheet("""
                                background-color: rgba(31, 27, 36, .7);
                                padding: 4px;
                                border-radius: 4px;
                                margin: 1px;
                                font-weight: bold;
                """)
        self._colorbar = None
        self._show_colorbar = True

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

    def add_colorbar(self, img, colormap, min, max):
        num_ticks = 2
        color_bar_w = 10
        color_bar_v_pad = 5
        color_bar_h_pad = 5

        img = cv2.resize(img,
                         dsize=(400, 400),
                         interpolation=cv2.INTER_LINEAR)
        if self._colorbar is None:
            rows = img.shape[0]
            # color bar
            self._colorbar = np.zeros(shape=(img.shape[0] - (color_bar_v_pad * 2), color_bar_w, 3))
            for i in range(self._colorbar.shape[0]):
                for j in range(self._colorbar.shape[1]):
                    v = 255 - 255 * i / self._colorbar.shape[0]
                    self._colorbar[i, j] = [v, v, v]
            self._colorbar = np.uint8(self._colorbar)
            self._colorbar = cv2.applyColorMap(self._colorbar, colormap)

        # add colorbar to image
        img[img.shape[0] - self._colorbar.shape[0] - color_bar_v_pad:img.shape[0] - color_bar_v_pad,
        img.shape[1] - self._colorbar.shape[1] - color_bar_h_pad:img.shape[1] - color_bar_h_pad] = self._colorbar

        # bar scale
        font = cv2.FONT_HERSHEY_SIMPLEX
        color = (128, 128, 128)
        fontScale = 1
        thickness = 2

        # h limit
        cv2.putText(img,
                    "{:10.0f}".format(min),
                    (img.shape[0] - 200, int(img.shape[0] - 10)),
                    font, fontScale, color, thickness, 2, False)
        # l limit
        cv2.putText(img,
                    "{:10.0f}".format(max),
                    (img.shape[0] - 200, 30),
                    font, fontScale, color, thickness, 2, False)
        return img

    def update(self):
        np_matrix_2d = self.qmap.get_matrix(dim=2)

        # typically initial resize
        if np_matrix_2d is None:
            return

        if self.qmap.get_inverted():
            np_matrix_2d = 1. / np_matrix_2d
            np_matrix_2d[np_matrix_2d == np.inf] = 0
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
        cv_image = cv2.applyColorMap(cv_image, cv_colormap)  # COLORMAP_HOT

        cv_image[mask] = [0, 0, 0]
        if self._show_colorbar:
            cv_image = self.add_colorbar(cv_image, cv_colormap, m_min, m_max)

        cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB, cv_image)
        height, width, rgb = cv_image.shape
        q_img = QImage(cv_image.data, width, height, QImage.Format.Format_RGB888)

        q_pix_map = QPixmap(q_img)
        q_pix_map = q_pix_map.scaled(self.canvas.size(), Qt.KeepAspectRatio)
        self.canvas.setAlignment(Qt.AlignCenter)
        self.canvas.setPixmap(q_pix_map)

        # q_pix_map = QPixmap(q_img)
        # q_pix_map = q_pix_map.scaled(self.canvas.size(), Qt.KeepAspectRatio)
        # self.canvas.setAlignment(Qt.AlignCenter)
        # self.canvas.setPixmap(q_pix_map)

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

    def toggle_colorbar(self):
        self._show_colorbar = not self._show_colorbar
        self.c.colorbar_toggled_signal.emit()

    def contextMenuEvent(self, event):

        context_menu = QMenu(self)
        colormap_menu = QMenu("Change Colormap", self)
        for c in Colormap.COLOR_LIST:
            hot_action = QAction(c, self)
            hot_action.triggered.connect(functools.partial(self.change_colormap, c))
            colormap_menu.addAction(hot_action)
        context_menu.addMenu(colormap_menu)

        colorbar_action = QAction("Toggle Colorbar", self)
        colorbar_action.triggered.connect(self.toggle_colorbar)
        context_menu.addAction(colorbar_action)

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
        self._colorbar = None
        self.c.colormap_changed_signal.emit(colormap)

    def invert_relaxation_map(self, inverted):
        self.c.invert_relaxation_map_signal.emit(inverted)
