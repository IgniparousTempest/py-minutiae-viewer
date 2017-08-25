import traceback
from pathlib import Path
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Frame, Button, Label
from tkinter import Canvas, NSEW, N, W, RAISED, E
from typing import Tuple

from PIL import Image, ImageTk

from pyminutiaeviewer.minutia import Minutia
from pyminutiaeviewer.minutiae_drawing import draw_minutiae
from pyminutiaeviewer.minutiae_reader import MinutiaeReader, MinutiaeFileFormat


class NotebookTabBase(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.grid(sticky=NSEW)

        self.minutiae = []
        self.image_minutiae = None

        self.file_path = Path()

        self.image_raw = Image.new('RGBA', (512, 512), (255, 255, 255, 255))
        self.image = ImageTk.PhotoImage(self.image_raw)

        self.controls_frame = None

        self.image_canvas = Canvas(self, bd=0, highlightthickness=0)
        self.image_canvas.create_image(0, 0, image=self.image, anchor=N + W, tags="IMG")
        self.image_canvas.grid(row=0, column=1, sticky=NSEW)
        self.bind("<Configure>", self.resize)

    def set_controls(self, controls_frame):
        self.controls_frame = controls_frame
        self.controls_frame.grid(row=0, column=0, sticky=NSEW)

    def resize(self, event):
        if self.image_minutiae is not None:
            self.draw_minutiae()
            return

        resized, _ = scale_image_to_fit_minutiae_canvas(self.image_canvas, self.image_raw)
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
            self.file_path = Path(file_path).resolve()
            self.master.set_title(self.file_path.name)
            self.minutiae = []
            self.update_idletasks()

    def load_minutiae_file(self):
        file_path = askopenfilename(initialfile=self.file_path.stem,
                                    filetypes=(("All minutiae files", ('*.min', '*.sim')),
                                               ("Simple minutiae file", '*.sim'),
                                               ("NBIST minutiae file", '*.min'),
                                               ("All files", "*.*")))
        if file_path:
            # Select the correct file format
            if Path(file_path).suffix == '.sim':
                reader = MinutiaeReader(MinutiaeFileFormat.SIMPLE)
            elif Path(file_path).suffix == '.min':
                reader = MinutiaeReader(MinutiaeFileFormat.NBIST)
            else:
                showerror("Read Minutiae File", "The chosen file had an extension of '{}', which can't be interpreted."
                          .format(Path(file_path).suffix))
                return

            try:
                self.minutiae = reader.read(file_path)
                self.draw_minutiae()
            except Exception as e:
                traceback.print_exc()
                showerror("Read Minutiae File", "There was an error in reading the minutiae file.\n\n"
                                                "The error message was:\n{}".format(e))

    def draw_minutiae(self):
        scaled_raw_image, ratio = scale_image_to_fit_minutiae_canvas(self.image_canvas, self.image_raw)
        minutiae = [Minutia(int(m.x * ratio), int(m.y * ratio), m.angle, m.minutia_type) for m in self.minutiae]
        self.image_minutiae = draw_minutiae(scaled_raw_image, minutiae)

        self.image = ImageTk.PhotoImage(self.image_minutiae)
        self.image_canvas.delete("IMG")
        self.image_canvas.create_image(0, 0, image=self.image, anchor=N + W, tags="IMG")
        self.update_idletasks()


class ControlsFrameBase(Frame):
    def __init__(self, parent, load_fingerprint_func):
        Frame.__init__(self, parent, relief=RAISED, borderwidth=1)
        self.open_fingerprint_image_button = Button(self, text="Open Fingerprint Image", command=load_fingerprint_func)
        self.open_fingerprint_image_button.grid(row=0, column=0, sticky=N + W + E)


class MinutiaeFrameBase(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.open_fingerprint_image_button = Frame(self, relief=RAISED, borderwidth=1)
        self.open_fingerprint_image_button.grid(row=0, column=0, sticky=NSEW)

        self.open_fingerprint_image_button.columnconfigure(0, weight=1)

        self.minutiae_file_label = Label(self.open_fingerprint_image_button, text="test")
        self.minutiae_file_label.grid(row=0, column=0)

        self.minutiae_file_label = ScrolledText(self)
        self.minutiae_file_label.grid(row=1, column=0, sticky=NSEW)


def aspect_ratio_for_scaling(canvas_size: Tuple[int, int], image_size: Tuple[int, int]) -> float:
    """
    Returns the correct ratio to scale an image by to fill a canvas while maintaining its aspect ratio.
    :param canvas_size: The size of the canvas to fill.
    :param image_size: The size of the image.
    :return: The aspect ratio to scale the image by.
    """
    cw, ch = canvas_size
    iw, ih = image_size
    return min(cw / iw, ch / ih)


def scale_image_to_fit_minutiae_canvas(canvas: Canvas, im: Image.Image) -> Tuple[Image.Image, float]:
    """
    Scales the provided image to fit the minutiae canvas.
    :param canvas: The canvas object to fit the image to.
    :param im: The image to scale
    :return: The scaled image
    """
    w, h = im.size
    canvas_size = (canvas.winfo_width(), canvas.winfo_height())
    ratio = aspect_ratio_for_scaling(canvas_size, im.size)
    new_size = (int(w * ratio), int(h * ratio))
    return im.resize(new_size, Image.ANTIALIAS), ratio
