"""
only controller has write privileges over the model
"""
import logging

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

    # CANVAS EVENTS
    def mouse_wheel_handler(self, event):
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
        mouse_behaviour = self.model.get_mouse_behaviour()
        if mouse_behaviour == PsModel.MouseBehaviour.WINDOW_SCALE:
            self.last_pos = event.pos()
        elif mouse_behaviour == PsModel.MouseBehaviour.ZOOM:
            # self.last_pos = event.pos()
            self.model.set_anchor_point(event.pos())
        elif mouse_behaviour == PsModel.MouseBehaviour.SLICE:
            self.last_pos_slice = event.pos()
        elif mouse_behaviour == PsModel.MouseBehaviour.TRANSLATE:
            pass
        #     self.last_pos = event.pos()
        #     self.model.set_anchor_point(self.last_pos)

    def mouse_release_handler(self, event):
        mouse_behaviour = self.model.get_mouse_behaviour()
        if mouse_behaviour == PsModel.MouseBehaviour.WINDOW_SCALE:
            self.last_pos = None
        elif mouse_behaviour == PsModel.MouseBehaviour.ZOOM:
            self.last_pos = None
        elif mouse_behaviour == PsModel.MouseBehaviour.SLICE:
            self.last_pos_slice = None
        elif mouse_behaviour == PsModel.MouseBehaviour.TRANSLATE:
            self.last_pos = None

    def mouse_move_handler(self, event):
        DELTA_RATIO_WW_WC = 8
        mouse_behaviour = self.model.get_mouse_behaviour()
        if mouse_behaviour == PsModel.MouseBehaviour.WINDOW_SCALE:
            curr_pos = event.pos()
            delta_pos = curr_pos - self.last_pos

            delta_ww = -1*delta_pos.x()
            delta_wc = delta_pos.y()
            print(delta_ww, delta_wc)
            if delta_ww != 0:
                self.model.get_smap().add_delta_window_width(int(delta_ww * DELTA_RATIO_WW_WC))
                self.model.reload_smap()
            if delta_wc != 0:
                self.model.get_smap().add_delta_window_center(int(delta_wc * DELTA_RATIO_WW_WC))
                self.model.reload_smap()
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
