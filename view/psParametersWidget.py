import logging

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox

from model.MRIImage import Orientation

log = logging.getLogger(__name__)


# log.setLevel(LOGGING_LVL)

class PsParametersWidget(QWidget):

    def __init__(self, model):
        super(PsParametersWidget, self).__init__()
        self.model = model
        self.general_layout = QVBoxLayout()

        slice_slider_group = QWidget()
        self.slice_slider_layout = QVBoxLayout()
        slice_slider_group.setLayout(self.slice_slider_layout)
        self.general_layout.addWidget(slice_slider_group)

        self.parameters_sliders_group = QGroupBox("Parameters")
        self.parameters_sliders_layout = QVBoxLayout()
        self.parameters_sliders_group.setLayout(self.parameters_sliders_layout)
        self.general_layout.addWidget(self.parameters_sliders_group)

        self.slice_slider_layout.setSpacing(0)
        self.slice_slider_layout.setContentsMargins(0, 0, 0, 0)

        # self.general_layout.addStretch()

        self.setLayout(self.general_layout)

        self.connect_handlers()

    def connect_handlers(self):
        self.model.c.signal_parameters_updated.connect(self.reload_all_sliders)
        self.model.c.signal_slice_slider_oriented.connect(self.slice_slider_oriented)

    def slice_slider_oriented(self, orientation):
        try:
            if orientation == str(Orientation.AXIAL):
                self.model.slice_slider[Orientation.SAGITTAL].hide()
                self.model.slice_slider[Orientation.CORONAL].hide()
                self.model.slice_slider[Orientation.AXIAL].show()
            elif orientation == str(Orientation.SAGITTAL):
                self.model.slice_slider[Orientation.SAGITTAL].show()
                self.model.slice_slider[Orientation.CORONAL].hide()
                self.model.slice_slider[Orientation.AXIAL].hide()
            elif orientation == str(Orientation.CORONAL):
                self.model.slice_slider[Orientation.SAGITTAL].hide()
                self.model.slice_slider[Orientation.CORONAL].show()
                self.model.slice_slider[Orientation.AXIAL].hide()
        except TypeError:
            pass

    def reload_all_sliders(self):
        for i in reversed(range(self.slice_slider_layout.count())):
            x = self.slice_slider_layout.itemAt(i).widget()
            self.slice_slider_layout.removeWidget(x)
            x.setParent(None)
            # we need to remove connected slots
            try:
                x.sliderQ.valueChanged.disconnect()
            except Exception:
                pass
        for i in reversed(range(self.parameters_sliders_layout.count())):
            x = self.parameters_sliders_layout.itemAt(i).widget()
            self.parameters_sliders_layout.removeWidget(x)
            x.setParent(None)
            try:
                x.sliderQ.valueChanged.disconnect()
            except Exception:
                pass

        log.debug("update")
        smap = self.model.get_smap()

        slice_slider = self.model.slice_slider
        self.slice_slider_layout.insertWidget(self.slice_slider_layout.count(), slice_slider[Orientation.CORONAL])
        self.slice_slider_layout.insertWidget(self.slice_slider_layout.count(), slice_slider[Orientation.SAGITTAL])
        self.slice_slider_layout.insertWidget(self.slice_slider_layout.count(), slice_slider[Orientation.AXIAL])
        parameters = smap.get_scanner_parameters()
        for parameter in parameters:
            self.parameters_sliders_layout.insertWidget(self.parameters_sliders_layout.count(), parameters[parameter]["slider"])

