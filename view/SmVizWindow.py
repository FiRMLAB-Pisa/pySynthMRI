import os

import cv2
import pyqtgraph as pg
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGridLayout, QWidget, QLabel, QVBoxLayout, QGroupBox, QPushButton, QFileDialog, QHBoxLayout

import Config
from Config import T1
from model.SmModel import Orientation
from view.SmPageWindow import SmPageWindow
from view.custom_dialog import CustomParamDialog, SimpleMessageDialog
from view.nav_bar import NavBarSM
from view.slider_param import SliderParam
from utils.utils import waiting_effects


class SmVizWindow(SmPageWindow):
    """
    Pyqt Visualization Window. This window contains the synthesized image, parameters sliders and resulting
    model equation
    """

    def __init__(self, model, parent=None):
        super().__init__()
        self.model = model
        self.setWindowTitle("PySynthMRI")
        self.sliders_groups = []

    def show_ui(self):
        self.showMaximized()
        self.generalLayout = QGridLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        self.init_ui()

    def init_ui(self):
        self._create_menu_bar()
        self._create_display_img()
        self._create_dispay_options()
        self._set_init_image()

    def goToLogin(self):
        self.goto("login")

    def _create_menu_bar(self):
        menuBar = NavBarSM(self)
        self.setMenuBar(menuBar)

    def _create_display_img(self):
        data = self.model.original_synth_matrix
        if data is None:
            # we are synthetizing a new image from quantitatives
            t1 = self.model.get_mri_image_by_name(T1)
            # use t1 for stat image and dicom header
            self.model.load_file(t1.path)
            pi_synth = self.model.get_mri_image_by_name(self.model.get_map_type())
            pi_synth.image3d = t1.image3d
            pi_synth.is_loaded = True
            data = self.model.original_synth_matrix
        self.model.set_init_slicenum()

        # initialize the Slice views
        self.imgView = SliceView(self.model, Orientation.AXIAL, data.shape[2])
        self.generalLayout.addWidget(self.imgView, 0, 0)
        # self.generalLayout.addWidget(QLabel("LOCATION VALUE"), 1, 0)

    def _create_dispay_options(self):
        right_group = QWidget()
        right_group_layout = QVBoxLayout()
        right_group.setLayout(right_group_layout)
        self.generalLayout.addWidget(right_group, 0, 1)

        # SYNTHETIC IMAGE TYPE LABEL
        map_type_widget = QWidget()
        map_type_layout = QHBoxLayout()
        map_type_widget.setLayout(map_type_layout)
        self.map_type_text = QLabel(
            "<h2>" + self.model.get_map_type() + "<br>" + self.model.get_map_type(long_name=True) + "</h2>")
        self.map_type_text.setAlignment(Qt.AlignCenter)
        map_type_layout.addWidget(self.map_type_text)
        right_group_layout.addWidget(map_type_widget, alignment=Qt.AlignCenter)

        # SLIDERS PARAMETERS
        options_group = QGroupBox("Parameters:")
        options_group.setFont(QFont('Arial', 13))
        self.layout_options_group = QVBoxLayout()
        options_group.setLayout(self.layout_options_group)

        slider_groupQ = QWidget()
        self.slider_groupQ_layout = QVBoxLayout()
        slider_groupQ.setLayout(self.slider_groupQ_layout)
        self.layout_options_group.addWidget(slider_groupQ)

        self.sliders_groups = []
        self.options = Config.synth_parameters

        for opt in self.options:
            slider = SliderParam(self.options[opt], self)
            self.sliders_groups.append(slider)
        # add slice slider
        slice_opt = {
            "label": "Slice",
            "default": self.model.get_slice_num(Orientation.AXIAL) + 1,
            "min": 1,
            "max": self.model.getAxialSlice(),
            "step": 1,
            "value": self.model.get_slice_num(Orientation.AXIAL) + 1,
            "weight": -1,
            "enabled": False
        }
        slider = SliderParam(slice_opt, self)
        self.sliders_groups.append(slider)

        # sort by weight
        self.sliders_groups = sorted(self.sliders_groups, key=lambda slider: slider.get_weigth())
        for slider in self.sliders_groups:
            self.slider_groupQ_layout.addWidget(slider.get_group())

        # add ADD CUSTOM PARAM button
        self.custom_param_button = QPushButton("ADD PARAMETER")
        self.custom_param_button.setMaximumWidth(230)

        self.custom_param_button.clicked.connect(self.on_clicked_custom_param_button)
        self.layout_options_group.addWidget(self.custom_param_button, alignment=Qt.AlignCenter)

        # add equation label
        self.total_equation_qlabel = QLabel(
            "<h2><b>SYNTHMAP EQUATION</b><br>" + SliderParam.get_equation_string(self.sliders_groups) + "</h2>")
        self.total_equation_qlabel.setStyleSheet("border: 1px solid gray; padding: 4px;")
        self.total_equation_qlabel.setAlignment(Qt.AlignCenter)
        self.layout_options_group.addWidget(self.total_equation_qlabel)

        # BUTTONS LAYOUT
        buttons_group = QWidget()
        self.layout_buttons_group = QVBoxLayout()
        buttons_group.setLayout(self.layout_buttons_group)

        right_group_layout.addWidget(options_group)
        right_group_layout.addWidget(buttons_group)
        right_group_layout.addStretch(1)

    def _set_init_image(self):
        self.model.reset_synth_params()
        for sg in self.sliders_groups:
            sg.update_to_default_value()
        self.model.modify_syntetic_map()
        self.imgView.update()

    def on_change_dropdown_map(self, value):
        self.model.set_map_type(self.model.synth_maps[value])

        for sg in self.sliders_groups:
            sg.update_to_default_value()

    def on_clicked_custom_param_button(self):
        dlg = CustomParamDialog(self)
        if dlg.exec():
            self.model.synt_par[dlg.custom_param["label"]] = dlg.custom_param
            slider = SliderParam(dlg.custom_param, self)
            self.sliders_groups.append(slider)
            self.slider_groupQ_layout.addWidget(slider.get_group())

            self.total_equation_qlabel.setText(
                "<h2><b>SYNTHMAP EQUATION</b><br>" + SliderParam.get_equation_string(self.sliders_groups) + "</h2>")

            self.model.modify_syntetic_map(dims=2)
            self.imgView.update()
        else:
            print("Cancel!")

    # @waiting_effects
    def on_clicked_save_dicom_button(self):
        dir_path, filename = self._save_directory_dialog()
        if dir_path is None or filename is None:
            return
        self.model.modify_syntetic_map(dims=3)
        try:
            self.save_dicom(dir_path, filename)
            SimpleMessageDialog(title="Synthetic image saved!",
                                message="Filename:\n{}".format(os.path.normpath(os.path.join(dir_path, filename))))
        except FileExistsError:
            SimpleMessageDialog(title="ERROR: File already Exists!",
                                message="File already Exists!\nPlease save it again with a different name.")

    @waiting_effects
    def save_dicom(self, dir_path, filename):
        self.model.save_synthetic_image(dir_path, filename, "dicom")

    def on_clicked_save_niftii_button(self):
        dir_path, filename = self._save_directory_dialog()
        if dir_path is None or filename is None:
            return
        self.model.modify_syntetic_map(dims=3)
        try:
            self.model.save_synthetic_image(dir_path, filename, "niftii")
            SimpleMessageDialog(title="Synthetic image saved!",
                                message="Filename:\n{}".format(os.path.normpath(os.path.join(dir_path, filename))))
        except FileExistsError:
            SimpleMessageDialog(title="ERROR: File already Exists!",
                                message="File already Exists!\nPlease save it again with a different name.")

    def _save_directory_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        default_file_name = self.model.get_map_type() + "_mod"
        path = QFileDialog.getSaveFileName(self, 'Save File', default_file_name)

        if path != ('', ''):
            dir_path = os.path.dirname(path[0])
            filename = os.path.basename(path[0])
            enabled_synth_par = dict([(k, v) for k, v in self.model.synt_par.items() if v['enabled']])
            for type in enabled_synth_par:
                filename = filename + "_" + type + "_" + str(self.model.synt_par[type]["value"])
            print("Saving " + filename + " to: " + dir_path)
            return dir_path, filename
        return None, None

    def on_clicked_back_button(self):
        # model = SmModel()
        # self.register(SmVizWindow(self.model), "viz")
        for i in range(self.generalLayout.count()):
            layout_item = self.generalLayout.itemAt(i)
            self.generalLayout.removeItem(layout_item)
        self.model.reload_ui = False
        self.goto("search")

    def synth_image_menu_handler(self, map_type, selected):
        self.model.set_map_type(map_type)
        self.map_type_text.setText(
            "<h2>" + self.model.get_map_type() + "<br>" + self.model.get_map_type(long_name=True) + "</h2>")

        for sg in self.sliders_groups:
            sg.update_to_default_value()
        self.model.modify_syntetic_map(dims=2)
        self.imgView.update()

    def interpolation_menu_handler(self, interpolation):
        self.model.interpolation = interpolation
        self.imgView.update()

    def orientation_menu_handler(self, orientation):
        if orientation == Orientation.AXIAL:
            self.model.setAxial()
        elif orientation == Orientation.SAGITTAL:
            self.model.setSagittal()
        else:
            self.model.setCoronal()

        self.z_slider.setValue(self.model.get_slice_num(orientation) + 1)
        self.z_text.setText(str(self.model.get_slice_num(orientation) + 1))
        self.model.modify_syntetic_map(dims=2)
        self.imgView.update()

    def on_change_slider(self, opt_tuple, value):
        (checkbox, label, slider, text, eq) = opt_tuple
        type = label.text()
        if type == "Slice":
            self.model.set_slice_num(value - 1)
            text.setText(str(value))
            self.model.modify_syntetic_map(dims=2)
        elif type == "WW":
            self.model.original_synth_hdr.WindowWidth = value
            text.setText(str(value))
        elif type == "WL":
            self.model.original_synth_hdr.WindowCenter = value
            text.setText(str(value))
        else:
            text.setText(str(value))
            self.model.synt_par[type]["value"] = value
            self.model.modify_syntetic_map(dims=2)

        self.imgView.update()

    def on_change_checkbox(self, opt_tuple, state):
        (checkbox, label, slider, text, eq) = opt_tuple
        if state == Qt.Checked:
            slider.setEnabled(True)
            text.setText(str(slider.value()))
            self.options[label.text()]["enabled"] = True
        else:
            text.setText("N/A")
            slider.setEnabled(False)
            self.options[label.text()]["enabled"] = False
        self.total_equation_qlabel.setText(
            "<h2><b>SYNTHMAP EQUATION</b><br>" + SliderParam.get_equation_string(self.sliders_groups) + "</h2>")
        self.model.modify_syntetic_map(dims=2)
        self.imgView.update()

    def on_change_text(self, opt_tuple):
        pass

    def on_changed_z_text(self):
        try:
            value = int(self.z_text.text()) - 1
            self.model.set_slice_num(value)
            self.z_slider.setValue(value)
            self.imgView.update()
        except ValueError:
            print("[{}] ValueError: {} not valid format. Expect Int".format(__name__, self.z_text.text()))


