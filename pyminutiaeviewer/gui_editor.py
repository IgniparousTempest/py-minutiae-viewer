import math
from pathlib import Path
from tkinter import W, N, E, StringVar, PhotoImage
from tkinter.ttk import Button, Label, LabelFrame

from overrides import overrides

from pyminutiaeviewer.gui_common import NotebookTabBase
from pyminutiaeviewer.minutia import Minutia, MinutiaType


class MinutiaeEditorFrame(NotebookTabBase):
    # TODO: I'd like to remove the <minutiae> parameter
    def __init__(self, parent, load_fingerprint_func, load_minutiae_func, save_minutiae_file):
        super(self.__class__, self).__init__(parent, load_fingerprint_func)

        self.root = parent

        self.minutiae_count = StringVar()

        self._update_minutiae_count()

        self.current_minutiae = None

        self.load_minutiae_btn = Button(self, text="Load Minutiae", command=load_minutiae_func)
        self.load_minutiae_btn.grid(row=1, column=0, sticky=N + W + E)

        self.export_minutiae_btn = Button(self, text="Export Minutiae", command=save_minutiae_file)
        self.export_minutiae_btn.grid(row=2, column=0, sticky=N + W + E)

        self.info_frame = InfoFrame(self, "Info", self.minutiae_count)
        self.info_frame.grid(row=3, column=0, padx=4, sticky=N + W + E)

    @overrides
    def load_fingerprint_image(self, image):
        self._update_minutiae_count()

    @overrides
    def load_minutiae_file(self):
        self._update_minutiae_count()

    def _update_minutiae_count(self):
        self.minutiae_count.set("Minutiae: {}".format(self.root.number_of_minutiae()))

    @overrides
    def on_canvas_mouse_left_click(self, event):
        """
        Adds a new bifurcation at the mouse click.
        """
        x, y = event.x, event.y
        if not self.root.is_point_in_canvas_image(x, y):
            return

        self.current_minutiae = ((x, y), MinutiaType.RIDGE_ENDING)

    @overrides
    def on_canvas_ctrl_mouse_left_click(self, event):
        """
        Adds a new ridge ending at the mouse click.
        """
        x, y = event.x, event.y
        if not self.root.is_point_in_canvas_image(x, y):
            return

        self.current_minutiae = ((x, y), MinutiaType.BIFURCATION)

    @overrides
    def on_canvas_mouse_right_click(self, event):
        """
        Removes a minutiae close to the mouse click.
        """
        x, y = event.x, event.y
        if not self.root.is_point_in_canvas_image(x, y):
            return

        scale_factor = self.root.canvas_image_scale_factor()
        x, y = x * scale_factor, y * scale_factor

        possible_minutiae = []

        for i in range(self.root.number_of_minutiae()):
            m = self.root.minutiae[i]
            dist = abs(m.x - x) + abs(m.y - y)
            if dist < 10:
                possible_minutiae.append((dist, i))

        # Sort ascending, in-place.
        possible_minutiae.sort(key=lambda tup: tup[0])

        if len(possible_minutiae) == 0:
            return
        else:
            del self.root.minutiae[possible_minutiae[0][1]]

        self.root.draw_minutiae()
        self._update_minutiae_count()

    @overrides
    def on_canvas_mouse_left_drag(self, event):
        """
        Sets the angle of the minutiae being placed.
        """
        x, y = event.x, event.y

        ((sx, sy), minutiae_type) = self.current_minutiae
        angle = math.degrees(math.atan2(y - sy, x - sx)) + 90

        minutia = Minutia(round(sx), round(sy), angle, minutiae_type, 1.0)

        self.root.draw_single_minutia(minutia)

    @overrides
    def on_canvas_mouse_left_release(self, event):
        """
        Places the minutiae currently being edited..
        """
        x, y = event.x, event.y

        scale_factor = self.root.canvas_image_scale_factor()

        ((px, py), minutiae_type) = self.current_minutiae
        angle = math.degrees(math.atan2(y - py, x - px)) + 90

        self.root.minutiae.append(Minutia(round(px * scale_factor), round(py * scale_factor), angle, minutiae_type, 1.0))
        self.current_minutiae = None

        self.root.draw_minutiae()
        self._update_minutiae_count()


class InfoFrame(LabelFrame):
    def __init__(self, parent, title, minutiae_count):
        super(self.__class__, self).__init__(parent, text=title)

        self.current_number_minutiae_label = Label(self, textvariable=minutiae_count)
        self.current_number_minutiae_label.grid(row=0, column=0, sticky=N + W + E)

        self.bifurcation_label = Label(self, text="Bifurcation (LMB):")
        self.bifurcation_label.grid(row=1, column=0, sticky=W)

        self.bifurcation_image = PhotoImage(file=Path(__file__).resolve().parent / 'images' / 'bifurcation_white.png')
        self.bifurcation_image_label = Label(self, image=self.bifurcation_image)
        self.bifurcation_image_label.grid(row=2, column=0, sticky=W)

        self.ridge_ending_label = Label(self, text="Ridge Ending (CTRL + LMB):")
        self.ridge_ending_label.grid(row=3, column=0, sticky=W)

        self.ridge_ending_image = PhotoImage(file=Path(__file__).resolve().parent / 'images' / 'ridge_ending_white.png')
        self.ridge_ending_image_label = Label(self, image=self.ridge_ending_image)
        self.ridge_ending_image_label.grid(row=4, column=0, sticky=W)
