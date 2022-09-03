import os

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QGroupBox, QFormLayout, QLineEdit, \
    QTextEdit, QWidget, QHBoxLayout, QComboBox, QSpinBox, QListWidget, QAbstractItemView, QSizePolicy, QFileDialog

# import Config
from model.CheckableComboBox import CheckableComboBox
from view.psQDoubleQListWidget import psQDoubleQListWidget


class SimpleMessageDialog(QDialog):
    def __init__(self, title="", message=""):
        super().__init__()

        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags()  # reuse initial flags
                            & ~Qt.WindowContextHelpButtonHint  # negate the flag you want to unset
                            )
        QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        message = QLabel(message)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.exec()


class PsCustomSmapDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._parameters = []
        self._create_form_group_box()
        self.custom_param = dict()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.add_new_custom_par)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.form_smap_description_group)
        mainLayout.addWidget(self.form_parameter_group)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Add Custom Sytnhetic Map")
        self.setWindowFlags(self.windowFlags()  # reuse initial flags
                            & ~Qt.WindowContextHelpButtonHint  # negate the flag you want to unset
                            )

    def _create_form_group_box(self):
        self.form_smap_description_group = QGroupBox("New Synthetic Map:")
        layout = QFormLayout()
        self.label_name_edit = QLineEdit()
        layout.addRow(QLabel("Synthetic Map Name *"), self.label_name_edit)
        self.label_title_edit = QLineEdit()
        layout.addRow(QLabel("Description"), self.label_title_edit)
        self.equation_edit = QLineEdit()
        layout.addRow(QLabel("Equation *"), self.equation_edit)
        self.form_smap_description_group.setLayout(layout)

        self.form_parameter_group = QGroupBox("Scanner Parameters: ")
        form_parameter_layout = QVBoxLayout()
        self.form_parameter_group.setLayout(form_parameter_layout)

        for x in range(5):
            parameter_row = QWidget()
            layout_sp = QHBoxLayout()

            label_sp_label = QLabel("Scanner Parameter {}".format(x))
            label_sp_name_edit = QLineEdit()
            label_sp_name_edit.setPlaceholderText("Name")

            label_sp_default_edit = QLineEdit()
            label_sp_default_edit.setPlaceholderText("Default Value")

            label_sp_min_edit = QLineEdit()
            label_sp_min_edit.setPlaceholderText("Min Value")

            label_sp_max_edit = QLineEdit()
            label_sp_max_edit.setPlaceholderText("Max Value")

            label_sp_step_edit = QLineEdit()
            label_sp_step_edit.setPlaceholderText("Slider Step")

            layout_sp.addWidget(label_sp_label)
            layout_sp.addWidget(label_sp_name_edit)
            layout_sp.addWidget(label_sp_default_edit)
            layout_sp.addWidget(label_sp_min_edit)
            layout_sp.addWidget(label_sp_max_edit)
            layout_sp.addWidget(label_sp_step_edit)

            parameter_row.setLayout(layout_sp)
            form_parameter_layout.addWidget(parameter_row)
            self._parameters.append({
                "name": label_sp_name_edit,
                "default": label_sp_default_edit,
                "min": label_sp_min_edit,
                "max": label_sp_max_edit,
                "step": label_sp_step_edit})

    def add_new_custom_par(self):
        try:
            self.custom_smap = {
                "name": self.label_name_edit.text(),
                "title": self.label_title_edit.text(),
                "equation": self.equation_edit.text(),
                "parameters": dict()
            }
            for param in self._parameters:
                param_struct = self.validate_single_param(param)
                if param_struct:
                    param_struct = {
                        "label": param["name"].text(),
                        "value": int(param["default"].text()),
                        "min": int(param["min"].text()),
                        "max": int(param["max"].text()),
                        "step": int(param["step"].text())
                    }
                    self.custom_smap["parameters"][param["name"].text()] = param_struct
            # self.custom_param[self.label_name_edit.text()][param[param]]

            if self.validate():
                self.accept()

        except Exception as e:
            print(e)
            return

    def validate_single_param(self, param):
        try:
            param_struct = {
                "label": param["name"].text(),
                "value": int(param["default"].text()),
                "min": int(param["min"].text()),
                "max": int(param["max"].text()),
                "step": int(param["step"].text())
            }
            if param_struct["label"] == "":
                return None

            return param_struct
        except:
            return None

    def validate(self):
        # if len(list(self.custom_smap["parameters"].keys())) == 0:
        #     return False
        return True


class CustomParamDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._create_form_group_box()
        self.custom_param = dict()
        # self.model = model

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.add_new_custom_par)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.form_smap_description_group)
        mainLayout.addWidget(self.form_parameter_group)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Add custom parameter")
        self.setWindowFlags(self.windowFlags()  # reuse initial flags
                            & ~Qt.WindowContextHelpButtonHint  # negate the flag you want to unset
                            )

    def _create_form_group_box(self):
        self.form_smap_description_group = QGroupBox("Slider parameters:")
        layout = QFormLayout()
        # for key in self.custom_param:
        #     layout.addRow(QLabel(key), QLineEdit())
        self.label_edit_edit = QLineEdit()
        layout.addRow(QLabel("label"), self.label_edit_edit)
        self.default_edit = QLineEdit()
        layout.addRow(QLabel("default"), self.default_edit)
        self.min_edit = QLineEdit()
        layout.addRow(QLabel("min"), self.min_edit)
        self.max_edit = QLineEdit()
        layout.addRow(QLabel("max"), self.max_edit)
        self.step_edit = QLineEdit()
        layout.addRow(QLabel("step"), self.step_edit)
        self.form_smap_description_group.setLayout(layout)

        self.form_parameter_group = QGroupBox("Equation parameters: ")
        self.form_parameter_group.setToolTip("""Equation form:\n[ offset + scale * exp(-par/map) ]
            where:
                offset: scalar
                scale: scalar or mapType
                map: mapType
                par: this parameter
                mapType: [\"T1\", \"T2\", \"PDw\"]""")
        layout_eq = QFormLayout()
        textEdit = QTextEdit()
        textEdit.setReadOnly(True)
        textEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        textEdit.setFixedHeight(120)
        textEdit.setPlainText("""Equation:\n[ offset + scale * exp(-par/map) ]
            where:
                offset: scalar
                scale: scalar or mapType
                map: mapType
                par: this parameter
                mapType: [\"T1\", \"T2\", \"PDw\"]""")
        layout_eq.addRow(textEdit)
        self.offset_edit = QLineEdit()
        layout_eq.addRow(QLabel("offset"), self.offset_edit)
        self.scale_edit = QLineEdit()
        layout_eq.addRow(QLabel("scale"), self.scale_edit)
        self.map_edit = QLineEdit()
        layout_eq.addRow(QLabel("map"), self.map_edit)
        self.form_parameter_group.setLayout(layout_eq)

    # def add_new_custom_par(self):
    #     try:
    #         self.custom_param = {"label": self.label_edit_edit.text() if self.label_edit_edit.text() != "" else None,
    #                              "default": int(self.default_edit.text()) if self.default_edit.text() != "" else None,
    #                              "min": int(self.min_edit.text()) if self.min_edit.text() != "" else None,
    #                              "max": int(self.max_edit.text()) if self.max_edit.text() != "" else None,
    #                              "step": int(self.step_edit.text()) if self.step_edit.text() != "" else None,
    #                              "value": int(self.default_edit.text()) if self.default_edit.text() != "" else None,
    #                              "weight": 10,
    #                              "enabled": False}
    #         offset = int(self.offset_edit.text()) if self.offset_edit.text() != "" else None
    #         # check scalar scale
    #         if self.scale_edit.text() == "":
    #             return
    #         else:
    #             if self.scale_edit.text() in [self.model.config.T1, self.model.config.T2, self.model.config.PD]:
    #                 scale = self.scale_edit.text()
    #             else:
    #                 scale = int(self.scale_edit.text())
    #         map = self.map_edit.text() if self.map_edit.text() in [Config.T1, Config.T2,
    #                                                                Config.PD] else None
    #         self.custom_param["equation"] = [offset, scale, map]
    #     except:
    #         return
    #
    #     if self.validate():
    #         self.accept()

    def validate(self):
        # validate required fields
        for k in self.custom_param:
            if self.custom_param[k] is None:
                return False
        offset = self.custom_param["equation"][0]
        scale = self.custom_param["equation"][1]
        if offset is None or scale is None or map is None:
            return False
        return True


class AboutDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        QBtn = QDialogButtonBox.Ok  # No cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()

        title = QLabel("PySynthMRI")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        layout.addWidget(title)

        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('resources', 'logos', 'logo3.png')))
        layout.addWidget(logo)

        layout.addWidget(QLabel("Version 0.2.2"))
        repo_label = QLabel("https://github.com/FiRMLAB-Pisa/pySynthMRI")
        repo_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        repo_label.setOpenExternalLinks(True)
        layout.addWidget(repo_label)

        layout.addWidget(QLabel("2022 FiRM LAB - Pisa"))
        layout.addWidget(QLabel("Laboratory of Medical Physics and \nMagnetic Resonance Technologies"))

        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

class BatchProcessDialog(QDialog):
    NumGridRows = 3
    NumButtons = 4
    selected_preset = None

    def __init__(self, presets, smap_types):
        super(BatchProcessDialog, self).__init__()
        self.createFormGroupBox(presets, smap_types)

        self.selected_preset = None
        self.selected_smaps = None
        self.selected_input_dir = None

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Batch Process")

    def accept(self):
        self.selected_preset = self.preset_qcombo.currentText()
        self.selected_smaps = self.smaps_qlist.selectedItems()
        self.selected_input_dir = self.input_dir_label.text()
        if self.selected_preset and self.selected_smaps and self.selected_input_dir != "Select input directory":
            super().accept()

    def createFormGroupBox(self,presets, smap_types):
        self.smap_types = smap_types
        self.formGroupBox = QGroupBox("Process information")

        layout = QFormLayout()

        self.preset_qcombo = QComboBox()
        self.preset_qcombo.activated[str].connect(self.changed_preset)
        layout.addRow(QLabel("Preset Images:"), self.preset_qcombo)
        for preset in presets:
            self.preset_qcombo.addItem(preset)


        # self.smaps_qlist = QListWidget()
        self.smaps_qlist = psQDoubleQListWidget()
        self.smaps_qlist.setToolTip("""Choose Synthetic images to process.""")

        synth_images_label = QLabel("Synthetic Images:")
        synth_images_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        synth_images_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addRow(synth_images_label, self.smaps_qlist)
        smap_types = [x for x in smap_types if smap_types[x]["preset"] == self.preset_qcombo.currentText()]
        self.smaps_qlist.insertItems(smap_types)


        self.input_dir_label = QLabel("Select input directory")
        layout.addRow(QLabel("Input Dir"), self.input_dir_label)
        self.input_dir_label.mousePressEvent = self.clicked_input_dir_label
        self.formGroupBox.setLayout(layout)

    def changed_preset(self, preset):
        self.smaps_qlist.clear()
        smap_types = [x for x in self.smap_types if self.smap_types[x]["preset"] == preset]
        self.smaps_qlist.insertItems(smap_types)

    def clicked_input_dir_label(self, event):
        self.open_batch_process_dialog()

    def open_batch_process_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        folderpath =  QFileDialog.getExistingDirectory(self, 'Select Folder that contains subjects subdirectories')
        if folderpath:
            self.input_dir_label.setText(folderpath)

class SliderLabelDirectionDialog(QDialog):
    def __init__(self, smap_type, parameter_type, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"Select mouse behaviour for parameter {parameter_type}")
        layout = QVBoxLayout()

        title = QLabel(f"Select mouse behaviour for parameter {parameter_type}")

        self.combo = QComboBox()
        self.combo.addItem("Vertical")
        self.combo.addItem("Horizontal")
        layout.addWidget(title)
        layout.addWidget(self.combo)
        self.setLayout(layout)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.No
        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)

    def accept(self) -> None:
        self.direction = self.combo.currentText()
        super(SliderLabelDirectionDialog, self).accept()

    def reject(self) -> None:
        self.direction = None
        super(SliderLabelDirectionDialog, self).reject()