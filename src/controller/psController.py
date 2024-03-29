"""
only controller has write privileges over the model
"""
import functools
import logging
import os
import sys

from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QCursor

from src.model.MRIImage import Orientation, Interpolation
from src.model.psExceptions import NotSelectedMapError, ConfigurationFilePermissionError
from src.model.psFileType import psFileType
from src.model.psModel import PsModel
from src.model.utils import get_unique_filename
from src.view.psCustomDialog import PsCustomSmapDialog, AboutDialog, ScreenshotDialog

log = logging.getLogger(__name__)


# log.setLevel(LOGGING_LVL)

class PsController:
    def __init__(self, model: PsModel, view):
        self.model = model
        self.view = view
        self.connect_handlers()


    def connect_handlers(self):
        # mainWindow
        self.view.keyPressEvent = self.on_keypressed

        # MENU BAR
        # File
        # load dicom image
        self.view.menu_bar.batch_load_dicom_action.triggered.connect(self.on_clicked_batch_load_dicom_button)
        self.view.c.signal_update_batch_qmap_path.connect(self.on_selected_path_batch_dialog_upload)

        # load niftii image
        self.view.menu_bar.batch_load_niftii_action.triggered.connect(self.on_clicked_batch_load_niftii_button)

        self.view.c.signal_update_qmap_path.connect(self.on_selected_path_dialog_upload)
        open_dicom_dir_actions = self.view.menu_bar.open_dicom_dir_actions
        for k_action in open_dicom_dir_actions:
            open_dicom_dir_actions[k_action].triggered.connect(
                functools.partial(self.on_clicked_open_dicom_button, k_action))

        # load niftii image
        open_niftii_dir_actions = self.view.menu_bar.open_niftii_dir_actions
        for k_action in open_niftii_dir_actions:
            open_niftii_dir_actions[k_action].triggered.connect(
                functools.partial(self.on_clicked_open_niftii_button, k_action))

        # save
        self.view.menu_bar.file_save_dicom_action.triggered.connect(self.on_clicked_save_dicom_button)

        self.view.menu_bar.file_save_niftii_action.triggered.connect(self.on_clicked_save_niftii_button)
        self.view.c.signal_saving_smap.connect(self.on_selected_path_dialog_save)
        # dicom tag changes
        self.view.c.signal_set_header_tag.connect(self.on_set_header_tag)

        # self.view.menu_bar.back_action.triggered.connect(self.on_clicked_back_button)
        self.view.menu_bar.exit_action.triggered.connect(self.on_clicked_exit_button)

        # self.view.menu_bar.settings_custom_param_action.triggered.connect(self.on_clicked_custom_param_button)


        # Preset change

        for preset_key in self.view.menu_bar.presets_actions:
            preset_action = self.view.menu_bar.presets_actions[preset_key]
            preset_action.triggered.connect(functools.partial(self.on_clicked_preset_menu, preset_key))

        # Synthetic map change
        for smap_key in self.view.menu_bar.synth_images_action:
            smap_action = self.view.menu_bar.synth_images_action[smap_key]
            smap_action.triggered.connect(functools.partial(self.on_clicked_synth_image_menu, smap_key))
        # custom smap
        # self.view.c.signal_custom_smap_added_to_navbar.connect(self.on_custom_smap_added)

        # orientation
        self.view.menu_bar.orientation_axial_action.triggered.connect(
            functools.partial(self.on_clicked_orientation_button, Orientation.AXIAL))
        self.view.menu_bar.orientation_sagittal_action.triggered.connect(
            functools.partial(self.on_clicked_orientation_button, Orientation.SAGITTAL))
        self.view.menu_bar.orientation_coronal_action.triggered.connect(
            functools.partial(self.on_clicked_orientation_button, Orientation.CORONAL))

        # orientation labels flag
        self.view.menu_bar.orientation_labels_action.triggered.connect(
            self.on_clicked_orientation_labels_button
        )

        # interpolation
        self.view.menu_bar.interpolation_none_action.triggered.connect(
            functools.partial(self.on_clicked_interpolation_button, Interpolation.NONE))
        self.view.menu_bar.interpolation_linear_action.triggered.connect(
            functools.partial(self.on_clicked_interpolation_button, Interpolation.LINEAR))
        self.view.menu_bar.interpolation_bicubic_action.triggered.connect(
            functools.partial(self.on_clicked_interpolation_button, Interpolation.BICUBIC))
        self.view.menu_bar.interpolation_nn_action.triggered.connect(
            functools.partial(self.on_clicked_interpolation_button, Interpolation.NN))

        # custom smap
        self.view.menu_bar.settings_custom_smap_action.triggered.connect(self.on_clicked_custom_smap_button)

        # batch process
        self.view.menu_bar.batch_process_action.triggered.connect(self.on_clicked_batch_process_button)
        # batch progress path selected
        self.view.c.signal_batch_progress_path.connect(self.on_selected_path_batch_process_dialog)  # TODO REMOVE
        self.view.c.signal_batch_progress_launch.connect(self.on_selected_launch_batch_process_dialog)

        # about
        self.view.menu_bar.about_action.triggered.connect(self.on_clicked_help_button)

        # TOOL BAR
        self.view.tool_bar.button_save_niftii.clicked.connect(self.on_clicked_save_niftii_button)
        self.view.tool_bar.button_save_dicom.clicked.connect(self.on_clicked_save_dicom_button)

        self.view.tool_bar.button_window_grayscale.clicked.connect(self.on_clicked_window_grayscale)
        self.view.tool_bar.button_window_grayscale_default.clicked.connect(self.on_clicked_window_grayscale_default)
        self.view.tool_bar.button_zoom.clicked.connect(self.on_clicked_zoom)
        self.view.tool_bar.button_save_param.clicked.connect(self.on_clicked_save_param)
        self.view.tool_bar.button_default_param.clicked.connect(self.on_clicked_default_param)
        self.view.tool_bar.button_reload_config.clicked.connect(self.on_clicked_reload_config)

        self.view.tool_bar.button_default_zoom.clicked.connect(self.on_clicked_default_zoom_and_translation)
        self.view.tool_bar.button_slicer.clicked.connect(self.on_clicked_slice)
        self.view.tool_bar.button_h_v_mouse.clicked.connect(self.on_clicked_v_h_mouse_parameter)
        self.view.tool_bar.button_screenshot.clicked.connect(self.on_clicked_screenshot)

        self.view.tool_bar.button_translate.clicked.connect(self.on_clicked_translate)
        # presets buttons
        # for preset_key in self.view.tool_bar.presets_buttons:
        #     preset_button = self.view.tool_bar.presets_buttons[preset_key]
        #     preset_button.clicked.connect(functools.partial(self.on_clicked_preset_button, preset_key))
        # synth images buttons
        for smap_key in self.view.tool_bar.synth_images_buttons:
            smap_button = self.view.tool_bar.synth_images_buttons[smap_key]
            smap_button.clicked.connect(functools.partial(self.on_clicked_synth_image_button, smap_key))

        # resize view
        self.view.c.signal_resize_window.connect(self.on_resize_window_handler)

        # SLIDERS
        self.model.c.signal_parameter_sliders_init_handlers.connect(self.on_sliders_init_handlers)

        qmaps = self.view.qmap_view
        for qmap_name in qmaps:
            qmaps[qmap_name].c.drop_event.connect(functools.partial(self.drag_event_handler, qmap_name))
            qmaps[qmap_name].c.colormap_changed_signal.connect(functools.partial(self.colormap_changed_handler, qmap_name))
            qmaps[qmap_name].c.invert_relaxation_map_signal.connect(functools.partial(self.invert_relaxation_handler, qmap_name))
            qmaps[qmap_name].c.colorbar_toggled_signal.connect(functools.partial(self.colorbar_toggled_handler, qmap_name))


        # preset changed from menubar image selection
        self.model.c.signal_preset_changed.connect(self.on_clicked_preset_menu)

        # INFO WIDGET
        self.view.info_widget.wc_label.editingFinished.connect(self.on_editing_finished_window_center)
        self.view.info_widget.ww_label.editingFinished.connect(self.on_editing_finished_window_width)

    def drag_event_handler(self, qmap_name, event):
        path = event.mimeData().text()
        if path.startswith("file:///"):
            path = path[8:]

        if os.path.isdir(path):
            # dicom folder
            log.debug("Drop DICOM folder: {}".format(path))
            self.model.update_qmap_path(qmap_name, path, psFileType.DICOM)
            self.view.tool_bar.autotoggle_smaps_buttons()

        elif os.path.isfile(path):
            if path.endswith(".nii"):
                log.debug("Drop NIFTII file: {}".format(path))
                self.model.update_qmap_path(qmap_name, path, psFileType.NIFTII)
                self.view.tool_bar.autotoggle_smaps_buttons()

    def colormap_changed_handler(self, qmap_name, colormap):
        self.model.update_qmap_colormap(qmap_name, colormap)

    def colorbar_toggled_handler(self, qmap_name):
        self.model.update_qmap_colorbar(qmap_name)

    def invert_relaxation_handler(self, qmap_name, inverted):
        self.model.invert_qmap(qmap_name, inverted)

    def on_keypressed(self, e):
        if e.key() == QtCore.Qt.Key_Control:
            if self.model.is_h_v_parameter_interaction():
                self.view.smap_view.canvas.setFocus()

    def on_clicked_batch_load_dicom_button(self):
        log.debug("on_clicked_batch_load_dicom_button.")
        self.view.open_dicom_batch_load_dialog()
        self.view.tool_bar.autotoggle_smaps_buttons()

    def on_clicked_batch_load_niftii_button(self):
        log.debug("on_clicked_batch_load_niftii_button.")
        self.view.open_niftii_batch_load_dialog()
        self.view.tool_bar.autotoggle_smaps_buttons()

    def on_clicked_open_dicom_button(self, qmap):
        log.debug("on_clicked_open_dicom_button: " + qmap)
        self.view.open_dicom_load_dialog(qmap)
        self.view.tool_bar.autotoggle_smaps_buttons()

    def on_clicked_open_niftii_button(self, qmap):
        log.debug("on_clicked_open_niftii_button: " + qmap)
        self.view.open_niftii_load_dialog(qmap)
        self.view.tool_bar.autotoggle_smaps_buttons()

    def on_selected_path_batch_dialog_upload(self, path, file_type):
        log.debug("on_selected_path_batch_dialog_upload: " + path + " - Type: " + file_type)
        # look into directory and search predefined file names of the quantitatives
        self.model.update_qmap_batch_path(path, file_type)

    def on_selected_path_dialog_upload(self, qmap, path, file_type):
        log.debug("on_selected_path_dialog_upload: " + qmap + " - " + path + " - Type: " + file_type)
        self.model.update_qmap_path(qmap, path, file_type)
        self.view.tool_bar.autotoggle_smaps_buttons()

    def on_clicked_save_dicom_button(self):
        log.debug("on_clicked_save_dicom_button")
        self.view.open_dicom_save_dialog()

    def on_clicked_save_niftii_button(self):
        log.debug("on_clicked_save_niftii_button")
        self.view.open_niftii_save_dialog()

    def on_selected_path_dialog_save(self, path, file_type):
        log.debug("on_selected_path_dialog_save: " + path + " - Type: " + file_type)
        self.model.save_smap(path, file_type)

    def on_set_header_tag(self, tag, value):
        log.debug("on_set_header_tag: " + tag + ": " + value)
        self.model.set_header_tag(tag, value)

    def on_clicked_back_button(self):
        log.debug("on_clicked_back_button")

    def on_clicked_exit_button(self):
        # self.model.appSM.quit()
        log.debug("on_clicked_exit_button")
        sys.exit()

    def on_clicked_custom_smap_button(self):
        log.debug("on_clicked_custom_smap_button")
        dlg = PsCustomSmapDialog()
        if dlg.exec():
            self.model.add_custom_smap(dlg.custom_smap)
            self.model.reload_smap()
            map_type = dlg.custom_smap["name"]
            self.view.add_custom_smap(map_type)

            smap_action = self.view.menu_bar.synth_images_action[map_type]
            smap_action.triggered.connect(functools.partial(self.on_clicked_synth_image_menu, map_type))

            smap_button = self.view.tool_bar.synth_images_buttons[map_type]
            smap_button.clicked.connect(functools.partial(self.on_clicked_synth_image_menu, map_type))

            # self.model.add_slide_parameter(dlg.custom_param)
            # self.model.modify_syntetic_map(dims=2)
            # self.model.update_image()
        else:
            log.debug("on_clicked_custom_smap_button: cancel operation")

    def on_clicked_batch_process_button(self):
        # select preset, images, output dir
        self.view.open_batch_process_info_dialog()
        # self.view.open_batch_process_dialog()

    def on_clicked_custom_param_button(self):
        log.debug("on_clicked_custom_param_button")

    def on_clicked_preset_menu(self, preset):
        log.debug(f"on_clicked_preset_menu: {preset}")
        self.model.set_current_preset(preset)
        self.view.tool_bar.hide_synth_images_btns_on_preset(preset)
        self.view.tool_bar.set_preset_label(preset)

    def on_clicked_synth_image_menu(self, map_type):
        log.debug("on_clicked_synth_image_menu")
        self.model.set_smap_type(map_type)
        self.model.reload_smap()
        self.view.tool_bar.activate_unique_smap_button(map_type)

    def on_clicked_preset_button(self, preset):
        log.debug(f"on_clicked_preset_button: {preset}")
        # TODO

    def on_clicked_synth_image_button(self, map_type):
        log.debug("on_clicked_synth_image_button")
        self.model.set_smap_type(map_type)
        self.model.reload_smap()
        self.view.menu_bar.activate_unique_smap_action(map_type)
        self.view.tool_bar.activate_unique_smap_button(map_type)
        self.view.tool_bar.toggle_toolbar_buttons(True)

    def on_clicked_orientation_button(self, orientation):
        log.debug("on_clicked_orientation_button - passed {}".format(orientation))
        self.model.set_orientation(orientation)

    def on_clicked_orientation_labels_button(self, value):
        self.model.set_orientation_labels_flag(value)
        self.model.reload_smap()

    def on_clicked_interpolation_button(self, interpolation):
        log.debug("on_clicked_interpolation_button - passed {}".format(interpolation))
        self.model.set_interpolation_type(interpolation)
        # viz_window.orientation_menu_handle

    def on_clicked_help_button(self):
        log.debug("on_clicked_help_button")
        dlg = AboutDialog()

        dlg.exec_()

    def on_resize_window_handler(self):
        self.model.reload_all_images()

    def on_sliders_init_handlers(self):
        log.debug("on_sliders_init_handlers")
        # connect handler slice slider
        # self.model.slice_slider.sliderQ.valueChanged.connect(
        #     functools.partial(self.on_change_parameter_slider, self.model.get_smap().map_type, "Slice"))
        for slider_key in self.model.slice_slider.keys():
            self.model.slice_slider[slider_key].sliderQ.valueChanged.connect(
                functools.partial(self.on_change_parameter_slider, self.model.get_smap().map_type, slider_key))

        # connect handlers to all parameters sliders
        parameters = self.model.get_smap().get_scanner_parameters()
        for parameter in parameters:
            slider = parameters[parameter]["slider"].sliderQ
            slider.valueChanged.connect(
                functools.partial(self.on_change_parameter_slider, self.model.get_smap().map_type, parameter))
            # label = parameters[parameter]["slider"].labelQ
            # label.mousePressEvent = lambda event: self.on_clicked_slider_label(event, self.model.get_smap().map_type, parameter)

            h_button = parameters[parameter]["slider"].h_button
            h_button.clicked.connect(
                functools.partial(self.on_clicked_h_mouse_parameter, self.model.get_smap().map_type, parameter))
            v_button = parameters[parameter]["slider"].v_button
            v_button.clicked.connect(
                functools.partial(self.on_clicked_v_mouse_parameter, self.model.get_smap().map_type, parameter))

    def disable_all_v_buttons(self, except_parameter):
        parameters = self.model.get_smap().get_scanner_parameters()
        for parameter in parameters:
            if parameter == except_parameter:
                parameters[parameter]["slider"].h_button.setChecked(False)
            else:
                parameters[parameter]["slider"].v_button.setChecked(False)

    def disable_all_h_buttons(self, except_parameter):
        parameters = self.model.get_smap().get_scanner_parameters()
        for parameter in parameters:
            if parameter == except_parameter:
                parameters[parameter]["slider"].v_button.setChecked(False)
            else:
                parameters[parameter]["slider"].h_button.setChecked(False)

    def on_clicked_h_mouse_parameter(self, smap_type, parameter_type, checked):
        if checked:
            self.disable_all_h_buttons(except_parameter=parameter_type)
            self.model.set_mouse_parameter(parameter_type, "h")
        else:
            self.model.set_mouse_parameter(None, "h")

    def on_clicked_v_mouse_parameter(self, smap_type, parameter_type, checked):
        if checked:
            self.disable_all_v_buttons(except_parameter=parameter_type)
            self.model.set_mouse_parameter(parameter_type, "v")
        else:
            self.model.set_mouse_parameter(None, "v")

    def on_change_parameter_slider(self, smap_type, parameter_type, value):
        # get correct sider
        if isinstance(parameter_type, Orientation):
            # TODO FIX BUG SLOW
            slice_slider = self.model.slice_slider[parameter_type]
            slice_slider.textQ.setText(str(value))
            slice_slider.value = value
            self.model.set_slice_num(value - 1, parameter_type)
            self.model.recompute_smap()
            self.model.reload_all_images()
        else:
            parameter = self.model.get_smap().get_scanner_parameters()[parameter_type]
            slider_widget = parameter["slider"]
            slider_widget.textQ.setText(str(value))
            self.model.set_smap_parameter_value(parameter_type, value)
            # self.model.modify_syntetic_map(dims=2)
            self.model.recompute_smap()
            self.model.reload_smap()
        # self.model.update_image()
        # print(smap_type, parameter)

    def on_clicked_window_grayscale(self):
        if self.view.tool_bar.button_window_grayscale.isChecked():
            self.view.tool_bar.button_zoom.setChecked(False)
            self.view.tool_bar.button_zoom.setStyleSheet("")
            self.view.tool_bar.button_slicer.setChecked(False)
            self.view.tool_bar.button_slicer.setStyleSheet("")
            self.view.tool_bar.button_translate.setChecked(False)
            self.view.tool_bar.button_translate.setStyleSheet("")
            self.view.tool_bar.button_window_grayscale.setStyleSheet('background-color: "red"')  # rgb(42, 130, 218)

            self.view.smap_view.setCursor(QCursor(QtCore.Qt.CrossCursor))
            self.model.set_mouse_behaviour(PsModel.MouseBehaviour.WINDOW_SCALE)
            self.view.smap_view.canvas.setFocus()
        else:
            self.view.tool_bar.button_window_grayscale.setChecked(True)  # stay checked

    def on_clicked_translate(self):
        if self.view.tool_bar.button_translate.isChecked():
            self.view.tool_bar.button_window_grayscale.setChecked(False)
            self.view.tool_bar.button_window_grayscale.setStyleSheet("")
            self.view.tool_bar.button_zoom.setChecked(False)
            self.view.tool_bar.button_zoom.setStyleSheet("")
            self.view.tool_bar.button_slicer.setChecked(False)
            self.view.tool_bar.button_slicer.setStyleSheet("")
            self.view.tool_bar.button_translate.setStyleSheet('background-color: "red"')  # rgb(42, 130, 218)
            self.view.smap_view.setCursor(QCursor(QtCore.Qt.SizeAllCursor))
            self.model.set_mouse_behaviour(PsModel.MouseBehaviour.TRANSLATE)
            self.view.smap_view.canvas.setFocus()
        else:
            self.view.tool_bar.button_translate.setChecked(True)  # stay checked

    def on_clicked_window_grayscale_default(self):
        try:
            self.model.get_smap().reset_widow_scale()
            self.model.reload_smap()
            self.model.c.signal_update_status_bar.emit("Window grayscale reset.")
            self.view.smap_view.canvas.setFocus()
        except NotSelectedMapError as e:
            self.model.c.signal_update_status_bar.emit(e.message)

    def on_clicked_zoom(self):
        if self.view.tool_bar.button_zoom.isChecked():
            self.view.smap_view.setCursor(QCursor(QtGui.QPixmap(':cursors/zoom_cursor_w.png')))
            self.view.tool_bar.button_window_grayscale.setChecked(False)
            self.view.tool_bar.button_window_grayscale.setStyleSheet("")
            self.view.tool_bar.button_slicer.setChecked(False)
            self.view.tool_bar.button_slicer.setStyleSheet("")
            self.view.tool_bar.button_translate.setChecked(False)
            self.view.tool_bar.button_translate.setStyleSheet("")
            self.view.tool_bar.button_zoom.setStyleSheet('background-color: "red"')  # rgb(42, 130, 218)
            self.model.set_mouse_behaviour(PsModel.MouseBehaviour.ZOOM)
            self.view.smap_view.canvas.setFocus()
        else:
            self.view.tool_bar.button_zoom.setChecked(True)  # stay checked

    def on_clicked_slice(self):
        if self.view.tool_bar.button_slicer.isChecked():
            self.view.tool_bar.button_window_grayscale.setChecked(False)
            self.view.tool_bar.button_window_grayscale.setStyleSheet("")
            self.view.tool_bar.button_zoom.setChecked(False)
            self.view.tool_bar.button_zoom.setStyleSheet("")
            self.view.tool_bar.button_translate.setChecked(False)
            self.view.tool_bar.button_translate.setStyleSheet("")
            self.view.tool_bar.button_slicer.setStyleSheet('background-color: "red"')  # rgb(42, 130, 218)
            self.view.smap_view.setCursor(QCursor(QtCore.Qt.SizeVerCursor))
            self.model.set_mouse_behaviour(PsModel.MouseBehaviour.SLICE)
            self.view.smap_view.canvas.setFocus()
        else:
            self.view.tool_bar.button_slicer.setChecked(True)  # stay checked

    def on_clicked_v_h_mouse_parameter(self, event):
        checked = self.view.tool_bar.button_h_v_mouse.isChecked()
        try:
            self.model.toggle_v_h_mouse_parameter(checked)

            if checked:
                self.model.set_h_v_parameter_interaction(True)
                self.view.tool_bar.button_h_v_mouse.setStyleSheet('background-color: "red"')  # rgb(42, 130, 218)
            else:
                self.model.set_h_v_parameter_interaction(False)
                self.view.tool_bar.button_h_v_mouse.setStyleSheet('')  # rgb(42, 130, 218)
                # self.view.parameter_graph_widget.hide()
            self.model.c.signal_update_status_bar.emit("Modify parameters using Ctrl+mouse.")
        except NotSelectedMapError as e:
            self.model.c.signal_update_status_bar.emit(e.message)

    def on_clicked_screenshot(self, event):
        # TODO SCREENSHOT
        if self.model.get_smap().is_loaded():
            old_orientation_labels_flag = self.model.get_smap().get_orientation_labels_flag()
            self.model.get_smap().set_orientation_labels_flag(False)
            old_interpolation_scale = self.model.interpolation["scale"]
            self.model.interpolation["scale"] = 8
            self.model.reload_smap()
            screenshot = self.model.get_screenshot_image()
            # ask user the output path
            screenshot_basename = self.model.get_smap().map_type[:-len(" - " + self.model.get_current_preset())] + ".png"
            screenshot_dlg = ScreenshotDialog(screenshot_basename)
            screenshot_dlg.exec_()
            filename = screenshot_dlg.screenshot_path
            # if file exist add incremental numeber to name
            filename = get_unique_filename(filename)
            if screenshot.save(filename,"PNG"):
                self.model.c.signal_update_status_bar.emit(f"Screenshot saved: {filename}")
            else:
                self.model.c.signal_update_status_bar.emit("[ERROR] Error saving screenshot")
            self.model.get_smap().set_orientation_labels_flag(old_orientation_labels_flag)
            self.model.interpolation["scale"] = old_interpolation_scale
            self.model.reload_smap()

    def on_clicked_save_param(self):
        try:
            self.model.save_parameters()
            self.view.smap_view.canvas.setFocus()
            self.model.c.signal_update_status_bar.emit("Scanner parameter saved.")
        except ConfigurationFilePermissionError as e:
            self.model.c.signal_update_status_bar.emit(e.message)

    def on_clicked_default_param(self):
        try:
            self.model.set_default_parameters()
            self.view.smap_view.canvas.setFocus()
            self.model.c.signal_update_status_bar.emit("Scanner parameter set to default values.")
        except NotSelectedMapError as e:
            self.model.c.signal_update_status_bar.emit(e.message)

    def on_clicked_reload_config(self):
        try:
            self.model.reload_configuration_file()
            self.view.smap_view.canvas.setFocus()
            self.model.c.signal_update_status_bar.emit("Configuration file correctly reloaded.")
        except KeyError as e:
            self.model.c.signal_update_status_bar.emit(str(e))

    def on_editing_finished_window_center(self):
        log.debug(f"on_editing_finished_window_center")
        if not self.model.is_sythetic_loaded():
            self.model.c.signal_update_status_bar.emit("Synthetic image not selected!")
            return
        try:
            value = float(self.view.info_widget.wc_label.text())
            self.model.set_manual_window_center(value)
            self.model.reload_smap()
            # self.model.c.signal_update_status_bar.emit("Window grayscale reset.")
        except NotSelectedMapError as e:
            self.model.c.signal_update_status_bar.emit(e.message)
        except ValueError as e:
            self.model.c.signal_update_status_bar.emit(str(e))

    def on_editing_finished_window_width(self):
        log.debug(f"on_editing_finished_window_width")
        if not self.model.is_sythetic_loaded():
            self.model.c.signal_update_status_bar.emit("Synthetic image not selected!")
            return
        try:
            value = float(self.view.info_widget.ww_label.text())
            self.model.set_manual_window_width(value)
            self.model.reload_smap()
            # self.model.c.signal_update_status_bar.emit("Window grayscale reset.")
        except NotSelectedMapError as e:
            self.model.c.signal_update_status_bar.emit(e.message)
        except ValueError as e:
            self.model.c.signal_update_status_bar.emit(str(e))

    def on_clicked_default_zoom_and_translation(self):
        self.model.translation_reset()
        self.model.zoom_reset()
        self.view.smap_view.canvas.setFocus()
        self.model.c.signal_update_status_bar.emit("Image position and zoom reset.")

    def on_selected_path_batch_process_dialog(self, path):  # TODO REMOVE
        log.debug(f"[REMOVE] on_selected_path_batch_progress_dialog: {path}")
        self.model.execute_batch_process(path)

    def on_selected_launch_batch_process_dialog(self, input_dir, preset, smaps, output_type):
        log.debug(f"on_selected_launch_batch_process_dialog: {input_dir} - {preset} - {smaps} - {output_type}")
        self.model.execute_batch_process(input_dir, preset, smaps, output_type)
