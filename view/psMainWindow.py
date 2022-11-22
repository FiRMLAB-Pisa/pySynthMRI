import logging

from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QGridLayout, QWidget, QVBoxLayout, QMainWindow, QFrame, QFileDialog, QAction

from model.psFileType import psFileType
from view.psCustomDialog import BatchProcessDialog
from view.psInfoWidget import PsInfoWidget
from view.psNavbar import PsNavbar
from view.psParameterGraph import PsParameterGraph
from view.psParametersWidget import PsParametersWidget
from view.psQMapWidget import PsQMapWidget
from view.psSyntheticImageWidget import PsSyntheticImageWidget
from view.psToolbar import PsToolbar

log = logging.getLogger(__name__)


# log.setLevel(LOGGING_LVL)


class MainWindowCommunicate(QObject):
    signal_resize_window = pyqtSignal()
    signal_update_qmap_path = pyqtSignal(str, str, str)
    signal_update_batch_qmap_path = pyqtSignal(str, str)
    signal_saving_smap = pyqtSignal(str, str)
    signal_batch_progress_path = pyqtSignal(str)  # TODO REMOVE
    signal_batch_progress_launch = pyqtSignal(str, str, list)
    # signal_custom_smap_added_to_navbar = pyqtSignal(str)


class PsMainWindow(QMainWindow):
    """
    Pyqt Visualization Window. This window contains the synthesized image, parameters sliders and resulting
    model equation
    """

    def __init__(self, model, parent=None):
        super().__init__()
        self.model = model
        self.qmap_view = dict()
        self.c = MainWindowCommunicate()

        self.setWindowTitle("PySynthMRI")
        self.show_ui()

    def show_ui(self):
        self.showFullScreen()
        self.init_ui()
        self.connect_handlers()

    def init_ui(self):
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_central_grid()
        self._create_status_bar()

    def _create_menu_bar(self):
        self.menu_bar = PsNavbar(self.model)
        self.setMenuBar(self.menu_bar)
        log.debug("Navigation Bar created")

    def _create_tool_bar(self):
        self.tool_bar = PsToolbar(self.model, parent=self)
        # self.tool_bar.setObjectName("toolBar")
        self.addToolBar(Qt.TopToolBarArea, self.tool_bar)
        log.debug("Tool Bar created")

    def _create_central_grid(self):
        # self.generalLayout = QGridLayout()
        self._centralWidget = QWidget(self)
        # self.setCentralWidget(self._centralWidget)

        # self._centralWidget.setLayout(self.generalLayout)

        # 1x3 layout
        self.generalLayout = QGridLayout(self._centralWidget)
        self.generalLayout.setColumnStretch(0, 2)
        self.generalLayout.setColumnStretch(1, 4)
        self.generalLayout.setColumnStretch(2, 1)
        self.qframes = []
        for y in range(3):

            qframe = QFrame()
            self.qframes.append(qframe)
            qframe.setLineWidth(2)
            qframe.setFrameStyle(QFrame.Panel | QFrame.Raised)

            self.generalLayout.addWidget(qframe, 0, y)
            # the 3rd column contains HverticalLayout with qmaps
            if y == 0:
                left_side_widget_layout = QVBoxLayout()

                parameters_widget_group = PsParametersWidget(self.model)
                left_side_widget_layout.addWidget(parameters_widget_group)

                self.parameter_graph_widget = PsParameterGraph(self.model)
                left_side_widget_layout.addWidget(self.parameter_graph_widget)

                left_side_widget_layout.addStretch(1)

                # info
                self.info_widget = PsInfoWidget("Synthetic Image Info", self.model)
                left_side_widget_layout.addWidget(self.info_widget)

                qframe.setLayout(left_side_widget_layout)
                # info text

            if y == 1:
                # synthetic image
                smap_widget_groups = QVBoxLayout()
                # smap_widget_groups.addWidget(QLabel("Synthetic Image", alignment=Qt.AlignCenter))
                self.smap_view = PsSyntheticImageWidget(self.model)  # TODO rimettere
                # self.smap_view = ImageViewer(self.model)  #TODO rimuovere

                smap_widget_groups.addWidget(self.smap_view)
                qframe.setLayout(smap_widget_groups)
            elif y == 2:
                # quantitative images
                qmaps_widget_groups = QVBoxLayout()
                for qmap in self.model.get_qmap_types():
                    self.qmap_view[qmap] = PsQMapWidget(self.model.get_qmap(qmap), self.model)
                    qmaps_widget_groups.addWidget(self.qmap_view[qmap])

                qframe.setLayout(qmaps_widget_groups)

        self.setCentralWidget(self._centralWidget)

        log.debug("central grid layout created")

    def _create_status_bar(self):
        self.statusbar = self.statusBar()

    def connect_handlers(self):
        self.model.c.signal_update_status_bar.connect(lambda message: self.statusbar.showMessage(message, 10000))
        self.model.c.signal_qmap_updated.connect(self.qmap_updated_handler)
        self.model.c.signal_smap_updated.connect(self.smap_updated_handler)

    def qmap_updated_handler(self, qmap_type):
        self.draw_qmap(qmap_type)

    def draw_qmap(self, qmap_type):
        self.qmap_view[qmap_type].update()

    def draw_info(self):
        self.info_widget.update()

    def smap_updated_handler(self):

        # log.debug("smap_updated_handler")
        if self.model.get_smap().is_loaded():
            self.smap_view.set_image(self.model.get_smap())  # TODO rimettere
            # self.smap_view.update()
            self.draw_info()
        # self.map_type_text.setText(
        #      "<h2>" + self.model.get_map_type() + "<br>" + self.model.get_map_type(long_name=True) + "</h2>")

    # def draw_smap(self, qmap_type):
    #     self.qmap_view[qmap_type].update()

    def resizeEvent(self, event):
        """Override built-in event"""
        self.c.signal_resize_window.emit()
        return super(PsMainWindow, self).resizeEvent(event)

    def add_custom_smap(self, map_type):
        # add smap to menubar
        action = QAction("&" + map_type, self, checkable=True)
        for other_action in self.menu_bar.synth_images_action:
            self.menu_bar.synth_images_action[other_action].setChecked(False)
        action.setChecked(True)
        # action.triggered.connect(functools.partial(viz_window.synth_image_menu_handler, synth_map))
        self.menu_bar.select_synthimages_menu.addAction(action)
        self.menu_bar.synth_images_action_group.addAction(action)
        self.menu_bar.synth_images_action[map_type] = action
        # add smap to toolbar
        self.tool_bar.add_new_synthetic_map_button(map_type)
        # self.tool_bar.activate_unique_smap_button(map_type)
        # self.c.signal_custom_smap_added_to_navbar.emit(map_type)

    def open_dicom_batch_load_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder that contains DICOM map')
        if folderpath:
            log.debug("open_dicom_batch_load_dialog: {}".format(folderpath))
            self.c.signal_update_batch_qmap_path.emit(folderpath, psFileType.DICOM)

    def open_niftii_batch_load_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder that contains NIFTII map')
        if folderpath:
            log.debug("open_niftii_batch_load_dialog: {}".format(folderpath))
            self.c.signal_update_batch_qmap_path.emit(folderpath, psFileType.NIFTII)

    def open_dicom_load_dialog(self, qmap):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder that contains {} map'.format(qmap))
        if folderpath:
            log.debug("open_dicom_load_dialog: {}".format(folderpath))
            self.c.signal_update_qmap_path.emit(qmap, folderpath, psFileType.DICOM)
            # self.directoryLabel.setText(folderpath)
            #
            # self.model.set_root_dcm_folder(folderpath)
            # self.model.load_dicom_folder_infos_nosub()

    def open_niftii_load_dialog(self, qmap):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        folderpath, filter = QFileDialog.getOpenFileName(self, 'Select Image that contains {} map'.format(qmap),
                                                         filter="Niftii files (*.nii)")
        if folderpath:
            log.debug("open_niftii_load_dialog: {}".format(folderpath))
            self.c.signal_update_qmap_path.emit(qmap, folderpath, psFileType.NIFTII)

    def open_dicom_save_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        scanner_params = self.model.get_smap().get_scanner_parameters()
        default_file_name = self.model.get_smap().get_map_type()
        for sp in scanner_params:
            default_file_name += "_" + sp + "_" + str(scanner_params[sp]["value"])

        path = QFileDialog.getSaveFileName(self, 'Save File', default_file_name)

        if path != ('', ''):
            log.debug("Saving dicoms to: " + path[0])
            self.c.signal_saving_smap.emit(path[0], psFileType.DICOM)

    def open_niftii_save_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        scanner_params = self.model.get_smap().get_scanner_parameters()
        default_file_name = self.model.get_smap().get_map_type()
        for sp in scanner_params:
            default_file_name += "_" + sp + "_" + str(scanner_params[sp]["value"])

        path, _ = QFileDialog.getSaveFileName(self, 'Save File', default_file_name, filter="Niftii files (*.nii)")

        if path != '':
            self.c.signal_saving_smap.emit(path, psFileType.NIFTII)

    def open_batch_process_info_dialog(self):
        presets = self.model.get_preset_list()
        smaps = self.model.get_smap_list()
        dlg = BatchProcessDialog(presets, smaps)
        res = dlg.exec_()
        if res:
            self.c.signal_batch_progress_launch.emit(dlg.selected_input_dir, dlg.selected_preset,
                                                     dlg.selected_smaps)  # path, preset, smaps

    # def open_batch_process_dialog(self):
    #     options = QFileDialog.Options()
    #     options |= QFileDialog.DontUseNativeDialog
    #
    #     folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder that contains subjects subdirectories')
    #     if folderpath:
    #         log.debug("open_batch_process_dialog: {}".format(folderpath))
    #         self.c.signal_batch_progress_path.emit(folderpath)
