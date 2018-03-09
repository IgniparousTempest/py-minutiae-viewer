from typing import List

from PIL import Image

from pyminutiaeviewer.errors import CorruptFileError
from pyminutiaeviewer.minutia import Minutia, MinutiaType
from pyminutiaeviewer.minutiae_reader import MinutiaeFileFormat


class MinutiaeEncoder(object):
    def __init__(self, file_format: MinutiaeFileFormat):
        self._file_format = file_format
        if file_format == MinutiaeFileFormat.NBIST:
            self._encoder = _encode_nbist_format
        elif file_format == MinutiaeFileFormat.MINDTCT:
            self._encoder = _encode_nbist_format
        elif file_format == MinutiaeFileFormat.SIMPLE:
            self._encoder = _encode_simple_format
        elif file_format == MinutiaeFileFormat.XYT:
            self._encoder = _encode_xyt_format
        else:
            raise AttributeError("MinutiaeReader is not configured to read file format: {}".format(file_format))

    def write(self, absolute_file_path: str, minutiae: List[Minutia], image: Image.Image):
        """
        Writes minutiae to a text file.
        :param absolute_file_path: The absolute file path for the minutiae to be written to.
        :param minutiae: The minutiae to write to file.
        :param image: The image the minutiae are from, provides metadata to encoding.
        """
        encoded_minutiae = self._encoder(minutiae, image)

        with open(absolute_file_path, 'w') as f:
            f.write(encoded_minutiae)


def _encode_nbist_format(minutiae: List[Minutia], image: Image.Image) -> str:
    """
    Encodes to the NBIST's MINDTCT minutiae file.
    See: http://ws680.nist.gov/publication/get_pdf.cfm?pub_id=51097#page=159
    :param minutiae: The minutiae to encode.
    :param image: The image the minutiae are from, provides metadata to encoding.
    :return: The string encoding.
    """
    string = ""

    string += "Image (w,h) {} {}\n".format(image.width, image.height)
    string += '\n'
    string += "{} Minutiae Detected\n".format(len(minutiae))
    string += '\n'

    for i in range(len(minutiae)):
        m = minutiae[i]

        if m.minutia_type == MinutiaType.BIFURCATION:
            minutia_type = "BIF"
        elif m.minutia_type == MinutiaType.RIDGE_ENDING:
            minutia_type = "RIG"
        else:
            raise CorruptFileError("Minutiae of unknown type '{}'".format(m))

        string += " {} :  {},  {} : {} :  {} :{} : This file is incomplete\n"\
            .format(i, m.x, m.y, round(m.angle / 11.25), m.quality, minutia_type)

    return string


def _encode_simple_format(minutiae: List[Minutia], image: Image) -> str:
    """
    Encodes to a simplified minutiae file.
    :param minutiae: The minutiae to encode.
    :param image: The image the minutiae are from, provides metadata to encoding. This is unused.
    :return: The string encoding.
    """
    string = ""

    for m in minutiae:
        if m.minutia_type == MinutiaType.BIFURCATION:
            minutia_type = "BIF"
        elif m.minutia_type == MinutiaType.RIDGE_ENDING:
            minutia_type = "END"
        else:
            raise CorruptFileError("Minutiae of unknown type '{}'".format(m))

        # TODO: If this project is upgraded to python 3.6+, use Formatted string literals.
        # TODO: See: https://www.python.org/dev/peps/pep-0498/
        string += "{} {} {} {} {}\n".format(m.x, m.y, m.angle, minutia_type, m.quality)

    return string[:-1]


def _encode_xyt_format(minutiae: List[Minutia], image: Image) -> str:
    """
    Encodes to a xyt minutiae file.
    :param minutiae: The minutiae to encode.
    :param image: The image the minutiae are from, provides metadata to encoding. This is unused.
    :return: The string encoding.
    """
    string = ""

    for m in minutiae:
        string += "{} {} {} {}\n".format(m.x, m.y, int(m.angle % 180), int(m.quality * 100))

    return string[:-1]
