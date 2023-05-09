from PyQt5 import QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg


class PsParameterGraph(PlotWidget):
    def __init__(self, model):
        self.model = model
        super(PsParameterGraph, self).__init__(enableMenu=False)
        self.showGrid(x=True, y=True)
        # self.setStyleSheet("border : 1px solid gray;"
        #                "padding : 5px;")
        self.scatter = pg.ScatterPlotItem(size=5)
        self.addItem(self.scatter)

        # self.setAspectLocked(True)
        self._disable_interaction()

        self.hide()
        self._connect_handlers()
        self._change_parameters()

    def _connect_handlers(self):
        self.model.c.signal_update_parameter_value_graph.connect(self._update_handler)
        self.model.c.signal_update_parameter_type_graph.connect(self._change_parameters)

    def _disable_interaction(self):
        self.mouseMoveEvent = lambda ev: ev.accept()
        self.mousePressEvent = lambda ev: ev.accept()
        self.mouseReleaseEvent = lambda ev: ev.accept()
        self.wheelEvent = lambda ev: ev.accept()

    def set_labels(self, x_label="Hour (H)", y_label="Temperature (°C)"):
        self.setLabel("left", y_label)
        self.setLabel("bottom", x_label)

    def set_ranges(self, x_range, y_range):
        self.setXRange(x_range[0], x_range[1])
        self.setYRange(y_range[0], y_range[1])

    def set_default_value(self, x, y):
        # self.scatter.clear()
        self.scatter.setData([{'pos': [x, y], 'data': 1,'brush': pg.mkBrush(30, 255, 35, 255)}])

    def set_value(self, x, y, x_default, y_default):
        self.scatter.setData([{'pos': [x_default, y_default],'brush': pg.mkBrush(30, 255, 35, 255)},
                              {'pos': [x, y], 'data': 2,'brush': pg.mkBrush(255, 0, 35, 255)}
                              ])

    def update(self, x, y, x_default, y_default):
        if x is not None and y is not None:
            self.set_value(x, y, x_default, y_default)

    def _update_handler(self):
        y_p_k = self.model.get_parameter("v")
        x_p_k = self.model.get_parameter("h")
        if y_p_k is not None and x_p_k is not None and self.model.is_h_v_parameter_interaction():
            self.scatter.clear()
            y_min, y_max, y_default, y_value, y_label = self.model.get_parameter_details("v")
            x_min, x_max, x_default, x_value, x_label = self.model.get_parameter_details("h")
            # self.scatter.clear()
            self.update(x_value, y_value, x_default, y_default)
            self.show()
        else:
            self.hide()

    def _change_parameters(self):
        y_p_k = self.model.get_parameter("v")
        x_p_k = self.model.get_parameter("h")
        if y_p_k is not None and x_p_k is not None and self.model.is_h_v_parameter_interaction():
            self.scatter.clear()
            x_min, x_max, x_default, x_value, x_label = self.model.get_parameter_details("h")
            y_min, y_max, y_default, y_value, y_label = self.model.get_parameter_details("v")
            #print(f"(x: {x_min}, {x_max}), {x_default}, {x_value}, {x_label}")
            self.set_labels(x_label, y_label)
            self.update(x_value, y_value, x_default, y_default)
            self.set_ranges((x_min, x_max), (y_min, y_max))
            # self.set_default_value(x_default, y_default)
            self.show()
        else:
            self.hide()