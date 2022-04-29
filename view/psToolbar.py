from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QCursor
from PyQt5.QtWidgets import QToolBar, QLabel, QPushButton, QButtonGroup, QComboBox
import resources.resources


class PsToolbar(QToolBar):
    """
    ToolBar used in Visual Page.
    """
    BUTTON_SIZE = QSize(24, 24)
    def __init__(self, model, parent=None):
        super(QToolBar, self).__init__(parent)
        self.model = model
        self.setContextMenuPolicy(Qt.PreventContextMenu)
        self.setMovable(True)
        self.setStyleSheet(
            """
            QToolBar
            {
                background-color: #2c2633;
                color: #999;
            }
            QToolBar::item
            {
                background-color: #2c2633;
                color: #999;
            }
            QToolBar::item::selected
            {
                background-color: "red";
                color: #fff;
            }
            QMenu
            {
                background-color: #2c2633;
                color: #fff;
            }
            QMenu::item::selected
            {
                background-color: "red";
                color: #999;
            }
            # QToolBar::separator
            # {
            #     background-color: "white";
            # }
             """)

        # MOUSE GROUP LABEL
        self.label_mouse = QLabel(" Mouse: ")
        self.label_mouse.setStyleSheet("QLabel {color : #999; }")

        # WINDOW SCALE MOUSE
        self.button_window_grayscale = QPushButton()
        self.button_window_grayscale.setIconSize(self.BUTTON_SIZE)
        self.button_window_grayscale.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.button_window_grayscale.setCheckable(True)
        icon_window_grayscale = QIcon()
        icon_window_grayscale.addPixmap(QPixmap(":/icons/gradient_linear_40.png"), QIcon.Normal, QIcon.On)
        self.button_window_grayscale.setIcon(icon_window_grayscale)
        self.button_window_grayscale.setToolTip("Use mouse to change:\n    window width  (\u2194)\n    window center (\u2195)")
        # WINDOW SCALE DEFAULT
        self.button_window_grayscale_default = QPushButton()
        self.button_window_grayscale_default.setIconSize(self.BUTTON_SIZE)
        self.button_window_grayscale_default.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        icon_window_grayscale = QIcon()
        icon_window_grayscale.addPixmap(QPixmap(":/icons/gradient_linear_refresh.png"), QIcon.Normal, QIcon.On)
        self.button_window_grayscale_default.setIcon(icon_window_grayscale)
        self.button_window_grayscale_default.setToolTip("Reset window scale value")

        # ZOOM MOUSE
        self.button_zoom = QPushButton()
        self.button_zoom.setIconSize(self.BUTTON_SIZE)
        self.button_zoom.setCheckable(True)
        self.button_zoom.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        icon_zoom = QIcon()
        icon_zoom.addPixmap(QPixmap(":/icons/zoom_icon.png"), QIcon.Normal, QIcon.On)
        self.button_zoom.setIcon(icon_zoom)
        self.button_zoom.setToolTip("Use mouse to Zoom:\n    zoom in   (\u2193)\n    zoom out (\u2191)")

        # TRANSLATE MOUSE
        self.button_translate = QPushButton()
        self.button_translate.setIconSize(self.BUTTON_SIZE)
        self.button_translate.setCheckable(True)
        self.button_translate.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        icon_translate = QIcon()
        icon_translate.addPixmap(QPixmap(":/icons/move_icon.png"), QIcon.Normal, QIcon.On)
        self.button_translate.setIcon(icon_translate)
        self.button_translate.setToolTip("Use mouse to translate image:\n    vertival axis   (\u2195)\n    horizontal axis (\u2194)")

        # DEFAULT ZOOM
        self.button_default_zoom = QPushButton()
        self.button_default_zoom.setIconSize(self.BUTTON_SIZE)
        self.button_default_zoom.setCheckable(False)
        self.button_default_zoom.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        icon_default_zoom = QIcon()
        icon_default_zoom.addPixmap(QPixmap(":/icons/zoom_refresh_40.png"), QIcon.Normal, QIcon.On)
        self.button_default_zoom.setIcon(icon_default_zoom)
        self.button_default_zoom.setToolTip("Reset zoom value")

        # SLICER MOUSE
        self.button_slicer = QPushButton()
        self.button_slicer.setIconSize(self.BUTTON_SIZE)
        self.button_slicer.setCheckable(True)
        self.button_slicer.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        icon_zoom = QIcon()
        icon_zoom.addPixmap(QPixmap(":/icons/three_layers.png"), QIcon.Normal, QIcon.On)
        self.button_slicer.setIcon(icon_zoom)
        self.button_slicer.setToolTip("Use mouse to change slice:\n    next slice   (\u2193)\n    previous slice (\u2191)")

        # PARAMS GROUP LABEL
        self.label_parameters = QLabel(" Parameters: ")
        self.label_parameters.setStyleSheet("QLabel {color : #999; }")

        # DEFAULT PARAMS
        self.button_default_param = QPushButton()
        self.button_default_param.setIconSize(self.BUTTON_SIZE)
        icon_default_params = QIcon()
        icon_default_params.addPixmap(QPixmap(":/icons/default_24.png"), QIcon.Normal, QIcon.On)
        self.button_default_param.setIcon(icon_default_params)
        self.button_default_param.setToolTip("Set scanner parameters \nto default values")

        # ORIENTATION
        # self.combo_orientation = QComboBox()
        # self.combo_orientation.setIconSize(self.BUTTON_SIZE)
        #
        # self.combo_orientation.addItem(QIcon(":icons/three_layers.png"), "Axial")
        #
        # self.combo_orientation.addItem(QIcon(":icons/translate_icon.png"), "Sagittal")
        # self.combo_orientation.addItem(QIcon(":icons/gradient_linear_refresh.png"), "Coronal")

        # SYNTH IMAGES
        self.synth_images_buttons = dict()
        smaps = self.model.get_smap_list()
        # self.smap_group_buttons = QButtonGroup(self)
        self.smap_group_buttons = QButtonGroup(self, exclusive=True)

        for synth_map in smaps:
            smap_button = QPushButton(synth_map)
            smap_button.setFixedHeight(self.BUTTON_SIZE.height())
            smap_button.setIconSize(self.BUTTON_SIZE)
            smap_button.setStyleSheet("QPushButton:pressed { background-color: red }"
                              "QPushButton:checked { background-color: red }")
            smap_button.setCheckable(True)
            smap_button.setToolTip("{} ({})\nModel: {}".format(synth_map,
                                                               smaps[synth_map]["title"],
                                                               smaps[synth_map]["equation_string"]))

            self.synth_images_buttons[synth_map] = smap_button
            self.smap_group_buttons.addButton(smap_button)

        # SAVE NIFTII
        self.button_save_niftii = QPushButton()
        self.button_save_niftii.setIconSize(self.BUTTON_SIZE)
        self.button_save_niftii.setCheckable(False)
        self.button_save_niftii.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        icon_save_niftii = QIcon()
        icon_save_niftii.addPixmap(QPixmap(":/icons/save_niftii.png"), QIcon.Normal, QIcon.On)
        self.button_save_niftii.setIcon(icon_save_niftii)
        self.button_save_niftii.setToolTip("Save current synthetic image as Niftii file")

        # SAVE DICOM
        self.button_save_dicom = QPushButton()
        self.button_save_dicom.setIconSize(self.BUTTON_SIZE)
        self.button_save_dicom.setCheckable(False)
        self.button_save_dicom.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        icon_save_dicom = QIcon()
        icon_save_dicom.addPixmap(QPixmap(":/icons/save_dicom.png"), QIcon.Normal, QIcon.On)
        self.button_save_dicom.setIcon(icon_save_dicom)
        self.button_save_dicom.setToolTip("Save current synthetic image as Dicom folder")

        # LAYOUT
        self.addWidget(self.button_save_niftii)
        self.addWidget(self.button_save_dicom)
        self.addSeparator()
        # self.addWidget(self.label_mouse)
        self.addWidget(self.button_window_grayscale)
        self.addWidget(self.button_window_grayscale_default)
        self.addSeparator()
        self.addWidget(self.button_zoom)
        self.addWidget(self.button_translate)
        self.addWidget(self.button_default_zoom)
        self.addSeparator()
        self.addWidget(self.button_slicer)
        self.addSeparator()
        # self.addWidget(self.label_parameters)
        self.addWidget(self.button_default_param)

        # self.addSeparator()
        # self.addWidget(self.combo_orientation)

        self.addSeparator()
        for sib in self.synth_images_buttons:
            self.addWidget(self.synth_images_buttons[sib])

    def activate_unique_smap_button(self, smap):
        self.synth_images_buttons[smap].setChecked(True)
        # for s in self.synth_images_buttons:
        #     self.synth_images_buttons[s].setChecked(False)
        # self.synth_images_buttons[smap].setChecked(True)

    def add_new_synthetic_map_button(self, smap_type):
        smap = self.model.get_smap_list()[smap_type]

        smap_button = QPushButton(smap_type)
        smap_button.setFixedHeight(self.BUTTON_SIZE.height())
        smap_button.setIconSize(self.BUTTON_SIZE)
        smap_button.setStyleSheet("QPushButton:pressed { background-color: red }"
                                  "QPushButton:checked { background-color: red }")
        smap_button.setCheckable(True)
        smap_button.setToolTip("{} ({})\nModel: {}".format(smap_type,
                                                           smap["title"],
                                                           smap["equation_string"]))

        self.synth_images_buttons[smap_type] = smap_button
        self.smap_group_buttons.addButton(smap_button)
        self.addWidget(smap_button)
