import traceback
from tkinter import W, N, E, StringVar
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror
from tkinter.ttk import Button, Label

import math

from PIL import ImageTk

from pyminutiaeviewer.gui_common import NotebookTabBase, ControlsFrameBase, scale_image_to_fit_minutiae_canvas
from pyminutiaeviewer.minutia import Minutia, MinutiaType
from pyminutiaeviewer.minutiae_drawing import draw_minutiae
from pyminutiaeviewer.minutiae_encoder import MinutiaeEncoder
from pyminutiaeviewer.minutiae_reader import MinutiaeReader, MinutiaeFileFormat


class MinutiaeEditorFrame(NotebookTabBase):
    def __init__(self, parent):
        super(self.__class__, self).__init__(parent)

        self.minutiae_file_format = StringVar()
        self.minutiae_count = StringVar()

        self.minutiae = []

        controls = ControlsFrame(self, self.load_fingerprint_image, self.minutiae_file_format, self.load_minutiae_file,
                                 self.save_minutiae_file, self.minutiae_count)

        self.set_controls(controls)

        self._update_minutiae_count()

        self.current_minutiae = None
        self.image_canvas.bind("<Button-1>", self.click_set_ridge_ending)
        self.image_canvas.bind("<Control-Button-1>", self.click_set_bifurcation)
        self.image_canvas.bind("<B1-Motion>", self.click_select_angle)
        self.image_canvas.bind("<ButtonRelease-1>", self.click_add_minutiae)
        self.image_canvas.bind("<Button-3>", self.click_remove_minutia)

    def load_minutiae_file(self):
        file_path = askopenfilename(filetypes=(("NBIST minutiae file", '*.min'),
                                               ("All files", "*.*")))
        if file_path:
            reader = MinutiaeReader(MinutiaeFileFormat.NBIST)

            try:
                self.minutiae = reader.read(file_path)
                self.draw_minutiae()
                self._update_minutiae_count()
            except Exception as e:
                traceback.print_exc()
                showerror("Read Minutiae File", "There was an error in reading the minutiae file.\n\n"
                                                "The error message was:\n{}".format(e))

    def save_minutiae_file(self):
        file_path = asksaveasfilename(filetypes=(("NBIST minutiae file", '*.min'),
                                                 ("All files", "*.*")))
        if file_path:
            writer = MinutiaeEncoder(MinutiaeFileFormat.NBIST)

            try:
                self.minutiae = writer.write(file_path, self.minutiae, self.image_raw)
            except Exception as e:
                traceback.print_exc()
                showerror("Save Minutiae File", "There was an error in saving the minutiae file.\n\n"
                                                "The error message was:\n{}".format(e))

    def draw_single_minutia(self, minutia: Minutia):
        if self.image_minutiae is None:
            resized, _ = scale_image_to_fit_minutiae_canvas(self.image_canvas, self.image_raw)
            temp_image = draw_minutiae(resized, [minutia])
        else:
            temp_image = draw_minutiae(self.image_minutiae, [minutia])

        self.image = ImageTk.PhotoImage(temp_image)
        self.image_canvas.delete("IMG")
        self.image_canvas.create_image(0, 0, image=self.image, anchor=N + W, tags="IMG")
        self.update_idletasks()

    def _update_minutiae_count(self):
        self.minutiae_count.set("Minutiae: {}".format(len(self.minutiae)))

    def click_set_ridge_ending(self, event):
        x, y = event.x, event.y
        if x > self.image.width() or y > self.image.height():
            return

        self.current_minutiae = ((x, y), MinutiaType.RIDGE_ENDING)

    def click_set_bifurcation(self, event):
        x, y = event.x, event.y
        if x > self.image.width() or y > self.image.height():
            return

        self.current_minutiae = ((x, y), MinutiaType.BIFURCATION)

    def click_remove_minutia(self, event):
        x, y = event.x, event.y
        if x > self.image.width() or y > self.image.height():
            return

        scale_factor = self.image_raw.width / self.image.width()
        x, y = x * scale_factor, y * scale_factor

        possible_minutiae = []

        for i in range(len(self.minutiae)):
            m = self.minutiae[i]
            dist = abs(m.x - x) + abs(m.y - y)
            if dist < 10:
                possible_minutiae.append((dist, i))

        # Sort ascending, in-place.
        possible_minutiae.sort(key=lambda tup: tup[0])

        if len(possible_minutiae) == 0:
            return
        else:
            del self.minutiae[possible_minutiae[0][1]]

        self.draw_minutiae()
        self._update_minutiae_count()

    def click_select_angle(self, event):
        x, y = event.x, event.y

        ((sx, sy), minutiae_type) = self.current_minutiae
        angle = math.degrees(math.atan2(y - sy, x - sx)) + 90

        minutia = Minutia(round(sx), round(sy), angle, minutiae_type)

        self.draw_single_minutia(minutia)
        self._update_minutiae_count()

    def click_add_minutiae(self, event):
        x, y = event.x, event.y  # TODO: SCALE THIS

        scale_factor = self.image_raw.width / self.image.width()
        print(scale_factor)

        ((px, py), minutiae_type) = self.current_minutiae
        angle = math.degrees(math.atan2(y - py, x - px)) + 90

        self.minutiae.append(Minutia(round(px * scale_factor), round(py * scale_factor), angle, minutiae_type))
        self.current_minutiae = None

        self.draw_minutiae()
        self._update_minutiae_count()


class ControlsFrame(ControlsFrameBase):
    def __init__(self, parent, load_fingerprint_func, minutiae_format, load_minutiae_func, save_minutiae_func,
                 minutiae_count):
        super(self.__class__, self).__init__(parent, load_fingerprint_func)

        self.load_minutiae_btn = Button(self, text="Load Minutiae", command=load_minutiae_func)
        self.load_minutiae_btn.grid(row=1, column=0, sticky=N + W + E)

        self.export_minutiae_btn = Button(self, text="Export Minutiae", command=save_minutiae_func)
        self.export_minutiae_btn.grid(row=2, column=0, sticky=N + W + E)

        self.current_number_minutiae_label = Label(self, textvariable=minutiae_count)
        self.current_number_minutiae_label.grid(row=3, column=0, sticky=N + W + E)
