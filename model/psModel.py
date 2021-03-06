import logging
import math
from enum import Enum

from PyQt5.QtCore import QObject, pyqtSignal, QPoint

from model.psExceptions import NotLoadedMapError
from model.psFileType import psFileType
from model.validateConfig import ValidateConfig
from model.MRIImage import Qmap, Smap, Orientation
from view.psSliderParam import PsSliderParam

log = logging.getLogger(__name__)


# log.setLevel(LOGGING_LVL)


class ModelCommunicate(QObject):
    signal_qmap_updated = pyqtSignal(str)  # qmap_type
    signal_update_status_bar = pyqtSignal(str)  # message
    # signal_reload_images = pyqtSignal(str) # request to reload images (str cont which. "all" for all reload)
    signal_smap_updated = pyqtSignal(str)  # smap_type
    signal_custom_smap_added = pyqtSignal(str)
    signal_parameters_updated = pyqtSignal()
    signal_slice_slider_oriented = pyqtSignal(str)
    signal_parameter_sliders_initialized = pyqtSignal()
    signal_parameter_sliders_init_handlers = pyqtSignal()

# counter_reload = 0


class PsModel:
    """
    The model of the Application. It contains all the loaded data, generated images and choosen parameter values
    """

    class MouseBehaviour(Enum):
        NONE = 0
        WINDOW_SCALE = 1
        ZOOM = 2
        SLICE = 3
        TRANSLATE = 4

    def __init__(self, appSM):

        self.appSM = appSM
        # Pyqt5 sygnal
        self.c = ModelCommunicate()
        # list of possible synthetic maps
        self.config = ValidateConfig()
        self._default_smaps = self.config.synth_types

        self.generate_parameter_sliders()

        # self._default_smaps = [t for t in self.config.synth_types]
        # self._default_smaps = [t[0] for t in Config.synth_images]

        # qmaps
        self._qmaps = dict()
        for qmap in self.config.qmap_types:
            self._qmaps[qmap] = Qmap(map_type=qmap)

        # orientation
        self._orientation = Orientation.AXIAL  # default
        # synthetic imag`e
        self._smap = Smap(self._qmaps)
        self._smap.set_orientation(self._orientation)
        # selected_smap = list(self._default_smaps.keys())[0]
        # self._smap.set_map_type(selected_smap)
        # self._smap.set_title(self._default_smaps[selected_smap]["title"])

        # interpolation
        self.interpolation = self.config.image_interpolation



        # slice slider
        self.slice_slider = None
        # mouse behaviour [window scale, zoom]
        self._mouse_behaviour_type = self.MouseBehaviour.NONE

        self._scaling_factor = 1  # synthesize image zoom

        self._anchor_point = QPoint(0, 0)
        self._translated_point = QPoint(0, 0)

    def get_current_map_type(self):
        # current synthetic map type
        # return self.properties["curr_smap_type"]
        return self._smap.get_map_type()

    def update_qmap_path(self, qmap_type, path, file_type):
        # crate new map only if exist [TODO singleton]
        if qmap_type not in self._qmaps.keys():
            self._qmaps[qmap_type] = Qmap(map_type=qmap_type)
        self._qmaps[qmap_type].path = path
        self._qmaps[qmap_type].is_loaded = False
        self._qmaps[qmap_type].set_orientation(self._orientation)
        log.debug(
            "update_qmap_path: {} of qmap: {}".format(self._qmaps[qmap_type].path, self._qmaps[qmap_type].map_type))
        # a new path is choosen -> reload map
        try:
            if file_type == psFileType.DICOM:
                self._qmaps[qmap_type].load_from_dicom()
            elif file_type == psFileType.NIFTII:
                self._qmaps[qmap_type].load_from_niftii()
            else:
                return
            self._qmaps[qmap_type].is_loaded = True

            self.generate_slice_slider()
            # show map on GUI
            self.c.signal_qmap_updated.emit(qmap_type)
            self.c.signal_update_status_bar.emit("{} map correctly loaded".format(qmap_type))
        except:
            self.c.signal_update_status_bar.emit(
                "{} map CANNOT BE loaded. Check again path: {}".format(qmap_type, path))

    def get_qmap(self, qmap_type):
        return self._qmaps[qmap_type]

    def get_qmap_types(self):
        return self.config.qmap_types

    def get_total_slice_num(self):
        # return max slices num (x,y,z)
        for qmap in self._qmaps.keys():
            if self._qmaps[qmap].is_loaded:
                return self._qmaps[qmap].get_matrix_shape()
        return 0, 0, 0

    def get_smap(self):
        return self._smap

    def save_smap(self, path, file_type):
        if file_type == psFileType.NIFTII:
            self._smap.save_niftii(path)
        elif file_type == psFileType.DICOM:
            self._smap.save_dicom(path)

        self.c.signal_update_status_bar.emit(
            "{} map saved on {} in {} format.".format(self.get_smap().file_type, path, file_type))

    def get_smap_list(self):
        return self._default_smaps

    def get_qmap_matrix(self, qmap_type, dim):
        return self._qmaps[qmap_type].get_matrix(dim)

    def set_orientation(self, orientation):
        # set all orientation
        self._orientation = orientation
        self._smap.set_orientation(orientation)
        for k_qmap in self._qmaps:
            self._qmaps[k_qmap].set_orientation(orientation)
        # show only oriented slice slider
        try:
            self.c.signal_slice_slider_oriented.emit(str(orientation))
            self.recompute_smap()
            self.reload_all_images()
        except NotLoadedMapError as e:
            log.debug(e.message)

    def get_orientation(self):
        return self._orientation
        # for qmap in self._qmaps.keys():
        #     if self._qmaps[qmap].is_loaded:
        #         return self._qmaps[qmap].get_orientation()

    def set_interpolation_type(self, interpolation_type):
        self.interpolation["interpolation_type"] = interpolation_type
        self.reload_smap()

    def set_mouse_behaviour(self, behaviour_mouse: MouseBehaviour):
        self._mouse_behaviour_type = behaviour_mouse
        if behaviour_mouse == self.MouseBehaviour.WINDOW_SCALE:
            behavior = "Window Scale"
        elif behaviour_mouse == self.MouseBehaviour.ZOOM:
            behavior = "Zoom"
        elif behaviour_mouse == self.MouseBehaviour.SLICE:
            behavior = "Sclicer"
        elif behaviour_mouse == self.MouseBehaviour.TRANSLATE:
            behavior = "Translate"
        else:
            behavior = "Standard"
        self.c.signal_update_status_bar.emit("Mouse behaviour set to {}".format(behavior))

    def get_mouse_behaviour(self):
        return self._mouse_behaviour_type

    def is_window_scale_behaviour_mouse(self):
        return self._mouse_behaviour_type == self.MouseBehaviour.WINDOW_SCALE

    def is_zoom_behaviour_mouse(self):
        return self._mouse_behaviour_type == self.MouseBehaviour.ZOOM

    def is_slice_behaviour_mouse(self):
        return self._mouse_behaviour_type == self.MouseBehaviour.SLICE

    def is_translate_behaviour_mouse(self):
        return self._mouse_behaviour_type == self.MouseBehaviour.TRANSLATE

    def set_anchor_point(self, point):
        self._anchor_point = point

    def get_anchor_point(self):
        return self._anchor_point

    def reload_all_images(self):
        # reaload qmaps
        qmap_types = self._qmaps.keys()
        for qmap_type in qmap_types:
            self.c.signal_qmap_updated.emit(qmap_type)
        # reload smap
        self.reload_smap()

    def reload_smap(self):
        # global counter_reload
        # counter_reload +=1
        # log.debug("reload_smap #{}".format(counter_reload))
        self.c.signal_smap_updated.emit(self._smap.get_map_type())

    def recompute_smap(self):
        self._smap.recompute_smap()
        # self.c.signal_smap_updated.emit(self._smap.get_map_type())

    def set_smap_type(self, smap_type):
        log.debug(__name__)
        # import gc
        # print(len(gc.get_objects()))
        # gc.collect()
        # print(len(gc.get_objects()))
        self._smap.set_map_type(smap_type)
        self._smap.set_title(self._default_smaps[smap_type]["title"])
        self._smap.set_init_slices_num(self._qmaps[list(self._qmaps.keys())[0]])
        # self._smap.set_total_slice_num(self._qmaps[list(self._qmaps.keys())[0]].get_total_slice_num())
        self._smap.set_qmaps_needed(self._default_smaps[smap_type]["qmaps_needed"])
        self._smap.set_scanner_parameters(self._default_smaps[smap_type]["parameters"])
        self._smap.set_equation(self._default_smaps[smap_type]["equation"])
        self._smap.set_equation_string(self._default_smaps[smap_type]["equation_string"])

        try:
            self.recompute_smap()
        except NotLoadedMapError as e:
            self.c.signal_update_status_bar.emit(e.message)
            return

        self.c.signal_parameters_updated.emit()
        self.c.signal_parameter_sliders_init_handlers.emit()
        # self.c.signal_slice_slider_oriented.emit(str(self._qmaps[list(self._qmaps.keys())[0]].get_orientation()))
        self.c.signal_slice_slider_oriented.emit(str(self.get_orientation()))
        self.c.signal_update_status_bar.emit(" {} image synthesized.".format(smap_type))
        # self.c.signal_smap_updated.emit(smap_type)

    def set_default_parameters(self):
        self._smap.set_default_scanner_parameters()
        self.recompute_smap()
        self.c.signal_parameters_updated.emit()

        # self.c.signal_parameter_sliders_init_handlers.emit()

    def set_slice_num(self, slice_num, coordinate=None):
        self._smap.set_slice_num(slice_num, coordinate)
        # for k_qmap in self._qmaps:
        #     self._qmaps[k_qmap].set_slice_num(slice_num)

    def set_next_slice(self):
        new_slice = self._smap.set_next_slice()
        # for k_qmap in self._qmaps:
        #     self._qmaps[k_qmap].set_next_slice()
        return new_slice

    def set_previous_slice(self):
        new_slice = self._smap.set_previous_slice()
        # for k_qmap in self._qmaps:
        #     self._qmaps[k_qmap].set_previous_slice()
        return new_slice

    def generate_slice_slider(self):
        if self.slice_slider is None:
            self.slice_slider = dict()
            self.slice_slider[Orientation.CORONAL] = PsSliderParam(label="Coronal",
                                                                   minv=1,
                                                                   maxv=self.get_total_slice_num()[0],
                                                                   value=math.floor(self.get_total_slice_num()[0] / 2),
                                                                   step=1)
            self.slice_slider[Orientation.SAGITTAL] = PsSliderParam(label="Sagittal",
                                                                    minv=1,
                                                                    maxv=self.get_total_slice_num()[1],
                                                                    value=math.floor(self.get_total_slice_num()[1] / 2),
                                                                    step=1)
            self.slice_slider[Orientation.AXIAL] = PsSliderParam(label="Axial",
                                                                 minv=1,
                                                                 maxv=self.get_total_slice_num()[2],
                                                                 value=math.floor(self.get_total_slice_num()[2] / 2),
                                                                 step=1)

    def generate_parameter_sliders(self):
        # add sliders to default map (one for each map/parameter)
        for default_smap in self._default_smaps:
            parameters = self._default_smaps[default_smap]["parameters"]
            for scanner_param in parameters:
                sp = parameters[scanner_param]
                sp["slider"] = PsSliderParam(sp["label"],
                                             sp["min"],
                                             sp["max"],
                                             sp["value"],
                                             sp["step"])

    def add_custom_smap(self, new_smap):
        for scanner_param in new_smap["parameters"]:
            sp = new_smap["parameters"][scanner_param]
            sp["slider"] = PsSliderParam(sp["label"],
                                         sp["min"],
                                         sp["max"],
                                         sp["value"],
                                         sp["step"])
        self.config.validate_equation(new_smap)
        self._default_smaps[new_smap["name"]] = new_smap
        # self.c.signal_custom_smap_added.emit(new_smap["name"])
        self.set_smap_type(new_smap["name"])

    def zoom_in(self):
        self._scaling_factor *= 1.02
        # self.reload_smap()
        self.reload_all_images()

    def zoom_out(self):
        self._scaling_factor *= 0.98
        # self.reload_smap()
        self.reload_all_images()

    def zoom_reset(self):
        self._scaling_factor = 1
        # self.reload_smap()
        self.reload_all_images()

    def get_zoom(self):
        return self._scaling_factor

    def translate(self, x, y):
        self._translated_point.setX(self._translated_point.x()+x)
        self._translated_point.setY(self._translated_point.y()+y)
        # self.reload_smap()
        self.reload_all_images()

    def get_translated_point(self):
        return self._translated_point

    def translation_reset(self):
        self._translated_point = QPoint(0,0)