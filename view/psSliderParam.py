from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider, QButtonGroup, QPushButton


class PsSliderParam(QWidget):
    """
    Class defining slider QWidget comprehensive of slider name, activation checkbox and value label
    """
    def __init__(self,
                 label,
                 minv,
                 maxv,
                 value,
                 step,
                 mouse=None):
        super(PsSliderParam, self).__init__()

        self.label = label
        self.minv = minv
        self.maxv = maxv
        self.value = value
        self.step = step
        self.mouse = mouse


        self.setStyleSheet("margin: 0px; padding: 0px")
        self._compose_widget()

    def _compose_widget(self):
        font_size = 8
        layout = QHBoxLayout()
        self.setLayout(layout)

        # label
        labelQ = QLabel(self.label)
        labelQ.setFont(QFont('Arial', font_size))
        labelQ.setFixedWidth(55)

        # slider
        sliderQ = QSlider(Qt.Horizontal)
        sliderQ.setMinimum(self.minv)
        sliderQ.setMaximum(self.maxv)
        sliderQ.setTickInterval(self.step)
        sliderQ.setValue(self.value)

        # sliderQ.valueChanged.connect(functools.partial())

        # label value
        textQ = QLabel(str(self.value))
        textQ.setFont(QFont('Arial', font_size))
        textQ.setFixedWidth(40)

        # Vertical Horizontal
        self.v_button = QPushButton(" ↕ ")
        self.v_button.setContentsMargins(3,3,3,3)
        self.v_button.setStyleSheet("QPushButton:pressed { background-color: red }"
                                  "QPushButton:checked { background-color: red }")
        self.v_button.setCheckable(True)
        if self.mouse == "V":
            self.v_button.setChecked(True)
        self.v_button.hide()

        self.h_button = QPushButton(" ↔ ")
        self.h_button.setStyleSheet("QPushButton:pressed { background-color: red }"
                                  "QPushButton:checked { background-color: red }")
        self.h_button.setCheckable(True)
        if self.mouse == "H":
            self.h_button.setChecked(True)
        self.h_button.hide()

        layout.addWidget(labelQ)
        layout.addWidget(sliderQ)
        layout.addWidget(textQ)
        layout.addWidget(self.v_button)
        layout.addWidget(self.h_button)

        self.labelQ = labelQ
        self.sliderQ = sliderQ
        self.textQ = textQ

    def show_v_h_buttons(self, show):
        if show:
            self.v_button.show()
            self.h_button.show()
        else:
            self.v_button.hide()
            self.h_button.hide()
