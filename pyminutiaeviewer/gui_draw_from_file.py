import traceback
from tkinter import W, N, E, StringVar
from tkinter.filedialog import askopenfilename, sys
from tkinter.messagebox import showerror
from tkinter.ttk import Button, Label, Radiobutton

from PIL import ImageTk

from pyminutiaeviewer.gui_common import scale_image_to_fit_minutiae_canvas, NotebookTabBase, ControlsFrameBase
from pyminutiaeviewer.minutia import Minutia
from pyminutiaeviewer.minutiae_drawing import draw_minutiae
from pyminutiaeviewer.minutiae_reader import MinutiaeReader, MinutiaeFileFormat


class DrawFromFile(NotebookTabBase):
    def __init__(self, parent):
        NotebookTabBase.__init__(self, parent)

        self.minutiae_file_format = StringVar()

        controls = ControlsFrame(self, self.load_fingerprint_image, self.minutiae_file_format,
                                 self.load_minutiae_file, self.draw_minutiae)

        self.set_controls(controls)

    def resize(self, event):
        if self.image_minutiae is not None:
            self.draw_minutiae()
            return
        super(self.__class__, self).resize(event)

    def load_minutiae_file(self):
        file_path = askopenfilename(filetypes=(("Text files", ('*.txt', '*.min')),
                                               ("All files", "*.*")))
        if file_path:
            if self.minutiae_file_format.get() == "Simple":
                reader = MinutiaeReader(MinutiaeFileFormat.SIMPLE)
            elif self.minutiae_file_format.get() == "NBIST":
                reader = MinutiaeReader(MinutiaeFileFormat.NBIST)
            else:
                print("The File Type was not set", file=sys.stderr)
                return

            try:
                self.minutiae = reader.read(file_path)
            except Exception as e:
                traceback.print_exc()
                showerror("Read Minutiae File", "There was an error in reading the minutiae file. Are you sure you "
                                                "selected the right format?\n\nThe error message was:\n{}".format(e))

    def draw_minutiae(self):
        if self.minutiae is None:
            showerror("Draw Minutiae", "The minutiae file has not been set.")
            return
        if self.image_raw is None:
            showerror("Draw Minutiae", "The image file has not been set.")
            return

        scaled_raw_image, ratio = scale_image_to_fit_minutiae_canvas(self.image_canvas, self.image_raw)
        minutiae = [Minutia(int(m.x * ratio), int(m.y * ratio), m.angle, m.minutia_type) for m in self.minutiae]
        self.image_minutiae = draw_minutiae(scaled_raw_image, minutiae)

        self.image = ImageTk.PhotoImage(self.image_minutiae)
        self.image_canvas.delete("IMG")
        self.image_canvas.create_image(0, 0, image=self.image, anchor=N + W, tags="IMG")
        self.update_idletasks()


class ControlsFrame(ControlsFrameBase):
    def __init__(self, parent, load_fingerprint_func, minutiae_format, load_minutiae_func, draw_minutiae_func):
        ControlsFrameBase.__init__(self, parent, load_fingerprint_func)

        self.radio_label = Label(self, text="Minutiae File Format:")
        self.radio_label.grid(row=1, column=0, sticky=N)
        self.radio_simple = Radiobutton(self, text="Simple", variable=minutiae_format, value="Simple")
        self.radio_simple.grid(row=2, column=0, sticky=W)
        self.radio_nbist = Radiobutton(self, text="NBIST/MINDTC", variable=minutiae_format, value="NBIST")
        self.radio_nbist.grid(row=3, column=0, sticky=W)
        minutiae_format.set("NBIST")

        self.open_minutiae_txt_btn = Button(self, text="Open Minutiae File", command=load_minutiae_func)
        self.open_minutiae_txt_btn.grid(row=4, column=0, sticky=N + W + E)

        self.draw_minutiae_btn = Button(self, text="Draw Minutiae", command=draw_minutiae_func)
        self.draw_minutiae_btn.grid(row=5, column=0, sticky=N + W + E)
