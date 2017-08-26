from tkinter import Canvas, NSEW, N, W, RAISED, E
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Frame, Button, Label
from typing import Tuple

from PIL import Image


class NotebookTabBase(Frame):
    def __init__(self, parent, load_fingerprint_func):
        Frame.__init__(self, parent, relief=RAISED, borderwidth=1)
        self.open_fingerprint_image_button = Button(self, text="Open Fingerprint Image", command=load_fingerprint_func)
        self.open_fingerprint_image_button.grid(row=0, column=0, sticky=N + W + E)

    def load_fingerprint_image(self):
        """
        Called if the root successfully loads a new fingerprint image.
        """
        pass

    def load_minutiae_file(self):
        """
        Called if the root successfully loads a new minutiae file.
        """
        pass

    def on_canvas_mouse_left_click(self, event):
        """
        Called when the left mouse button is pressed while on the canvas.
        """
        pass

    def on_canvas_ctrl_mouse_left_click(self, event):
        """
        Called when the the control key and left mouse button are pressed while on the canvas.
        """
        pass

    def on_canvas_mouse_left_drag(self, event):
        """
        Called when the left mouse button is held down and moved while on the canvas.
        """
        pass

    def on_canvas_mouse_left_release(self, event):
        """
        Called when the left mouse button is released.
        """
        pass

    def on_canvas_mouse_right_click(self, event):
        """
        Called when the right mouse button is pressed while on the canvas.
        """
        pass


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
