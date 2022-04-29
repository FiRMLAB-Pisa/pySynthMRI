from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider


class PsSliderParam(QWidget):
    """
    Class defining slider QWidget comprehensive of slider name, activation checkbox and value label
    """
    def __init__(self,
                 label,
                 minv,
                 maxv,
                 value,
                 step):
        super(PsSliderParam, self).__init__()

        self.label = label
        self.minv = minv
        self.maxv = maxv
        self.value = value
        self.step = step



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

        layout.addWidget(labelQ)
        layout.addWidget(sliderQ)
        layout.addWidget(textQ)

        self.labelQ = labelQ
        self.sliderQ = sliderQ
        self.textQ = textQ

