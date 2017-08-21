from tkinter import Canvas
from typing import Tuple

from PIL import Image


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
