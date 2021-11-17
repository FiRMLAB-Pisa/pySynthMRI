import functools
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog, QGroupBox, QFormLayout, QVBoxLayout, QHBoxLayout, QMenu, QAction, QWidget, \
    QPushButton, QGridLayout, QLabel, QRadioButton

from view.SmPageWindow import SmPageWindow
from view.custom_dialog import SimpleMessageDialog, SelectImageTypeDialog
from utils.utils import waiting_effects


class SmSearchWindow(SmPageWindow):
    def __init__(self, model, parent=None):
        super().__init__()
        self.model = model
        self.setWindowTitle("PySynthMRI")
        self.parametric_images_btns = []
        self.synthetic_images_btns = []

    def show_ui(self):
        self.resize(600, 300)
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        self._init_ui()

    def _init_ui(self):
        self._create_display()
        self._create_display_dcm()
        # self._createMenuBar()

    def _createMenuBar(self):
        # menuBar = NavBarSM()
        menuBar = self.menuBar()
        menuBar.setStyleSheet(
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
        menuBar.addMenu(fileMenu)  # FILE MENU
        self.open_dicom_dir_action = QAction(QIcon(":file-open.svg"), "&Open Dicom Dir...", self)
        self.save_synth_img_action = QAction("&Save synthetic image", self)
        self.save_synth_img_action.setEnabled(False)
        self.exit_action = QAction("&Exit", self)
        self.exit_action.triggered.connect(self.model.appSM.quit)

        fileMenu.addAction(self.open_dicom_dir_action)
        fileMenu.addAction(self.save_synth_img_action)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exit_action)
        # FILE -> OPEN
        self.open_dicom_dir_action.triggered.connect(self.load_root_directory_dialog)
        # Creating menus using a title
        editMenu = menuBar.addMenu("&Edit")
        # self.saveAction.triggered.connect(self.saveFile)
        # self.exitAction.triggered.connect(self.close)
        # HELP MENU
        helpMenu = menuBar.addMenu("&Help")
        self.about_action = QAction("&About", self)
        helpMenu.addAction(self.about_action)

    @waiting_effects
    def go_to_viz(self, mode, map=None):
        try:
            # just the first time (each laoded forder)
            if self.model.missing_dicoms:
                self.model.load_missing_dicoms()
                self.model.missing_dicoms = False

            # if self.model.missing_dicoms:
            #     self.model.load_missing_dicoms()
            #     self.model.missing_dicoms = False
            if mode == "synthesize":
                self.model.set_map_type(map)

            self.model.reset_synth_params()
            self.goto("viz")
        except Exception as e:
            SimpleMessageDialog(title="ERROR: Image File not supported",
                                message="Please check the loaded paths of {}".format(e.dicom_map_type))

    def check_mode_and_go_to_viz(self, mode):
        if mode == "modify":
            self.go_to_viz("modify")
        elif mode == "synthesize":
            title = "Select New Synthetic Image"
            message = "Select the contrast-weighted image you want to synthesize:"
            images = self.model.get_synthetic_mri_image_names()
            dialog = SelectImageTypeDialog(title, message, images)
            self.go_to_viz("synthesize", dialog.choosen_map)

    def _create_display(self):
        self.dir_selection_group = QGroupBox("Select directory")
        layout = QGridLayout()
        # directory Dialog Button
        self.modify_synthetic_image_button = QPushButton("Select:")
        self.modify_synthetic_image_button.setFixedWidth(170)
        self.modify_synthetic_image_button.clicked.connect(
            self.load_root_directory_dialog
        )
        layout.addWidget(self.modify_synthetic_image_button, 0, 0)

        # Label for selected Directory
        self.directoryLabel = QLabel(text="No dir selected")
        self.directoryLabel.has_selected_dir = False
        layout.addWidget(self.directoryLabel, 0, 1)
        self.dir_selection_group.setLayout(layout)
        self.generalLayout.addWidget(self.dir_selection_group)

        # FILE TYPE RADIO
        self.file_type_group = QWidget()
        # self.file_type_group.setFixedHeight(60)
        self.file_type_group_layout = QHBoxLayout()
        self.file_type_group.setLayout(self.file_type_group_layout)
        self.dicom_radiobtn = QRadioButton('Dicom')
        self.dicom_radiobtn.setChecked(True)
        self.niftii_radiobtn = QRadioButton('Niftii')
        self.dicom_radiobtn.toggled.connect(functools.partial(self.on_click_file_type_handler, "Dicom"))
        self.niftii_radiobtn.toggled.connect(functools.partial(self.on_click_file_type_handler, "Niftii"))
        self.file_type_group_layout.addWidget(self.dicom_radiobtn)
        self.file_type_group_layout.addWidget(self.niftii_radiobtn)
        layout.addWidget(self.file_type_group, 1, 0)

    def _create_display_dcm(self):
        # INFOS GROUP
        footer_group = QWidget()
        self.layout_footer_group = QHBoxLayout()
        footer_group.setLayout(self.layout_footer_group)

        # QUANTITATIVES MAP T1, T2, PD
        self.parametric_maps_group = QGroupBox("Parametric Maps:")
        self.parametric_maps_group_layout = QFormLayout()
        self.parametric_maps_group.setLayout(self.parametric_maps_group_layout)
        self.layout_footer_group.addWidget(self.parametric_maps_group)

        for map_type in self.model.get_quantitative_mri_image_names():
            map_type_button = QPushButton(map_type)
            file_path_label = QLabel("--- Click to manually choose File ---")
            file_path_label.setMinimumWidth(200)
            file_path_label.setToolTip("Click to select a different folder")
            file_path_label.mousePressEvent = functools.partial(self.on_click_map_path, map_type, file_path_label)
            self.parametric_images_btns.append((map_type_button, file_path_label))
            self.parametric_maps_group_layout.addRow(map_type_button, file_path_label)

        # DCM INFOS GROUP
        # Accession Number: AccessionNumber
        self.synthetic_image_group = QGroupBox("Synthetic Images")
        self.synthetic_map_group_layout = QFormLayout()

        for map_type in self.model.get_synthetic_mri_image_names():
            btn = QPushButton(map_type)
            # btn.clicked.connect(lambda: self.on_clicked_dcm_button(btn))
            file_path_label = QLabel("--- Click to manually choose File ---")
            file_path_label.setMinimumWidth(200)
            btn.clicked.connect(functools.partial(self.on_clicked_dcm_button, btn, file_path_label))
            file_path_label.setToolTip("Click to select a different folder")
            file_path_label.mousePressEvent = functools.partial(self.on_click_map_path, map_type, file_path_label)
            self.synthetic_images_btns.append((btn, file_path_label))
            self.synthetic_map_group_layout.addRow(btn, file_path_label)

        self.synthetic_image_group.setLayout(self.synthetic_map_group_layout)
        self.layout_footer_group.addWidget(self.synthetic_image_group)
        self.disable_all_sub_dirs()
        self.generalLayout.addWidget(footer_group)

        # DCM INFOS GROUP
        # Accession Number: AccessionNumber
        dcm_info_group = QGroupBox("Infos:")
        layout_dcm_info = QFormLayout()

        self.accessionNumberQLabel = QLabel("")
        self.accessionNumberQLabel.setMinimumWidth(200)
        self.patientAgeQLabel = QLabel("")
        self.patientIdQLabel = QLabel("")
        self.seriesDescriptionQLabel = QLabel("")
        self.repetitionTimeQLabel = QLabel("")
        self.echoTimeQLabel = QLabel("")
        layout_dcm_info.addRow(QLabel("Accession Number"), self.accessionNumberQLabel)
        layout_dcm_info.addRow(QLabel("Patient Age"), self.patientAgeQLabel)
        layout_dcm_info.addRow(QLabel("Patient ID"), self.patientIdQLabel)
        layout_dcm_info.addRow(QLabel("Series Description"), self.seriesDescriptionQLabel)
        layout_dcm_info.addRow(QLabel("Repetition Time"), self.repetitionTimeQLabel)
        layout_dcm_info.addRow(QLabel("Echo Time"), self.echoTimeQLabel)
        dcm_info_group.setLayout(layout_dcm_info)
        self.layout_footer_group.addWidget(dcm_info_group)

        # FOOTER BUTTONS
        self.modify_synthetic_image_button = QPushButton("Modify synthetic image")
        self.modify_synthetic_image_button.setMinimumWidth(240)
        self.modify_synthetic_image_button.clicked.connect(functools.partial(self.check_mode_and_go_to_viz, "modify"))
        self.modify_synthetic_image_button.setDisabled(False) if \
            self.directoryLabel.has_selected_dir else \
            self.modify_synthetic_image_button.setDisabled(True)
        self.generalLayout.addWidget(self.modify_synthetic_image_button, alignment=Qt.AlignCenter)

        self.generate_synthetic_image_button = QPushButton("Synthesize Image using quantitative maps")
        self.generate_synthetic_image_button.setMinimumWidth(240)
        self.generate_synthetic_image_button.clicked.connect(
            functools.partial(self.check_mode_and_go_to_viz, "synthesize"))
        self.generate_synthetic_image_button.setDisabled(False) if \
            not self.model.missing_dicoms else \
            self.generate_synthetic_image_button.setDisabled(True)
        self.generalLayout.addWidget(self.generate_synthetic_image_button, alignment=Qt.AlignCenter)
        self.generalLayout.addStretch(1)

    def deselect_all_buttons(self):
        for (btn, label) in self.synthetic_images_btns:
            btn.setStyleSheet("")

    def on_click_map_path(self, map_type, label, mouse_event):
        if self.model.is_input_niftii():
            path = self.load_single_map_niftii_path_dialog(map_type)
        else:
            path = self.load_single_map_dicom_path_dialog(map_type)
        if path:
            pi = self.model.get_mri_image_by_name(map_type)
            pi.is_found = True
            pi.path = path
            pi.is_loaded = False
            label.setText(path)
            self.model.missing_dicoms = True
            if pi.type_image == "S":
                (btn, lbl) = self.get_button_by_name(pi.name)
                btn.setEnabled(True)
            # if self.model.are_quantitative_maps_set() and self.model.map_type is not None:
            #     self.modify_synthetic_image_button.setEnabled(True)
            if self.model.are_quantitative_maps_set():
                self.generate_synthetic_image_button.setEnabled(True)

    @waiting_effects
    def on_clicked_dcm_button(self, btn, label, flag):
        self.deselect_all_buttons()
        # when a dcm button is clicked, dicom is is_loaded and info are shown
        type = btn.text()
        # print("Pressed ", type)QColor(42, 130, 218)
        # btn.setStyleSheet("background-color: lightgreen")
        btn.setStyleSheet("background-color: rgb(42, 130, 218)")
        pi = self.model.get_mri_image_by_name(type)
        if pi.is_found:

            self.model.set_map_type(type)
            # self.model.set_dcm_folder(self.model.get_path_from_name(type))
            dicom_folder_path = os.path.normpath(label.text())
            try:
                self.model.load_file(dicom_folder_path)
            except Exception as e:
                SimpleMessageDialog(title="ERROR: Image File not supported",
                                    message="Please check the loaded paths of {}".format(e.dicom_map_type))
            self.update_dcm_info()
            if self.model.are_quantitative_maps_set():
                self.generate_synthetic_image_button.setEnabled(True)
                if self.model.map_type is not None:
                    self.modify_synthetic_image_button.setEnabled(True)
        else:
            self.model.set_map_type(type)
            self.model.original_synth_matrix = None
            self.model.original_synth_hdr = None
            self.update_dcm_info()  # empty dicom infos
            # ERRORE self.model.set_dcm_folder(self.model.parametric_images[0][1])
            self.model.load_file()  # load T1 for starting synthesize
            self.modify_synthetic_image_button.setEnabled(False)
            self.generate_synthetic_image_button.setEnabled(True)

    def update_dcm_info(self):
        if self.model.original_synth_hdr is not None:
            self.accessionNumberQLabel.setText(self.model.original_synth_hdr.AccessionNumber)
            self.patientAgeQLabel.setText(self.model.original_synth_hdr.PatientAge)
            self.patientIdQLabel.setText(self.model.original_synth_hdr.PatientID)
            self.seriesDescriptionQLabel.setText(self.model.original_synth_hdr.SeriesDescription)
            self.repetitionTimeQLabel.setText(str(self.model.original_synth_hdr.RepetitionTime))
            self.echoTimeQLabel.setText(str(self.model.original_synth_hdr.EchoTime))
        else:
            self.accessionNumberQLabel.setText("")
            self.patientAgeQLabel.setText("")
            self.patientIdQLabel.setText("")
            self.seriesDescriptionQLabel.setText("")
            self.repetitionTimeQLabel.setText("")
            self.echoTimeQLabel.setText("")

    def disable_all_sub_dirs(self):
        for (btn, label) in self.parametric_images_btns:
            btn.setEnabled(False)
        for (btn, label) in self.synthetic_images_btns:
            btn.setEnabled(False)

    def get_button_by_name(self, name):
        for (btn, label) in self.synthetic_images_btns:
            if btn.text() == name:
                return btn, label

        for (btn, label) in self.parametric_images_btns:
            if btn.text() == name:
                return btn, label

    def update_sub_dirs(self):
        self.disable_all_sub_dirs()
        # if self.model.get_synthetic_mri_image_list() is not None:
        for pi in self.model.get_synthetic_mri_image_list():
            if pi.is_found:
                name = pi.name
                path = pi.path
                btn, label = self.get_button_by_name(name)
                label.setText(path)
                btn.setEnabled(True)
        for pi in self.model.get_quantitative_mri_image_list():
            if pi.is_found:
                name = pi.name
                path = pi.path
                btn, label = self.get_button_by_name(name)
                label.setText(path)
                # update model
                self.model.set_mri_image_path(name, path)

    def load_root_directory_dialog(self):

        # options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        if self.model.input_images_type == "Dicom":
            folderpath = QFileDialog.getExistingDirectory(self, 'Select Dicom Folder:')
            if folderpath:
                # print(folderpath)
                self.directoryLabel.setText(folderpath)

                self.model.set_root_dcm_folder(folderpath)
                self.model.load_dicom_folder_infos()
                self.update_sub_dirs()
                self.model.missing_dicoms = True
                if self.model.are_quantitative_maps_set():
                    self.generate_synthetic_image_button.setEnabled(True)
        elif self.model.input_images_type == "Niftii":
            folderpath = QFileDialog.getExistingDirectory(self, 'Select Niftii Folder:')
            if folderpath:
                # print(folderpath)
                self.directoryLabel.setText(folderpath)

                self.model.set_root_dcm_folder(folderpath)
                self.model.load_niftii_folder_infos()
                self.update_sub_dirs()
                self.model.missing_dicoms = True
                if self.model.are_quantitative_maps_set():
                    self.generate_synthetic_image_button.setEnabled(True)

    # def load_root_directory_dialog_nosub(self):
    #     options = QFileDialog.Options()
    #     options |= QFileDialog.DontUseNativeDialog
    #
    #     folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder:')
    #     if folderpath:
    #         # print(folderpath)
    #         self.directoryLabel.setText(folderpath)
    #
    #         self.model.set_root_dcm_folder(folderpath)
    #         self.model.load_dicom_folder_infos_nosub()

    def load_single_map_dicom_path_dialog(self, map_type):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        folderpath = QFileDialog.getExistingDirectory(self, 'Select {}:'.format(map_type))
        return os.path.normpath(folderpath)

    def load_single_map_niftii_path_dialog(self, map_type):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        filepath = QFileDialog.getOpenFileName(self, 'Select {}:'.format(map_type), filter="Niftii (*.nii)")
        return filepath[0]

    def on_click_file_type_handler(self, type):
        self.model.set_input_images_type(type)