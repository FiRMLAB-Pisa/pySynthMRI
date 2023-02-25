import logging
import math
import os
from enum import Enum

from PyQt5.QtCore import QObject, pyqtSignal, QPoint
from PyQt5.QtWidgets import QApplication

from model.psExceptions import NotLoadedMapError, NotSelectedMapError
from model.psFileType import psFileType
from model.validateConfig import ValidateConfig
from model.MRIImage import Qmap, Smap, Orientation
from view.psSliderParam import PsSliderParam

log = logging.getLogger(__name__)


class ModelCommunicate(QObject):
    signal_qmap_updated = pyqtSignal(str)  # qmap_type
    signal_update_status_bar = pyqtSignal(str)  # message
    # signal_reload_images = pyqtSignal(str) # request to reload images (str cont which. "all" for all reload)
    signal_smap_updated = pyqtSignal(str)  # smap_type
    signal_custom_smap_added = pyqtSignal(str)
    signal_parameters_updated = pyqtSignal()
    signal_slice_slider_oriented = pyqtSignal(str)
    signal_preset_changed = pyqtSignal(str)

    signal_parameter_sliders_initialized = pyqtSignal()
    signal_parameter_sliders_init_handlers = pyqtSignal()

    signal_update_parameter_value_graph = pyqtSignal()
    signal_update_parameter_type_graph = pyqtSignal()


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

    def __init__(self):
        # Pyqt5 sygnal
        self.c = ModelCommunicate()
        # list of possible synthetic maps
        self.config = ValidateConfig()
        self._default_smaps = self.config.synth_types
        self._current_preset = self.config.default_preset
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
        self._h_v_parameter_interaction = False
        self._scaling_factor = 1  # synthesize image zoom

        self._anchor_point = QPoint(0, 0)
        self._translated_point = QPoint(0, 0)
        self._screenshot_image = None  # cached generated image fort screenshot

    def set_h_v_parameter_interaction(self, h_v_parameter_interaction):
        self._h_v_parameter_interaction = h_v_parameter_interaction
        self.c.signal_update_parameter_type_graph.emit()

    def is_h_v_parameter_interaction(self):
        return self._h_v_parameter_interaction

    def get_current_map_type(self):
        # current synthetic map type
        # return self.properties["curr_smap_type"]
        return self._smap.get_map_type()

    def has_missing_qmap(self, smap):
        for qmap in self._default_smaps[smap]["qmaps_needed"]:
            try:
                if not self._qmaps[qmap].is_loaded:
                    return True
            except KeyError:
                return True
        return False

    def update_qmap_batch_path(self, root_path, file_type):
        # foreach qmap defined in config.json
        for qmap_type in self._qmaps:
            file_regex_basename = self.config.qmap_types[qmap_type]["file_name"]
            for file_complete_basename in os.listdir(root_path):
                if file_regex_basename.lower() in file_complete_basename.lower():
                    path = os.path.join(root_path, file_complete_basename)
                    self.update_qmap_path(qmap_type, path, file_type)

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

    def update_qmap_colormap(self, qmap_k, colormap):
        log.debug(f"Update colormap to {colormap}")
        self._qmaps[qmap_k].set_colormap(colormap)
        self.reload_qmaps()

    def invert_qmap(self, qmap_k, inverted):
        log.debug(f"Inverted qmap {qmap_k} to {inverted}")
        self._qmaps[qmap_k].set_inverted(inverted)
        self.reload_qmaps()

    def get_qmap(self, qmap_type):
        return self._qmaps[qmap_type]

    def get_current_preset(self):
        return self._current_preset

    def set_current_preset(self, preset):
        self._current_preset = preset

    def get_preset_list(self):
        return self.config.presets

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

    def is_smap_synthesized(self):
        if self._smap.map_type:
            return True
        else:
            return False

    def get_series_number(self):
        return self._smap.get_series_number()

    def save_smap(self, path, file_type):
        if file_type == psFileType.NIFTII:
            self._smap.save_niftii(path)
        elif file_type == psFileType.DICOM:
            self._smap.save_dicom(path)

        self.c.signal_update_status_bar.emit(
            "{} map saved on {} in {} format.".format(self.get_smap().file_type, path, file_type))

    def set_header_tag(self, tag, value):
        self._smap.set_header_tag(tag, value)

    def get_smap_list(self):
        return self._default_smaps

    def get_qmap_matrix(self, qmap_type, dim):
        return self._qmaps[qmap_type].get_matrix(dim)

    def get_preset_list(self):
        return self.config.presets

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

    def set_orientation_labels_flag(self, orientation_labels_flag):
        self._smap.set_orientation_labels_flag(orientation_labels_flag)

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

    def set_screenshot_image(self, screenshot_image):
        self._screenshot_image = screenshot_image

    def get_screenshot_image(self):
        return self._screenshot_image

    def reload_all_images(self):
        # reaload qmaps
        self.reload_qmaps()
        # reload smap
        self.reload_smap()

    def reload_qmaps(self):
        qmap_types = self._qmaps.keys()
        for qmap_type in qmap_types:
            self.c.signal_qmap_updated.emit(qmap_type)

    def reload_smap(self):
        # global counter_reload
        # counter_reload +=1
        # log.debug("reload_smap #{}".format(counter_reload))
        self.c.signal_smap_updated.emit(self._smap.get_map_type())

    def recompute_smap(self):
        # PROFILELP
        # pr.enable()
        self._smap.recompute_smap()
        # pr.disable()
        # PROFILEPL

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
        self._smap.set_window_center(self._default_smaps[smap_type]["window_center"])
        self._smap.set_window_width(self._default_smaps[smap_type]["window_width"])
        self._smap.set_default_window_center(self._default_smaps[smap_type]["default_window_center"])
        self._smap.set_default_window_width(self._default_smaps[smap_type]["default_window_width"])
        self._smap.set_parameter(self._default_smaps[smap_type]["mouse_h"], "h")
        self._smap.set_parameter(self._default_smaps[smap_type]["mouse_v"], "v")
        self._smap.set_series_number(self._default_smaps[smap_type]["series_number"])

        # update preset
        self._current_preset = self._default_smaps[smap_type]['preset']
        self.c.signal_preset_changed.emit(self._current_preset)

        try:
            self.recompute_smap()
        except NotLoadedMapError as e:
            self.c.signal_update_status_bar.emit(e.message)
            return

        self.c.signal_parameters_updated.emit()
        self.c.signal_parameter_sliders_init_handlers.emit()
        # self.c.signal_slice_slider_oriented.emit(str(self._qmaps[list(self._qmaps.keys())[0]].get_orientation()))
        self.c.signal_slice_slider_oriented.emit(str(self.get_orientation()))

        self.c.signal_update_parameter_type_graph.emit()

        self.c.signal_update_status_bar.emit(" {} image synthesized.".format(smap_type))
        # self.c.signal_smap_updated.emit(smap_type)

    def set_smap_parameter_value(self, parameter_k, value):
        parameter = self.get_smap().get_scanner_parameters()[parameter_k]
        parameter["value"] = value
        self.c.signal_update_parameter_value_graph.emit()

    def save_parameters(self):
        # save all parameters
        smaps = self.get_smap_list()
        for smap_k in smaps:
            parameters = smaps[smap_k]["parameters"]
            # update model
            ww = smaps[smap_k]["window_width"]
            wc = smaps[smap_k]["window_center"]
            preset = smaps[smap_k]["preset"]
            self.update_config_strunct(parameters)
            # update config file

            self.update_config_file(preset, smap_k, parameters, ww, wc)

    def toggle_v_h_mouse_parameter(self, checked):
        for smap_k in self.get_smap_list():
            parameters = self.get_smap_list()[smap_k]['parameters']
            for param_k in parameters:
                parameters[param_k]['slider'].show_v_h_buttons(checked)

    def set_parameter_value(self, v_value, direction):
        v_value = self._smap.set_parameter_value(v_value, direction)
        if self.get_parameter("h") is not None and self.get_parameter_value("v") is not None:
            self.c.signal_update_parameter_value_graph.emit()
        return v_value

    def set_mouse_parameter(self, parameter_type, direction):
        self.get_smap().set_parameter(parameter_type, direction)
        self.c.signal_update_parameter_type_graph.emit()

    def get_parameter_details(self, direction):
        param = self.get_parameter(direction)
        if param is None:
            return None
        min = self.get_smap().get_scanner_parameters()[param]["min"]
        max = self.get_smap()._parameters[param]["max"]
        default = self.get_smap()._parameters[param]["default"]
        value = self.get_smap()._parameters[param]["value"]
        label = param
        return min, max, default, value, label

    def modify_mouse_parameters(self, h_param_delta, direction):
        parameter = self.get_parameter(direction)
        if parameter is not None:
            new_h_param = self.get_parameter_value(direction) + h_param_delta
            new_h_param = self.set_parameter_value(new_h_param, direction)
            slider = self._smap.get_parameter_slider(self._smap.get_parameter(direction))
            slider.sliderQ.setValue(new_h_param)

    def get_parameter_value(self, direction):
        return self._smap.get_parameter_value(direction)

    def get_parameter(self, direction: str):
        return self._smap.get_parameter(direction)

    def update_config_strunct(self, parameters):
        for p_name in parameters:
            p_value = parameters[p_name]["value"]
            parameters[p_name]['default'] = p_value

    def update_config_file(self, preset, map_type, parameters, ww=None, wc=None):

        return self.config.update_file(preset, map_type, parameters, ww, wc)

    def set_default_parameters(self):
        self._smap.set_default_scanner_parameters()
        self.recompute_smap()
        self.c.signal_parameters_updated.emit()

        # self.c.signal_parameter_sliders_init_handlers.emit()

    def reload_configuration_file(self):
        self.config = ValidateConfig()
        for smap_k in self.config.synth_types:
            smap_new_conf = self.config.synth_types[smap_k]
            if smap_k in self._default_smaps:
                # this smap already exists
                smap = self._default_smaps[smap_k]
                smap["title"] = smap_new_conf["title"]
                smap["equation"] = smap_new_conf["equation"]
                smap["preset"] = smap_new_conf["preset"]
                smap["equation_string"] = smap_new_conf["equation_string"]
                smap["qmaps_needed"] = smap_new_conf["qmaps_needed"]
                smap["window_width"] = smap_new_conf["window_width"]
                smap["window_center"] = smap_new_conf["window_center"]
                smap["default_window_center"] = smap_new_conf["window_center"]
                smap["default_window_width"] = smap_new_conf["window_width"]
                smap["series_number"] = smap_new_conf["series_number"]

                for param_k in smap["parameters"]:
                    # all stored smap
                    param = smap["parameters"][param_k]
                    new_param = smap_new_conf["parameters"][param_k]
                    param["label"] = new_param["label"]
                    param["value"] = new_param["value"]
                    param["min"] = new_param["min"]
                    param["max"] = new_param["max"]
                    param["step"] = new_param["step"]
                    param["default"] = new_param["default"]

            else:  # new smap
                self._default_smaps[smap_k] = smap_new_conf

        if self._smap.get_map_type():
            self.set_smap_type(self._smap.get_map_type())
            self._smap.set_default_scanner_parameters()
            self.recompute_smap()
            self.c.signal_parameters_updated.emit()
            self.c.signal_parameter_sliders_init_handlers.emit()
            self.c.signal_slice_slider_oriented.emit(str(self.get_orientation()))

            self.reload_smap()

    def set_manual_window_width(self, window_width):
        if isinstance(window_width, float):
            self._smap.set_window_width(window_width)
            self._default_smaps[self._smap.get_map_type()]["window_width"] = window_width

    def set_manual_window_center(self, window_center):
        if isinstance(window_center, float):
            self._smap.set_window_center(window_center)
            self._default_smaps[self._smap.get_map_type()]["window_center"] = window_center

    def add_delta_window_scale(self, delta_ww, delta_wc):
        if delta_ww != 0:
            try:
                ww = self._smap.add_delta_window_width(delta_ww)
                self._default_smaps[self._smap.get_map_type()]["window_width"] = ww
            except NotSelectedMapError as e:
                self.c.signal_update_status_bar.emit(e.message)
                return

        if delta_wc != 0:
            try:
                wc = self._smap.add_delta_window_center(delta_wc)
                self._default_smaps[self._smap.get_map_type()]["window_center"] = wc
            except NotSelectedMapError as e:
                self.c.signal_update_status_bar.emit(e.message)
                return
        self.reload_smap()

    def is_sythetic_loaded(self):
        return self._smap.np_matrix is not None

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
                                             sp["step"],
                                             sp["mouse"])

    def add_custom_smap(self, new_smap):
        for scanner_param in new_smap["parameters"]:
            sp = new_smap["parameters"][scanner_param]
            sp["slider"] = PsSliderParam(sp["label"],
                                         sp["min"],
                                         sp["max"],
                                         sp["value"],
                                         sp["step"],
                                         sp["mouse"])
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
        self._translated_point.setX(self._translated_point.x() + x)
        self._translated_point.setY(self._translated_point.y() + y)
        # self.reload_smap()
        self.reload_all_images()

    def get_translated_point(self):
        return self._translated_point

    def translation_reset(self):
        self._translated_point = QPoint(0, 0)

    def execute_batch_process(self, input_dir, preset, smaps, output_type):
        # iteratively select subject and synthesize images
        suject_paths = get_subdirs(input_dir)
        qmaps_path = None
        smaps_path = None
        for subject_path in suject_paths:
            # TODO this is not general
            try:
                exam_number = get_subdirs(get_subdirs(os.path.join(subject_path, "nifti"))[0])[0]
                exam_number = os.path.normpath(exam_number).split("\\")[-1]
                self._smap.set_header_tag("StudyID", exam_number)
                self._smap.set_header_tag("PatientID", "000")

                qmaps_path = os.path.join(
                    get_subdirs(get_subdirs(get_subdirs(os.path.join(subject_path, "nifti"))[0])[0])[0], 'qmap')
                qmaps_path = os.path.normpath(qmaps_path)
                smaps_path = os.path.join(
                    get_subdirs(get_subdirs(get_subdirs(os.path.join(subject_path, "nifti"))[0])[0])[0], 'smap')
                smaps_path = os.path.normpath(smaps_path)
            except FileNotFoundError as e:
                self.c.signal_update_status_bar.emit(f"Error processing input directory: {input_dir}")
                return

            #
            if not os.path.exists(smaps_path):
                os.makedirs(smaps_path)

            # load qmaps, compute all smaps, save smaps
            # 1 load qmaps
            self.update_qmap_batch_path(qmaps_path, file_type=psFileType.NIFTII)
            # 2 compute all smaps
            # get only preset
            smaps = {k: v for k, v in self._default_smaps.items() if k in smaps}

            for smap_k in smaps:
                self.c.signal_update_status_bar.emit(
                    f"Processing subject: {os.path.basename(subject_path)} - map: {smap_k}")
                QApplication.processEvents()
                # 1 load qmaps and generate smap

                self.c.signal_update_status_bar.emit("All Subjects processed.")

                self._smap.set_map_type(smap_k)
                self._smap.set_title(self._default_smaps[smap_k]["title"])
                self._smap.set_init_slices_num(self._qmaps[list(self._qmaps.keys())[0]])
                # self._smap.set_total_slice_num(self._qmaps[list(self._qmaps.keys())[0]].get_total_slice_num())
                self._smap.set_qmaps_needed(self._default_smaps[smap_k]["qmaps_needed"])
                self._smap.set_scanner_parameters(self._default_smaps[smap_k]["parameters"])
                self._smap.set_equation(self._default_smaps[smap_k]["equation"])
                self._smap.set_equation_string(self._default_smaps[smap_k]["equation_string"])
                self._smap.set_window_center(self._default_smaps[smap_k]["default_window_center"])
                self._smap.set_window_width(self._default_smaps[smap_k]["default_window_width"])
                self._smap.set_series_number(self._default_smaps[smap_k]["series_number"])

                self.recompute_smap()

                if output_type == psFileType.NIFTII:
                    self.save_smap(os.path.join(smaps_path, smap_k[:-len(" - " + self._current_preset)] + ".nii"),
                                   psFileType.NIFTII)  # TODO ERROR _current_preset!
                elif output_type == psFileType.DICOM:

                    self.save_smap(os.path.join(smaps_path, smap_k[:-len(" - " + self._current_preset)]),
                                   psFileType.DICOM)  # TODO ERROR _current_preset!

    def execute_batch_process_old(self, root_path):
        # iteratively select subject and synthesize images
        suject_paths = get_subdirs(root_path)
        for subject_path in suject_paths:
            try:
                # TODO this is not general
                qmaps_path = os.path.join(
                    get_subdirs(get_subdirs(get_subdirs(os.path.join(subject_path, "nifti"))[0])[0])[0], 'qmap')
                qmaps_path = os.path.normpath(qmaps_path)
                smaps_path = os.path.join(
                    get_subdirs(get_subdirs(get_subdirs(os.path.join(subject_path, "nifti"))[0])[0])[0], 'smap')
                smaps_path = os.path.normpath(smaps_path)
                if not os.path.exists(smaps_path):
                    os.makedirs(smaps_path)

                # load qmaps, compute all smaps, save smaps
                # 1 load qmaps
                self.update_qmap_batch_path(qmaps_path, file_type=psFileType.NIFTII)
                # 2 compute all smaps
                # get only preset
                smaps = {k: v for k, v in self._default_smaps.items() if v["preset"] == self._current_preset}

                for smap_k in smaps:
                    self.c.signal_update_status_bar.emit(
                        f"Processing subject: {os.path.basename(subject_path)} - map: {smap_k}")
                    QApplication.processEvents()
                    self._smap.set_map_type(smap_k)
                    self._smap.set_title(self._default_smaps[smap_k]["title"])
                    self._smap.set_init_slices_num(self._qmaps[list(self._qmaps.keys())[0]])
                    # self._smap.set_total_slice_num(self._qmaps[list(self._qmaps.keys())[0]].get_total_slice_num())
                    self._smap.set_qmaps_needed(self._default_smaps[smap_k]["qmaps_needed"])
                    self._smap.set_scanner_parameters(self._default_smaps[smap_k]["parameters"])
                    self._smap.set_equation(self._default_smaps[smap_k]["equation"])
                    self._smap.set_equation_string(self._default_smaps[smap_k]["equation_string"])
                    self._smap.set_series_number(self._default_smaps[smap_k]["series_number"])

                    self.recompute_smap()
                    self.save_smap(os.path.join(smaps_path, smap_k[:-len(" - " + self._current_preset)] + ".nii"),
                                   psFileType.NIFTII)
                self.c.signal_update_status_bar.emit("All Subjects processed.")
            except FileNotFoundError as e:
                self.c.signal_update_status_bar.emit(f"Error processing {e}")


def get_subdirs(path):
    return [d.path for d in os.scandir(path) if d.is_dir()]
