from typing import List

import math
from PIL import ImageDraw, Image

from pyminutiaeviewer.minutia import Minutia, MinutiaType


def draw_minutiae(image: Image.Image, minutiae: List[Minutia], size: int = None):
    """
    Draws minutiae of to a copy of the image. Bifurcations are drawn as green squares, and ridge ends are drawn as red 
    circles. A line indicates the angle of the minutiae.
    :param image: An image to drawn the minutiae on to, typically a fingerprint.
    :param minutiae: A list of minutiae to be drawn.
    :param size: the size of the minutiae visualizations in pixels. If unset an auto scaling value is set.
    :return: The annotated image.
    """
    new_image = image.copy()
    draw = ImageDraw.Draw(new_image)

    if size is None:
        size = min(image.size[0], image.size[1]) / 512.0 * 10.0
    half = size / 2.0

    for m in minutiae:
        bounding_box = (m.x - half, m.y - half, m.x + half, m.y + half)
        if m.minutia_type == MinutiaType.BIFURCATION:
            colour = (255, 0, 0, 255)
            draw.ellipse(bounding_box, outline=colour)
        elif m.minutia_type == MinutiaType.RIDGE_ENDING:
            colour = (0, 255, 0, 255)
            draw.rectangle(bounding_box, outline=colour)
        else:
            raise AttributeError("Unknown minutiae type: {}".format(m))

        angle = (m.angle - 90) % 360

        x2 = m.x + math.cos(math.radians(angle)) * size * 1.5
        y2 = m.y + math.sin(math.radians(angle)) * size * 1.5
        draw.line((m.x, m.y, x2, y2), fill=colour)

    return new_image
