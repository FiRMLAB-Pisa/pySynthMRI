import logging
import os

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMenuBar, QAction, QMenu, QActionGroup, QFileDialog

from model.psFileType import psFileType

log = logging.getLogger("psNavbar")





class PsNavbar(QMenuBar):
    """
    Navbar used in Visual Page.
    """

    def __init__(self, model, parent=None):
        super(PsNavbar, self).__init__(parent)
        self.model = model
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
                background-color: "red";
                color: #fff;
            }
            QMenu
            {
                background-color: #1F1B24;
                color: #fff;
            }
            QMenu::item::selected
            {
                background-color: "red";
                color: #999;
            }
             """
        )
        # #2a82da lightblue
        # FILE
        fileMenu = QMenu("&File", self)
        self.addMenu(fileMenu)

        # FILE -> OPEN DIR
        file_load_dicom_menu = QMenu("&Load Dicom QMAP...", self)
        self.open_dicom_dir_actions = dict()
        for qmap in model.get_qmap_types():
            self.open_dicom_dir_actions[qmap] = QAction("&"+qmap + " Quantitative Map", self)
            file_load_dicom_menu.addAction(self.open_dicom_dir_actions[qmap])

        file_load_niftii_menu = QMenu("&Load Niftii QMAP...", self)
        self.open_niftii_dir_actions = dict()
        for qmap in model.get_qmap_types():
            self.open_niftii_dir_actions[qmap] = QAction("&" + qmap + " Quantitative Map", self)
            file_load_niftii_menu.addAction(self.open_niftii_dir_actions[qmap])

        # FILE -> SAVE IMAGES
        # self.save_synth_img_action = QAction("&Save synthetic image", self)
        # self.save_synth_img_action.setEnabled(True)
        # self.save_synth_img_action.triggered.connect(viz_window.on_clicked_save_dicom_button)
        file_save_menu = QMenu("&Save synthetic image...", self)
        file_save_menu_action_group = QActionGroup(file_save_menu)
        file_save_menu_action_group.setExclusive(True)
        self.file_save_dicom_action = QAction("&Dicom Format", self, checked=True, checkable=False)
        file_save_menu.addAction(self.file_save_dicom_action)
        file_save_menu_action_group.addAction(self.file_save_dicom_action)
        self.file_save_niftii_action = QAction("&Niftii Format", self, checked=True, checkable=False)
        file_save_menu.addAction(self.file_save_niftii_action)
        file_save_menu_action_group.addAction(self.file_save_niftii_action)

        # FILE -> SAVE BACK
        # self.back_action = QAction("&Back", self)

        self.exit_action = QAction("&Exit", self)

        fileMenu.addMenu(file_load_dicom_menu)
        fileMenu.addMenu(file_load_niftii_menu)
        fileMenu.addSeparator()
        # fileMenu.addAction(self.save_synth_img_action)
        fileMenu.addMenu(file_save_menu)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exit_action)

        # FILE -> OPEN
        # self.open_dicom_dir_action.triggered.connect(self.load_root_directory_dialog)

        # IMAGE
        image_menu = QMenu("&Image", self)
        self.addMenu(image_menu)

        # SETTINGS -> SELECT SYNTHETIC IMAGES
        self.select_synthimages_menu = QMenu("&Select Synth image", self)
        image_menu.addMenu(self.select_synthimages_menu)
        self.synth_images_action_group = QActionGroup(self.select_synthimages_menu)
        self.synth_images_action_group.setExclusive(True)
        self.synth_images_action = dict()
        for synth_map in model.get_smap_list():
            action = QAction("&" + synth_map, self, checkable=True)
            # if synth_map == self.model.get_current_map_type():
            #     action.setChecked(True)
            self.select_synthimages_menu.addAction(action)
            self.synth_images_action_group.addAction(action)
            self.synth_images_action[synth_map] = action

        image_menu.addSeparator()

        # IMAGE -> ORIENTATION
        image_orientation_menu = QMenu("&Orientation", self)
        image_menu.addMenu(image_orientation_menu)
        self.orientation_action_group = QActionGroup(image_orientation_menu)
        self.orientation_action_group.setExclusive(True)

        self.orientation_axial_action = QAction("&Axial", self, checked=True, checkable=True)
        self.orientation_axial_action.setChecked(True)
        self.orientation_axial_action.setShortcut(QKeySequence("Ctrl+Shift+A"))

        image_orientation_menu.addAction(self.orientation_axial_action)
        self.orientation_action_group.addAction(self.orientation_axial_action)

        self.orientation_sagittal_action = QAction("&Sagittal", self, checked=False, checkable=True)
        self.orientation_sagittal_action.setShortcut(QKeySequence("Ctrl+Shift+S"))

        image_orientation_menu.addAction(self.orientation_sagittal_action)
        self.orientation_action_group.addAction(self.orientation_sagittal_action)

        self.orientation_coronal_action = QAction("&Coronal", self, checked=False, checkable=True)
        self.orientation_coronal_action.setShortcut(QKeySequence("Ctrl+Shift+C"))

        image_orientation_menu.addAction(self.orientation_coronal_action)
        self.orientation_action_group.addAction(self.orientation_coronal_action)

        # IMAGE -> INTERPOLATION
        image_interpolation_menu = QMenu("&Interpolation", self)
        image_menu.addMenu(image_interpolation_menu)
        self.interpolation_action_group = QActionGroup(image_interpolation_menu)
        self.interpolation_action_group.setExclusive(True)

        self.interpolation_none_action = QAction("&None", self, checkable=True)
        # self.interpolation_none_action.triggered.connect(
        #     functools.partial(viz_window.interpolation_menu_handler, "none"))
        image_interpolation_menu.addAction(self.interpolation_none_action)
        self.interpolation_action_group.addAction(self.interpolation_none_action)

        self.interpolation_linear_action = QAction("&Linear", self, checked=False, checkable=True)
        self.interpolation_linear_action.setChecked(True)
        # self.interpolation_linear_action.triggered.connect(
        #     functools.partial(viz_window.interpolation_menu_handler, "linear"))
        image_interpolation_menu.addAction(self.interpolation_linear_action)
        self.interpolation_action_group.addAction(self.interpolation_linear_action)

        self.interpolation_bicubic_action = QAction("&Bicubic", self, checked=False, checkable=True)

        image_interpolation_menu.addAction(self.interpolation_bicubic_action)
        self.interpolation_action_group.addAction(self.interpolation_bicubic_action)

        self.interpolation_nn_action = QAction("&Nearest Neighbor", self, checked=False, checkable=True)
        image_interpolation_menu.addAction(self.interpolation_nn_action)
        self.interpolation_action_group.addAction(self.interpolation_nn_action)


        # SETTINGS
        settings_menu = self.addMenu("&Settings")



        # SETTINGS -> SHOW DICOM HEADER
        # TODO

        # SETTINGS -> ADD CUSTOM SYNTHETIC MAP
        self.settings_custom_smap_action = QAction("&Add custom Synthetic Map", self)
        settings_menu.addAction(self.settings_custom_smap_action)

        # SETTINGS -> ADD CUSTOM PARAMETER
        self.settings_custom_param_action = QAction("&Add custom parameter", self)
        settings_menu.addAction(self.settings_custom_param_action)



        # # TOOLS
        # tools_menu = self.addMenu("&Tools")
        # mouse_behaviour_menu = QMenu("&Mouse behaviour", self)
        # tools_menu.addMenu(mouse_behaviour_menu)
        # self.mouse_behaviour_action_group = QActionGroup(mouse_behaviour_menu)
        # self.mouse_behaviour_action_group.setExclusive(True)
        # window_scale_action = QAction("&Window scale", self, checkable=True)
        # self.mouse_behaviour_action_group.addAction(window_scale_action)
        # mouse_behaviour_menu.addAction(window_scale_action)
        # zoom_action = QAction("&Zoom", self, checkable=True)
        # self.mouse_behaviour_action_group.addAction(zoom_action)
        # mouse_behaviour_menu.addAction(zoom_action)

        # HELP MENU
        helpMenu = self.addMenu("&Help")
        self.about_action = QAction("&About", self)
        helpMenu.addAction(self.about_action)


    # def add_custom_smap(self, map_type):
    #     action = QAction("&" + map_type, self, checkable=True)
    #     for other_action in self.synth_images_action:
    #         self.synth_images_action[other_action].setChecked(False)
    #     action.setChecked(True)
    #     # action.triggered.connect(functools.partial(viz_window.synth_image_menu_handler, synth_map))
    #     self.select_synthimages_menu.addAction(action)
    #     self.synth_images_action_group.addAction(action)
    #     self.synth_images_action[map_type] = action
    #
    #     # self.c.signal_custom_smap_added_to_navbar.emit(map_type)
    #
    # def open_dicom_load_dialog(self, qmap):
    #     options = QFileDialog.Options()
    #     options |= QFileDialog.DontUseNativeDialog
    #
    #     folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder that contains {} map'.format(qmap))
    #     if folderpath:
    #         log.debug("open_dicom_load_dialog: {}".format(folderpath))
    #         self.c.signal_update_qmap_path.emit(qmap, folderpath, psFileType.DICOM)
    #         # self.directoryLabel.setText(folderpath)
    #         #
    #         # self.model.set_root_dcm_folder(folderpath)
    #         # self.model.load_dicom_folder_infos_nosub()
    #
    # def open_niftii_load_dialog(self, qmap):
    #     options = QFileDialog.Options()
    #     options |= QFileDialog.DontUseNativeDialog
    #
    #     folderpath, filter = QFileDialog.getOpenFileName(self, 'Select Image that contains {} map'.format(qmap), filter="Niftii files (*.nii)")
    #     if folderpath:
    #         log.debug("open_niftii_load_dialog: {}".format(folderpath))
    #         self.c.signal_update_qmap_path.emit(qmap, folderpath, psFileType.NIFTII)
    #
    # def open_dicom_save_dialog(self):
    #     options = QFileDialog.Options()
    #     options |= QFileDialog.DontUseNativeDialog
    #     scanner_params = self.model.get_smap().get_scanner_parameters()
    #     for sp in scanner_params:
    #         default_file_name = self.model.get_smap().get_map_type() + "_" + sp + "_" + str(scanner_params[sp]["value"])
    #
    #     path = QFileDialog.getSaveFileName(self, 'Save File', default_file_name)
    #
    #     if path != ('', ''):
    #         dir_path = os.path.dirname(path[0])
    #         filename = os.path.basename(path[0])
    #
    #         log.debug("Saving dicoms to: " + path[0])
    #         self.c.signal_saving_smap.emit(path[0], psFileType.DICOM)
    #
    # def open_niftii_save_dialog(self):
    #     options = QFileDialog.Options()
    #     options |= QFileDialog.DontUseNativeDialog
    #     default_file_name = self.model.get_smap().get_map_type() + "_mod.nii"
    #     path, _ = QFileDialog.getSaveFileName(self, 'Save File', default_file_name, filter="Niftii files (*.nii)")
    #
    #     if path != '':
    #         self.c.signal_saving_smap.emit(path, psFileType.NIFTII)

    def activate_unique_smap_action(self, smap):
        self.synth_images_action[smap].setChecked(True)
