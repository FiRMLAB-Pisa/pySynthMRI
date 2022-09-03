"""
only controller has write privileges over the model
"""
import logging
import math
from math import ceil

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QCursor
from PyQt5.QtWidgets import QApplication, QFrame

from model.psExceptions import NotLoadedMapError, NotSelectedMapError
from model.psModel import PsModel

log = logging.getLogger(__name__)


# log.setLevel(LOGGING_LVL)

class PsPoint:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def x(self):
        return self._x

    def y(self):
        return self._y


class PsCanvasController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.connect_handlers()
        self.last_pos = None
        self.last_pos_slice = None

    def connect_handlers(self):
        # synthetic image widget controller
        self.view.smap_view.canvas.c.mouse_wheel_sgn.connect(self.mouse_wheel_handler)
        self.view.smap_view.canvas.c.mouse_press_sgn.connect(self.mouse_press_handler)
        self.view.smap_view.canvas.c.mouse_release_sgn.connect(self.mouse_release_handler)
        self.view.smap_view.canvas.c.mouse_move_sgn.connect(self.mouse_move_handler)
        self.view.smap_view.canvas.c.keyboard_pressed_sgn.connect(self.keyboard_press_handler)
        self.view.smap_view.canvas.c.keyboard_released_sgn.connect(self.keyboard_release_handler)
        self.view.smap_view.canvas.c.focus_in_sgn.connect(self.focus_in_handler)
        self.view.smap_view.canvas.c.focus_out_sgn.connect(self.focus_out_handler)

    # CANVAS EVENTS
    def mouse_wheel_handler(self, event):
        if not self.model.is_sythetic_loaded():
            self.model.c.signal_update_status_bar.emit("Synthetic image not selected!")
            return
        scroll = event.angleDelta().y()
        if scroll > 0:
            # scrolling forward -> +1 slice
            new_slice = self.model.set_next_slice()
        elif scroll < 0:
            # scrolling backward -> -1 slice
            new_slice = self.model.set_previous_slice()
        else:
            return

        if self.model.slice_slider is None:
            return

        self.model.get_smap()
        slice_slider = self.model.slice_slider[self.model.get_orientation()]

        # avoid triggering onValueChanged
        slice_slider.sliderQ.blockSignals(True)
        slice_slider.sliderQ.setValue(new_slice)
        slice_slider.sliderQ.blockSignals(False)

        slice_slider.textQ.setText(str(new_slice + 1))
        slice_slider.value = new_slice
        try:
            self.model.recompute_smap()
        except NotLoadedMapError as e:
            self.model.c.signal_update_status_bar.emit(e.message)
            return
        except NotSelectedMapError as e:
            self.model.c.signal_update_status_bar.emit(e.message)
            return
        self.model.reload_all_images()

    def mouse_press_handler(self, event):
        self.view.smap_view.canvas.setFocus()
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            # parameters behavious overrides others (Ctrl+click)
            #log.debug("Ctrl+click")
            self.last_pos = self.start_pos = event.pos()
        else:
            mouse_behaviour = self.model.get_mouse_behaviour()
            if not self.model.is_sythetic_loaded():
                self.model.c.signal_update_status_bar.emit("Synthetic image not selected!")
                return
            if mouse_behaviour == PsModel.MouseBehaviour.WINDOW_SCALE:
                self.last_pos = event.pos()
                self.start_pos = self.last_pos
            elif mouse_behaviour == PsModel.MouseBehaviour.ZOOM:
                # self.last_pos = event.pos()
                self.model.set_anchor_point(event.pos())
            elif mouse_behaviour == PsModel.MouseBehaviour.SLICE:
                self.last_pos_slice = event.pos()
            elif mouse_behaviour == PsModel.MouseBehaviour.TRANSLATE:
                pass

    def mouse_release_handler(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            # parameters behavious overrides others (Ctrl+click)
            #log.debug("mouse_release_handler:Ctrl+click:")
            self.last_pos = self.start_pos = None
        else:
            mouse_behaviour = self.model.get_mouse_behaviour()
            if not self.model.is_sythetic_loaded():
                self.model.c.signal_update_status_bar.emit("Synthetic image not selected!")
                return
            if mouse_behaviour == PsModel.MouseBehaviour.WINDOW_SCALE:
                self.last_pos = None
                self.start_pos = None
            elif mouse_behaviour == PsModel.MouseBehaviour.ZOOM:
                self.last_pos = None
            elif mouse_behaviour == PsModel.MouseBehaviour.SLICE:
                self.last_pos_slice = None
            elif mouse_behaviour == PsModel.MouseBehaviour.TRANSLATE:
                self.last_pos = None


    def mouse_move_handler(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier and self.model.is_h_v_parameter_interaction():
            if self.last_pos is None:
                self.last_pos = event.pos()
            curr_pos = event.pos()
            delta_pos = curr_pos - self.last_pos

            h_param_delta = delta_pos.x()
            v_param_delta = -1*delta_pos.y()
            range_validate = 30
            h_validate = abs((curr_pos - self.start_pos).x()) > range_validate
            v_validate = abs((curr_pos - self.start_pos).y()) > range_validate

            perc_step = .005  # 2%
            v_param = self.model.get_smap().get_vertical_parameter()
            if v_param_delta != 0 and v_validate and v_param is not None:
                param = self.model.get_smap().get_scanner_parameters()[self.model.get_smap().get_vertical_parameter()]
                range_param = param["max"] - param["min"]
                if v_param_delta < 0:
                    v_param_delta_perc = -1*math.ceil(range_param * perc_step)
                elif v_param_delta > 0:
                    v_param_delta_perc = math.ceil(range_param * perc_step)
                self.model.modify_v_parameters_mouse(v_param_delta_perc)

            h_param = self.model.get_smap().get_horizontal_parameter()
            if h_param_delta != 0 and h_validate and h_param is not None:
                param = self.model.get_smap().get_scanner_parameters()[self.model.get_smap().get_horizontal_parameter()]
                range_param = param["max"] - param["min"]
                if h_param_delta < 0:
                    h_param_delta_perc = -1*math.ceil(range_param * perc_step)
                elif h_param_delta > 0:
                    h_param_delta_perc = math.ceil(range_param * perc_step)
                self.model.modify_h_parameters_mouse(h_param_delta_perc)

            self.last_pos = curr_pos

        else:
            mouse_behaviour = self.model.get_mouse_behaviour()
            if not self.model.is_sythetic_loaded():
                self.model.c.signal_update_status_bar.emit("Synthetic image not selected!")
                return
            if mouse_behaviour == PsModel.MouseBehaviour.WINDOW_SCALE:
                curr_pos = event.pos()
                delta_pos = self.last_pos - curr_pos

                delta_ww = delta_pos.x()
                delta_wc = delta_pos.y()

                ratio_ww = ceil(abs(curr_pos.x() - self.start_pos.x())*.1)
                ratio_wc = ceil(abs(curr_pos.y() - self.start_pos.y())*.1)
                if delta_ww != 0 or delta_wc != 0:
                    self.model.add_delta_window_scale(delta_ww=ceil(delta_ww * ratio_ww), delta_wc=ceil(delta_wc * ratio_wc))

                self.last_pos = curr_pos

            elif mouse_behaviour == PsModel.MouseBehaviour.ZOOM:
                if self.last_pos is None:
                    self.last_pos = event.pos()
                curr_pos = event.pos()
                delta_pos = curr_pos - self.last_pos

                zoom = delta_pos.y()
                if zoom > 0:
                    self.model.zoom_in()
                elif zoom < 0:
                    self.model.zoom_out()

                self.last_pos = curr_pos

            elif mouse_behaviour == PsModel.MouseBehaviour.SLICE:
                if self.last_pos_slice is None:
                    self.last_pos_slice = event.pos()
                curr_pos = event.pos()
                delta = curr_pos.y() - self.last_pos_slice.y()

                if delta > 0:
                    # scrolling forward -> +1 slice
                    new_slice = self.model.set_next_slice()
                elif delta < 0:
                    # scrolling backward -> -1 slice
                    new_slice = self.model.set_previous_slice()
                else:
                    return
                slice_slider = self.model.slice_slider[self.model.get_orientation()]

                # avoid triggering onValueChanged
                slice_slider.sliderQ.blockSignals(True)
                slice_slider.sliderQ.setValue(new_slice)
                slice_slider.sliderQ.blockSignals(False)

                slice_slider.textQ.setText(str(new_slice + 1))
                slice_slider.value = new_slice
                try:
                    self.model.recompute_smap()
                    self.model.reload_all_images()

                    self.last_pos_slice = curr_pos
                except NotSelectedMapError as e:
                    self.model.c.signal_update_status_bar.emit(e.message)

            elif mouse_behaviour == PsModel.MouseBehaviour.TRANSLATE:
                if self.last_pos is None:
                    self.last_pos = event.pos()

                curr_pos = event.pos()
                delta_pos = curr_pos - self.last_pos

                self.model.translate(delta_pos.x(), delta_pos.y())

                self.last_pos = curr_pos

    def keyboard_press_handler(self, event):
        if event.modifiers() & Qt.ControlModifier :
            if self.model.is_h_v_parameter_interaction():
                self.view.smap_view.setCursor(QCursor(QtGui.QPixmap(':cursors/center-of-gravity-32.png')))

    def keyboard_release_handler(self, event):
        if event.key() == Qt.Key_Control and self.model.is_h_v_parameter_interaction():
            behaviour_mouse = self.model.get_mouse_behaviour()
            if behaviour_mouse == self.model.MouseBehaviour.WINDOW_SCALE:
                self.view.smap_view.setCursor(QCursor(QtCore.Qt.CrossCursor))
            elif behaviour_mouse == self.model.MouseBehaviour.ZOOM:
                self.view.smap_view.setCursor(QCursor(QtGui.QPixmap(':cursors/zoom_cursor_w.png')))
            elif behaviour_mouse == self.model.MouseBehaviour.SLICE:
                self.view.smap_view.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            elif behaviour_mouse == self.model.MouseBehaviour.TRANSLATE:
                self.view.smap_view.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            else:
                self.view.smap_view.setCursor(QCursor(QtCore.Qt.ArrowCursor))

    def focus_in_handler(self, event):
        canvasFrame = self.view.qframes[1]
        canvasFrame.setFrameShadow(QFrame.Plain)
        pal = canvasFrame.palette()
        pal.setColor(QPalette.WindowText, QColor("red"))
        canvasFrame.setPalette(pal)
        print("get focus")

    def focus_out_handler(self, event):
        canvasFrame = self.view.qframes[1]
        canvasFrame.setFrameShadow(QFrame.Plain)
        pal = canvasFrame.palette()
        pal.setColor(QPalette.WindowText, QColor(170, 172, 191))
        canvasFrame.setPalette(pal)
        print("lost focus")
