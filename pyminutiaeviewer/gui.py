import traceback
from tkinter.ttk import Frame, Button, Label, Radiobutton, Style, Notebook
from tkinter import W, E, N, S, NSEW, RAISED, StringVar, Canvas, BOTH
from tkinter.filedialog import askopenfilename, sys
from tkinter.messagebox import showerror
from typing import Tuple

from PIL import ImageTk, Image

from pyminutiaeviewer.minutia import Minutia
from pyminutiaeviewer.minutiae_drawing import draw_minutiae
from pyminutiaeviewer.minutiae_reader import MinutiaeReader, MinutiaeFileFormat


class Root(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        s = Style()
        s.theme_use("clam")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.grid(sticky=NSEW)

        self.minutiae_file_format = StringVar()
        self.minutiae = None

        self.control_panel = ControlPanel(self, self.load_fingerprint_image, self.load_minutiae_file,
                                          self.draw_minutiae, self.minutiae_file_format)
        self.control_panel.grid(row=0, column=0, sticky=NSEW)

        self.image_raw = Image.new('RGBA', (512, 512), (255, 255, 255, 255))
        self.image_minutiae = None
        self.image = ImageTk.PhotoImage(self.image_raw)
        # self.image_label = Label(self, image=self.image)
        # self.image_label.grid(row=0, column=1, sticky=N)

        self.image_canvas = Canvas(self, bd=0, highlightthickness=0)
        self.image_canvas.create_image(0, 0, image=self.image, anchor=N + W, tags="IMG")
        self.image_canvas.grid(row=0, column=1, sticky=NSEW)
        self.bind("<Configure>", self.resize)

    def resize(self, event):
        if self.image_minutiae is not None:
            self.draw_minutiae()
            return
        resized, _ = _scale_image_to_fit_minutiae_canvas(self.image_canvas, self.image_raw)
        self.image = ImageTk.PhotoImage(resized)
        self.image_canvas.delete("IMG")
        self.image_canvas.create_image(0, 0, image=self.image, anchor=N + W, tags="IMG")

    def load_fingerprint_image(self):
        file_path = askopenfilename(filetypes=(("Image files", ('*.bmp', '*.jpeg', '*.jpg', '*.png')),
                                               ("All files", "*.*")))
        if file_path:
            self.image_raw = Image.open(file_path).convert("RGBA")
            self.image = ImageTk.PhotoImage(self.image_raw)
            self.image_minutiae = None
            self.image_canvas.delete("IMG")
            self.image_canvas.create_image(0, 0, image=self.image, anchor=N + W, tags="IMG")
            self.resize(None)
            self.update_idletasks()

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

        scaled_raw_image, ratio = _scale_image_to_fit_minutiae_canvas(self.image_canvas, self.image_raw)
        minutiae = [Minutia(int(m.x * ratio), int(m.y * ratio), m.angle, m.minutia_type) for m in self.minutiae]
        self.image_minutiae = draw_minutiae(scaled_raw_image, minutiae)

        self.image = ImageTk.PhotoImage(self.image_minutiae)
        self.image_canvas.delete("IMG")
        self.image_canvas.create_image(0, 0, image=self.image, anchor=N + W, tags="IMG")
        self.update_idletasks()


class ControlPanel(Frame):
    def __init__(self, parent, load_fingerprint_func, load_minutiae_func, draw_minutiae_func, minutiae_format):
        Frame.__init__(self, parent, borderwidth=1)
        self.columnconfigure(0, weight=1)

        self.mode_label = Label(self, text="Display Pre-calculated Minutiae")
        self.mode_label.grid(row=0, column=0, sticky=N)

        self.mode_button = Button(self, text="Change Mode", command=None)
        self.mode_button.grid(row=1, column=0, sticky=N + W + E)

        self.controls_frame = PreCalculatedFrame(self, load_fingerprint_func, load_minutiae_func, draw_minutiae_func,
                                                 minutiae_format)
        self.controls_frame.grid(row=2, column=0, pady=(10, 0), sticky=N + W + E)


class PreCalculatedFrame(Frame):
    def __init__(self, parent, load_fingerprint_func, load_minutiae_func, draw_minutiae_func, minutiae_format):
        Frame.__init__(self, parent, relief=RAISED, borderwidth=1)
        self.columnconfigure(0, weight=1)

        self.open_fingerprint_image_button = Button(self, text="Open Fingerprint Image", command=load_fingerprint_func)
        self.open_fingerprint_image_button.grid(row=0, column=0, sticky=N + W + E)

        self.radio_label = Label(self, text="Minutiae File Format:")
        self.radio_label.grid(row=1, column=0, sticky=N)
        self.radio_simple = Radiobutton(self, text="Simple", variable=minutiae_format, value="Simple")
        self.radio_simple.grid(row=2, column=0, sticky=W)
        self.radio_nbist = Radiobutton(self, text="NBIST/MINDTC", variable=minutiae_format, value="NBIST")
        self.radio_nbist.grid(row=3, column=0, sticky=W)
        minutiae_format.set("NBIST")

        self.open_minutiae_txt_button = Button(self, text="Open Minutiae File", command=load_minutiae_func)
        self.open_minutiae_txt_button.grid(row=4, column=0, sticky=N + W + E)

        self.draw_minutiae = Button(self, text="Draw Minutiae", command=draw_minutiae_func)
        self.draw_minutiae.grid(row=5, column=0, sticky=N + W + E)


def _aspect_ratio_for_scaling(canvas_size: Tuple[int, int], image_size: Tuple[int, int]) -> float:
    """
    Returns the correct ratio to scale an image by to fill a canvas while maintaining its aspect ratio.
    :param canvas_size: The size of the canvas to fill.
    :param image_size: The size of the image.
    :return: The aspect ratio to scale the image by.
    """
    cw, ch = canvas_size
    iw, ih = image_size
    return min(cw / iw, ch / ih)


def _scale_image_to_fit_minutiae_canvas(canvas: Canvas, im: Image.Image) -> Tuple[Image.Image, float]:
    """
    Scales the provided image to fit the minutiae canvas.
    :param canvas: The canvas object to fit the image to.
    :param im: The image to scale
    :return: The scaled image
    """
    w, h = im.size
    canvas_size = (canvas.winfo_width(), canvas.winfo_height())
    ratio = _aspect_ratio_for_scaling(canvas_size, im.size)
    new_size = (int(w * ratio), int(h * ratio))
    return im.resize(new_size, Image.ANTIALIAS), ratio
