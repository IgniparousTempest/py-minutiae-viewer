import copy
from enum import Enum


class MinutiaType(Enum):
    BIFURCATION = "bifurcation"
    RIDGE_ENDING = "ridge ending"


class Minutia(object):
    def __init__(self, x: int, y: int, angle: float, minutia_type: MinutiaType, quality: float):
        """
        A DTO to encapsulate a fingerprint minutia.
        :param x: The x co-ordinate.
        :param y: The y co-ordinate.
        :param angle: The angle of the minutia.
        :param minutia_type: The type of the minutia, either a ridge ending or a bifurcation.
        :param quality: The quality of the feature.
        """
        self.x = x
        self.y = y
        self.angle = angle
        self.minutia_type = minutia_type
        self.quality = quality

    def copy(self) -> 'Minutia':
        return copy.deepcopy(self)

    def __str__(self):
        return "Minutia(x: {}, y: {}, angle: {}, minutia_type: {}, confidence: {})".format(
            self.x,
            self.y,
            self.angle,
            self.minutia_type.name,
            self.quality
        )
