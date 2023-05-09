import logging

from PyQt5.QtWidgets import QVBoxLayout, QLabel, QGroupBox, QHBoxLayout, QWidget, QLineEdit

log = logging.getLogger(__name__)


# log.setLevel(LOGGING_LVL)

class PsInfoWidget(QGroupBox):
    def __init__(self, title, model):
        super(PsInfoWidget, self).__init__(title=title)

        self.model = model
        self.setMaximumWidth(400)
        info_widget_layout = QHBoxLayout()
        self.setLayout(info_widget_layout)

        left_label_widget = QWidget()
        left_labels_layout = QVBoxLayout()
        left_label_widget.setLayout(left_labels_layout)

        smap_label = QLabel("Type: ")
        left_labels_layout.addWidget(smap_label)

        equation_label = QLabel("Equation: ")
        left_labels_layout.addWidget(equation_label)

        desc_smap_label = QLabel("Descr: ")
        left_labels_layout.addWidget(desc_smap_label)

        ww_label = QLabel("WW: ")
        left_labels_layout.addWidget(ww_label)

        wc_label = QLabel("WC: ")
        left_labels_layout.addWidget(wc_label)

        dims_label = QLabel("DIMS: ")
        left_labels_layout.addWidget(dims_label)

        right_label_widget = QWidget()
        right_labels_layout = QVBoxLayout()
        right_label_widget.setLayout(right_labels_layout)

        # edited labels
        self.smap_label = QLabel("")
        right_labels_layout.addWidget(self.smap_label)

        self.equation_label = QLabel("")
        right_labels_layout.addWidget(self.equation_label)

        self.desc_smap = QLabel("")
        right_labels_layout.addWidget(self.desc_smap)

        self.ww_label = QLineEdit("")
        right_labels_layout.addWidget(self.ww_label)

        self.wc_label = QLineEdit("")
        right_labels_layout.addWidget(self.wc_label)

        self.dims_label = QLabel("")
        right_labels_layout.addWidget(self.dims_label)

        info_widget_layout.addWidget(left_label_widget)
        info_widget_layout.addWidget(right_label_widget)
        info_widget_layout.addStretch(1)

    def update(self):
        try:
            smap = self.model.get_smap().get_map_type()
            equation_string = self.model.get_smap().get_equation_string()
            desc_smap = self.model.get_smap().get_title()
            ww = self.model.get_smap().get_window_width()
            wc = self.model.get_smap().get_window_center()
            dims = self.model.get_total_slice_num()

            self.smap_label.setText("{}".format(smap))
            self.equation_label.setText("{}".format(equation_string))
            self.desc_smap.setText("{}".format(desc_smap))
            self.ww_label.setText("{}".format(ww))
            self.wc_label.setText("{}".format(wc))
            self.dims_label.setText("{}x{}x{}".format(dims[0], dims[1], dims[2]))
        except ValueError:
            return