class SliceView(QWidget):
    def __init__(self, model, sliceType, numSlices):
        super(SliceView, self).__init__()
        self.model = model
        self.sliceType = sliceType
        self.numSlices = numSlices
        self.canvas = PlotCanvas(self.model, sliceType, self)
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        self.setLayout(vbox)
        self.view = self.canvas.addViewBox()
        self.view.setAspectLocked(True)
        self.canvas.add_image(self.view)
        self.update()

    def update(self, figure=True, show_value=True):
        if figure:
            self.canvas.plot(self.model.get_2d_image())


class WindowScale:
    def __init__(self, sliceView):
        self.press = None
        self.curr_x = None
        self.curr_y = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.prev_x = None
        self.prev_y = None
        self.sliceView = sliceView
        self.update = sliceView.update
        self.model = sliceView.model

    def greyscale_factory(self, graphics_layout_widget):
        def on_press(event):
            glw = graphics_layout_widget
            # if event.inaxes != ax: return
            if event.currentItem is None:
                return
            # pos = glw.mapToScene(event.pos()[0], event.pos()[1])
            pos = event.pos()
            event.xdata, event.ydata = pos.x(), pos.y()
            event.xdata, event.ydata = round(event.xdata), round(event.ydata)
            self.press = event.xdata, event.ydata
            print(event.xdata, event.ydata)
            # self.x0, self.y0, self.prev_x, self.prev_y = self.press

        def on_release(event):
            self.press = None
            self.update()

        def on_motion(event):
            # if event.inaxes != ax:
            # self.update(figure=False, show_value=False)
            # return
            if self.press is None:
                self.model.mousePos = round(event.xdata), round(event.ydata)
                self.update(figure=False, show_value=True)
                return
            dx = round(event.xdata) - self.press[0]
            dy = round(event.ydata) - self.press[1]

            self.model.original_synth_hdr.WindowWidth -= dx
            if self.model.original_synth_hdr.WindowWidth >= self.model.maxWindowWidth:
                self.model.original_synth_hdr.WindowWidth = self.model.maxWindowWidth
            elif self.model.original_synth_hdr.WindowWidth <= self.model.minWindowWidth:
                self.model.original_synth_hdr.WindowWidth = self.model.minWindowWidth

            self.model.original_synth_hdr.WindowCenter -= dy
            if self.model.original_synth_hdr.WindowCenter >= self.model.maxWindowCenter:
                self.model.original_synth_hdr.WindowCenter = self.model.maxWindowCenter
            elif self.model.original_synth_hdr.WindowCenter <= self.model.minWindowCenter:
                self.model.original_synth_hdr.WindowCenter = self.model.minWindowCenter

            self.update()

        # fig = ax.get_figure()
        graphics_layout_widget.scene().sigMouseClicked.connect(on_press)
        # attach the call back
        # fig.canvas.mpl_connect('button_press_event', on_press)
        # fig.canvas.mpl_connect('button_release_event', on_release)
        # fig.canvas.mpl_connect('motion_notify_event', on_motion)

        # return the function
        return on_motion


