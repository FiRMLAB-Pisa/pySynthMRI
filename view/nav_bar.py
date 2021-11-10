import functools

from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QMenuBar, QAction, QMenu, QActionGroup

from model.SmModel import Orientation


class NavBarSM(QMenuBar):
    """
    Navbar used in Visual Page.
    """
    def __init__(self, viz_window, parent=None):

        super(NavBarSM, self).__init__(parent)
        self.setStyleSheet(
            """
            QMenuBar
            {
                background-color: #1F1B24;
                color: #999;
            }
            QMenuBar::item
            {
                background-color: #1F1B24;
                color: #999;
            }
            QMenuBar::item::selected
            {
                background-color: #2a82da;
                color: #fff;
            }
            QMenu
            {
                background-color: #1F1B24;
                color: #fff;
            }
            QMenu::item::selected
            {
                background-color: #2a82da;
                color: #999;
            }
             """
        )
        # FILE
        fileMenu = QMenu("&File", self)
        self.addMenu(fileMenu)
        # FILE -> OPEN DIR
        self.open_dicom_dir_action = QAction(QIcon(":file-open.svg"), "&Open Dicom Dir...", self)
        # FILE -> SAVE IMAGES
        # self.save_synth_img_action = QAction("&Save synthetic image", self)
        # self.save_synth_img_action.setEnabled(True)
        # self.save_synth_img_action.triggered.connect(viz_window.on_clicked_save_dicom_button)
        file_save_menu = QMenu("&Save synthetic image...", self)
        file_save_menu_action_group = QActionGroup(file_save_menu)
        file_save_menu_action_group.setExclusive(True)
        file_save_dicom_action = QAction("&Dicom Format", self, checked=True, checkable=False)
        file_save_dicom_action.triggered.connect(viz_window.on_clicked_save_dicom_button)
        file_save_menu.addAction(file_save_dicom_action)
        file_save_menu_action_group.addAction(file_save_dicom_action)
        file_save_niftii_action = QAction("&Niftii Format", self, checked=True, checkable=False)
        file_save_niftii_action.triggered.connect(viz_window.on_clicked_save_niftii_button)
        file_save_menu.addAction(file_save_niftii_action)
        file_save_menu_action_group.addAction(file_save_niftii_action)


        # FILE -> SAVE BACK
        self.back_action = QAction("&Back", self)
        self.back_action.triggered.connect(viz_window.on_clicked_back_button)

        self.exit_action = QAction("&Exit", self)
        self.exit_action.triggered.connect(viz_window.model.appSM.quit)

        fileMenu.addAction(self.open_dicom_dir_action)
        # fileMenu.addAction(self.save_synth_img_action)
        fileMenu.addMenu(file_save_menu)
        fileMenu.addSeparator()
        fileMenu.addAction(self.back_action)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exit_action)

        # FILE -> OPEN
        # self.open_dicom_dir_action.triggered.connect(self.load_root_directory_dialog)
        # Creating menus using a title
        # SETTINGS
        settings_menu = self.addMenu("&Settings")
        # SETTINGS -> SELECT SYNTHETIC IMAGES
        select_synthimages_menu = QMenu("&Select Synth image", self)
        settings_menu.addMenu(select_synthimages_menu)
        self.synth_images_action_group = QActionGroup(select_synthimages_menu)
        self.synth_images_action_group.setExclusive(True)

        for synth_map in viz_window.model.synth_maps:
            action = QAction("&" + synth_map, self, checkable=True)
            if synth_map == viz_window.model.get_map_type():
                action.setChecked(True)
            action.triggered.connect(functools.partial(viz_window.synth_image_menu_handler, synth_map))
            select_synthimages_menu.addAction(action)
            self.synth_images_action_group.addAction(action)

        settings_menu.addSeparator()

        # SETTINGS -> ADD CUSTOM PARAMETER
        self.settings_custom_param_action = QAction("&Add custom parameter", self)
        self.settings_custom_param_action.triggered.connect(viz_window.on_clicked_custom_param_button)
        settings_menu.addAction(self.settings_custom_param_action)

        # IMAGE
        image_menu = QMenu("&Image", self)
        self.addMenu(image_menu)
        # IMAGE -> ORIENTATION
        image_orientation_menu = QMenu("&Orientation", self)
        image_menu.addMenu(image_orientation_menu)
        self.orientation_action_group = QActionGroup(image_orientation_menu)
        self.orientation_action_group.setExclusive(True)

        self.orientation_axial_action = QAction("&Axial", self, checked=True, checkable=True)
        self.orientation_axial_action.setChecked(True)
        self.orientation_axial_action.setShortcut(QKeySequence("Ctrl+Shift+A"))
        self.orientation_axial_action.triggered.connect(functools.partial(viz_window.orientation_menu_handler, Orientation.AXIAL))
        image_orientation_menu.addAction(self.orientation_axial_action)
        self.orientation_action_group.addAction(self.orientation_axial_action)

        self.orientation_sagittal_action = QAction("&Sagittal", self, checked=False, checkable=True)
        self.orientation_sagittal_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.orientation_sagittal_action.triggered.connect(functools.partial(viz_window.orientation_menu_handler, Orientation.SAGITTAL))
        image_orientation_menu.addAction(self.orientation_sagittal_action)
        self.orientation_action_group.addAction(self.orientation_sagittal_action)

        self.orientation_coronal_action = QAction("&Cononal", self, checked=False, checkable=True)
        self.orientation_coronal_action.setShortcut(QKeySequence("Ctrl+Shift+C"))
        self.orientation_coronal_action.triggered.connect(functools.partial(viz_window.orientation_menu_handler, Orientation.CORONAL))
        image_orientation_menu.addAction(self.orientation_coronal_action)
        self.orientation_action_group.addAction(self.orientation_coronal_action)

        # IMAGE -> INTERPOLATION
        image_interpolation_menu = QMenu("&Interpolation", self)
        image_menu.addMenu(image_interpolation_menu)
        self.interpolation_action_group = QActionGroup(image_interpolation_menu)
        self.interpolation_action_group.setExclusive(True)

        self.interpolation_none_action = QAction("&None", self, checkable=True)
        self.interpolation_none_action.triggered.connect(functools.partial(viz_window.interpolation_menu_handler, "none"))
        image_interpolation_menu.addAction(self.interpolation_none_action)
        self.interpolation_action_group.addAction(self.interpolation_none_action)

        self.interpolation_linear_action = QAction("&Linear", self, checked=False, checkable=True)
        self.interpolation_linear_action.setChecked(True)
        self.interpolation_linear_action.triggered.connect(functools.partial(viz_window.interpolation_menu_handler, "linear"))
        image_interpolation_menu.addAction(self.interpolation_linear_action)
        self.interpolation_action_group.addAction(self.interpolation_linear_action)

        self.interpolation_bicubic_action = QAction("&Bicubic", self, checked=False, checkable=True)
        self.interpolation_bicubic_action.triggered.connect(functools.partial(viz_window.interpolation_menu_handler, "bicubic"))
        image_interpolation_menu.addAction(self.interpolation_bicubic_action)
        self.interpolation_action_group.addAction(self.interpolation_bicubic_action)

        self.interpolation_nn_action = QAction("&Nearest Neighbor", self, checked=False, checkable=True)
        self.interpolation_nn_action.triggered.connect(functools.partial(viz_window.interpolation_menu_handler, "nn"))
        image_interpolation_menu.addAction(self.interpolation_nn_action)
        self.interpolation_action_group.addAction(self.interpolation_nn_action)

        # HELP MENU
        helpMenu = self.addMenu("&Help")
        self.about_action = QAction("&About", self)
        helpMenu.addAction(self.about_action)