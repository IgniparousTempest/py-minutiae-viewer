from tkinter import Canvas, NSEW, N, W, RAISED, E, Menu
from tkinter.messagebox import showinfo
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Frame, Button, Label, Widget
from types import FunctionType
from typing import Tuple, List

from PIL import Image

from pyminutiaeviewer.minutia import Minutia


class NotebookTabBase(Frame):
    def __init__(self, parent, load_fingerprint_func):
        Frame.__init__(self, parent, relief=RAISED, borderwidth=1)
        self.open_fingerprint_image_button = Button(self, text="Open Fingerprint Image", command=load_fingerprint_func)
        self.open_fingerprint_image_button.grid(row=0, column=0, sticky=N + W + E)

    def load_fingerprint_image(self, image: Image):
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

    def fingerprint_drawing(self, image: Image) -> Image:
        """
        The function the root calls to draw on to.
        :param image: The image to draw on to.
        :return: The edited image.
        """
        return image

    def minutiae_filtering(self, minutiae: List[Minutia]) -> List[Minutia]:
        """
        The function the root calls to allow modules to refine the minutiae to be shown.
        :param minutiae: The image to draw on to.
        """
        return minutiae


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


class MenuBar(Menu):
    def __init__(self, parent):
        super(self.__class__, self).__init__(parent)

        file_menu = Menu(self, tearoff=0)
        file_menu.add_command(label="Open Fingerprint Image...", command=parent.load_fingerprint_image)
        file_menu.add_command(label="Open Minutiae File...", command=parent.load_minutiae_file)
        file_menu.add_command(label="Export Minutiae File...", command=parent.save_minutiae_file)
        file_menu.add_separator()
        file_menu.add_command(label="About", command=about_info_box)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=parent.exit_application)
        self.add_cascade(label="File", menu=file_menu)


def about_info_box():
    """
    Constructs an about dialogue box.
    :return: The about dialogue box.
    """
    return showinfo("About", "Written by Courtney Pitcher")


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


def validate_float(value_if_allowed: str, character: str) -> bool:
    """
    Ensures that a string is a float.
    :param value_if_allowed: The value that is being tested.
    :param character: The character being inserted or removed.
    :return: True if valid, otherwise False.
    """
    if character in '0123456789.-+':
        try:
            float(value_if_allowed)
            return True
        except ValueError:
            return False
    else:
        return False


def validate_int(value_if_allowed: str, character: str) -> bool:
    """
    Ensures that a string is an int.
    :param value_if_allowed: The value that is being tested.
    :param character: The character being inserted or removed.
    :return: True if valid, otherwise False.
    """
    if character in '0123456789-+':
        try:
            int(value_if_allowed)
            return True
        except ValueError:
            return False
    else:
        return False


def validate_float_between_0_and_1(value_if_allowed: str, character: str) -> bool:
    """
    Ensures that a string is a float and is in the interval [0.0 and 1.0].
    :param value_if_allowed: The value that is being tested.
    :param character: The character being inserted or removed.
    :return: True if valid, otherwise False.
    """
    if validate_float(value_if_allowed, character):
        v = float(value_if_allowed)
        if v < 0 or v > 1:
            return False
        return True
    return False


def validate_int_between_0_and_100(value_if_allowed: str, character: str) -> bool:
    """
    Ensures that a string is an int and is in the interval [0, 100].
    :param value_if_allowed: The value that is being tested.
    :param character: The character being inserted or removed.
    :return: True if valid, otherwise False.
    """
    if validate_int(value_if_allowed, character):
        v = int(value_if_allowed)
        if v < 0 or v > 100:
            return False
        return True
    return False


def validate_int_between_neg_100_and_100(value_if_allowed: str, character: str) -> bool:
    """
    Ensures that a string is an int and is in the interval [-100, 100].
    :param value_if_allowed: The value that is being tested.
    :param character: The character being inserted or removed.
    :return: True if valid, otherwise False.
    """
    if validate_int(value_if_allowed, character):
        v = int(value_if_allowed)
        if v < -100 or v > 100:
            return False
        return True
    return False


def validation_command(parent: Widget, command: FunctionType) -> dict:
    """
    Creates the validate and validatecommand parameters of an Entry widget for the provided validation command.
    Use keyword argument unpacking to set values of the __init__ method directly.
    :param parent: The parent of the Entry Widget.
    :param command: The command to call to validate the Entry widget.
    :return: The __init__ parameters at a dictionary.
    """
    return {'validate': 'key', 'validatecommand': (parent.register(command), '%P', '%S')}
