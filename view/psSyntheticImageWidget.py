import cv2
import numpy as np
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from model.MRIImage import Interpolation
from view.psSyntheticCanvas import PsSyntheticCanvas


class PsSyntheticImageWidget(QWidget):

    def __init__(self, model):
        super(PsSyntheticImageWidget, self).__init__()
        self.model = model

        self.canvas = PsSyntheticCanvas(self.model)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        self.setLayout(vbox)

    def set_image(self, smap):

        def get_affine_cv(scale_center, rot, scale, translate):
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

        synthetic_image_2d = smap.get_matrix(dim=2)
        img_2d_cp = synthetic_image_2d.astype(np.uint16)

        # interpolate
        interpolation = self.model.interpolation["interpolation_type"]
        scale = self.model.interpolation["scale"]

        if interpolation == Interpolation.LINEAR:
            img_2d_cp = cv2.resize(img_2d_cp,
                                   dsize=(round(img_2d_cp.shape[0] * scale),
                                          round(img_2d_cp.shape[1] * scale)),
                                   interpolation=cv2.INTER_LINEAR)
        elif interpolation == Interpolation.NN:
            img_2d_cp = cv2.resize(img_2d_cp,
                                   dsize=(round(img_2d_cp.shape[0] * scale),
                                          round(img_2d_cp.shape[1] * scale)),
                                   interpolation=cv2.INTER_NEAREST)
        elif interpolation == Interpolation.BICUBIC:
            img_2d_cp = cv2.resize(img_2d_cp,
                                   dsize=(round(img_2d_cp.shape[0] * scale),
                                          round(img_2d_cp.shape[1] * scale)),
                                   interpolation=cv2.INTER_CUBIC)
        elif interpolation == Interpolation.NONE:
            img_2d_cp = cv2.resize(img_2d_cp,
                                   dsize=(round(img_2d_cp.shape[0] * scale),
                                          round(img_2d_cp.shape[1] * scale)))

        # scale to windowWidth and windowCenter
        try:
            ww = self.model.get_smap().get_window_width()
            wc = self.model.get_smap().get_window_center()
        except ValueError:
            self.model.get_smap().reset_widow_scale()
            ww = self.model.get_smap().get_window_width()
            wc = self.model.get_smap().get_window_center()

        v_min = (wc - 0.5 * ww)
        v_max = (wc + 0.5 * ww)
        img_2d_cp[img_2d_cp > v_max] = v_max
        img_2d_cp[img_2d_cp < v_min] = v_min

        # use Affine Transformation Matrix M
        zoom = self.model.get_zoom()
        # scale_center_point = self.model.get_anchor_point()
        translation_point = self.model.get_translated_point()
        # M = get_affine_cv(scale_center_point, 0, zoom, translation_point)

        M = get_affine_cv(QPoint(img_2d_cp.shape[0] / 2, img_2d_cp.shape[1] / 2), 0, zoom, translation_point)
        img_2d_cp = cv2.warpAffine(img_2d_cp, M, (img_2d_cp.shape[0], img_2d_cp.shape[1]))

        # convert to grayscale 16 bit
        cv_image = (65535 * ((img_2d_cp - img_2d_cp.min()) / img_2d_cp.ptp())).astype(np.uint16)  # .copy()
        height, width = cv_image.shape

        qImg = QImage(cv_image.data, width, height, QImage.Format.Format_Grayscale16)
        qPixMap = QPixmap(qImg)
        qPixMap = qPixMap.scaled(self.canvas.size() * self.model.get_zoom(), Qt.KeepAspectRatio)

        self.canvas.setAlignment(Qt.AlignCenter)
        self.canvas.setPixmap(qPixMap)
