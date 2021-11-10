import functools

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider, QCheckBox


class SliderParam(QWidget):
    """
    Class defining slider QWidget comprehensive of slider name, activation checkbox and value label
    """
    def __init__(self, opt, sm_viz_window):
        super(SliderParam, self).__init__()
        self.label = opt["label"]
        self.minv = opt["min"]
        self.maxv = opt["max"]
        self.value = opt["value"]
        self.step = opt["step"]
        self.weight = opt["weight"]
        self.maps = opt["default_maps"] if "default_maps" in opt else []
        self.equation = opt["equation"] if "equation" in opt else None
        self.group = QWidget()
        self.sm_viz_window = sm_viz_window
        self._compose_widget()

    def _compose_widget(self):
        layout = QHBoxLayout()
        self.group.setLayout(layout)
        is_slicer = (self.label == "Slice")
        # disabling checkbox
        # label
        labelQ = QLabel(self.label)
        labelQ.setFont(QFont('Arial', 13))
        labelQ.setFixedWidth(55)
        # slider
        sliderQ = QSlider(Qt.Horizontal)
        sliderQ.setMinimum(self.minv)
        sliderQ.setMaximum(self.maxv)
        sliderQ.setTickInterval(self.step)
        sliderQ.setValue(self.value)
        # slider.valueChanged.connect(self.on_changed_slider)
        # label value
        textQ = QLabel(str(self.value))
        textQ.setFont(QFont('Arial', 13))
        textQ.setFixedWidth(40)

        # Equation label
        if not is_slicer and self.equation is not None:
            equationQ = None
            text_equation = self.format_equation()
            sliderQ.setToolTip("Equation:  " + text_equation)
            # equationQ = QLabel(text_equation)
            # equationQ.setFixedWidth(80)
        else:
            equationQ = None

        checkboxQ = None if is_slicer else QCheckBox()
        opt_tuple = (checkboxQ, labelQ, sliderQ, textQ, equationQ)
        # textQ.returnPressed.connect(functools.partial(self.on_change_text, opt_tuple))

        sliderQ.valueChanged.connect(functools.partial(self.sm_viz_window.on_change_slider, opt_tuple))

        # set initial checked box based on synth map
        if is_slicer:
            self.sm_viz_window.z_slider = sliderQ
            self.sm_viz_window.z_text = textQ
            self.sm_viz_window.z_label = self.label
        else:
            if self.sm_viz_window.model.get_map_type() in self.maps:
                checkboxQ.setChecked(True)
                self.sm_viz_window.model.synt_par[self.label]["enabled"] = True
            else:
                checkboxQ.setChecked(False)
                textQ.setText("N/A")
                sliderQ.setEnabled(False)
                self.sm_viz_window.model.synt_par[self.label]["enabled"] = False

            checkboxQ.stateChanged.connect(functools.partial(self.sm_viz_window.on_change_checkbox, opt_tuple))

        # append the widget to form a parameter modifier
        layout.addWidget(checkboxQ)
        layout.addWidget(labelQ)
        layout.addWidget(sliderQ)
        layout.addWidget(textQ)
        layout.addWidget(equationQ)

        self.checkboxQ = checkboxQ
        self.labelQ = labelQ
        self.sliderQ = sliderQ
        self.textQ = textQ
        self.equationQ = equationQ

    def get_group(self):
        return self.group

    def get_weigth(self):
        return self.weight

    def update_to_default_value(self):
        map = self.sm_viz_window.model.get_map_type()
        if self.checkboxQ is not None:
            if map in self.maps:
                self.checkboxQ.setChecked(True)
                self.sm_viz_window.model.synt_par[self.label]["enabled"] = True
            else:
                self.checkboxQ.setChecked(False)
                self.textQ.setText("N/A")
                self.sliderQ.setEnabled(False)
                self.sm_viz_window.model.synt_par[self.label]["enabled"] = False

    def update_slider_value(self, value):
        if self.checkboxQ is not None:
            self.checkboxQ.stateChanged.emit(value)

    def format_equation(self):
        offset = self.equation[0]
        scale = self.equation[1]
        map = self.equation[2]
        str_eq = ""

        if offset != 0:
            str_eq += "{}".format(offset)

        if isinstance(scale, str):
            if offset != 0:
                str_eq += "+{}*".format(scale)
            else:
                str_eq += "{}*".format(scale)
        else:
            if scale == 1:
                pass
            elif scale == -1:
                str_eq += "-"
            elif scale >= 0:
                str_eq += "+{}*".format(scale)
            else:
                str_eq += "-{}*".format(abs(scale))

        str_eq += "exp(-{}/{})".format(self.label, map)
        return str_eq

    @staticmethod
    def get_equation_string(slider_group):
        final_equation = ""
        for slider in slider_group:
            if slider.labelQ.text() != "Slice" and slider.checkboxQ is not None and slider.checkboxQ.isChecked():
                if final_equation == "":
                    final_equation = final_equation + "(" + slider.format_equation() + ")"
                else:
                    final_equation = final_equation + " * " + "(" + slider.format_equation() + ")"
        return final_equation