class PlotCanvas(pg.GraphicsLayoutWidget):
    """Displays the image"""

    def __init__(self, model, sliceType, sliceView):
        self.model = model
        self.sliceType = sliceType
        self.text1 = None
        self.text2 = None
        pg.GraphicsLayoutWidget.__init__(self)
        # zp = WindowScale(sliceView)
        # figZoom = zp.greyscale_factory(self)

    def add_image(self, slice_view_view):
        self.img = pg.ImageItem()
        slice_view_view.addItem(self.img)

    # @timeit
    def plot(self, plotData):
        ww = self.model.original_synth_hdr.WindowWidth
        wc = self.model.original_synth_hdr.WindowCenter  # wl in radiant
        v_min = (wc - 0.5 * ww)
        v_max = (wc + 0.5 * ww)
        scale = self.model.scale
        interpolation = self.model.interpolation
        # print(wc, ww, v_min, v_max)
        # self.ax.cla()
        # self.ax.set_axis_off()
        data = plotData
        if interpolation == "linear":
            data = cv2.resize(data,
                              dsize=(round(data.shape[0] * self.model.scale), round(data.shape[1] * self.model.scale)),
                              interpolation=cv2.INTER_LINEAR)
        elif interpolation == "nn":
            data = cv2.resize(data,
                              dsize=(round(data.shape[0] * self.model.scale), round(data.shape[1] * self.model.scale)),
                              interpolation=cv2.INTER_NEAREST)
        elif interpolation == "bicubic":
            data = cv2.resize(data,
                              dsize=(round(data.shape[0] * self.model.scale), round(data.shape[1] * self.model.scale)),
                              interpolation=cv2.INTER_CUBIC)
        elif interpolation == "none":
            data = cv2.resize(data,
                              dsize=(round(data.shape[0] * self.model.scale), round(data.shape[1] * self.model.scale)))

        # For backward compatibility, image data is assumed to be in column-major order (column, row) by default.
        # However, most data is stored in row-major order (row, column)
        self.img.setImage(data.T, levels=(v_min, v_max))

    def plot_text(self, plotData, show_value):
        if self.text1 is not None:
            self.text1.remove()

        self.text1 = self.ax.text(x=10,
                                  y=10,
                                  s="WL: {} WW: {}".format(self.model.original_synth_hdr.WindowCenter,
                                                           self.model.original_synth_hdr.WindowWidth),
                                  color="firebrick")
        if show_value:
            if self.model.mousePos[0] >= plotData.shape[0]: return
            if self.model.mousePos[1] >= plotData.shape[1]: return
            if self.text2 is not None:
                self.text2.remove()
            value = str(round(plotData[self.model.mousePos[0], self.model.mousePos[1]], 2))
            self.text2 = self.ax.text(x=self.model.mousePos[0],
                                      y=self.model.mousePos[1],
                                      s="value: {}\nloc:({},{})".format(
                                          value,
                                          self.model.mousePos[0],
                                          self.model.mousePos[1]),
                                      color="firebrick")

        self.draw()
