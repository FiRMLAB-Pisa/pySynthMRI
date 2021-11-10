from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QGroupBox, QFormLayout, QLineEdit, \
    QTextEdit, QWidget, QHBoxLayout, QComboBox

import Config


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


class SelectImageTypeDialog(QDialog):
    def __init__(self, title="", message="", images=""):
        super().__init__()
        self.images = images
        self.choosen_map = images[0]
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

        # MAP TYPE DROPDOWN
        select_map_group = QWidget()
        layout_maptype_group = QHBoxLayout()
        select_map_group.setLayout(layout_maptype_group)
        dropdown_maptype = QComboBox()
        for syth_map in images:
            dropdown_maptype.addItem(syth_map)
        layout_maptype_group.addWidget(dropdown_maptype, alignment=Qt.AlignCenter)
        dropdown_maptype.currentIndexChanged.connect(self.on_change_dropdown_map)
        self.layout.addWidget(select_map_group)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.exec()

    def on_change_dropdown_map(self, value):
        # update all sliders
        self.choosen_map = self.images[value]


class CustomParamDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._create_form_group_box()
        self.custom_param = dict()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.add_new_custom_par)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.formEquationBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Add custom parameter")
        self.setWindowFlags(self.windowFlags()  # reuse initial flags
                            & ~Qt.WindowContextHelpButtonHint  # negate the flag you want to unset
                            )

    def _create_form_group_box(self):
        self.formGroupBox = QGroupBox("Slider parameters:")
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
        self.formGroupBox.setLayout(layout)

        self.formEquationBox = QGroupBox("Equation parameters: ")
        self.formEquationBox.setToolTip("""Equation form:\n[ offset + scale * exp(-par/map) ]
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
        self.formEquationBox.setLayout(layout_eq)

    def add_new_custom_par(self):
        try:
            self.custom_param = {"label": self.label_edit_edit.text() if self.label_edit_edit.text() != "" else None,
                                 "default": int(self.default_edit.text()) if self.default_edit.text() != "" else None,
                                 "min": int(self.min_edit.text()) if self.min_edit.text() != "" else None,
                                 "max": int(self.max_edit.text()) if self.max_edit.text() != "" else None,
                                 "step": int(self.step_edit.text()) if self.step_edit.text() != "" else None,
                                 "value": int(self.default_edit.text()) if self.default_edit.text() != "" else None,
                                 "weight": 10,
                                 "enabled": False}
            offset = int(self.offset_edit.text()) if self.offset_edit.text() != "" else None
            # check scalar scale
            if self.scale_edit.text() == "":
                return
            else:
                if self.scale_edit.text() in [Config.T1, Config.T2, Config.PD]:
                    scale = self.scale_edit.text()
                else:
                    scale = int(self.scale_edit.text())
            map = self.map_edit.text() if self.map_edit.text() in [Config.T1, Config.T2,
                                                                   Config.PD] else None
            self.custom_param["equation"] = [offset, scale, map]
        except:
            return

        if self.validate():
            self.accept()

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
