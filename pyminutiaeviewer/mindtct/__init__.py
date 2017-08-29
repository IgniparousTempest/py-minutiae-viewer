import os
import platform
import tempfile
from pathlib import Path

import shutil
from typing import List

from PIL.Image import Image

from pyminutiaeviewer.minutia import Minutia
from pyminutiaeviewer.minutiae_reader import MinutiaeReader, MinutiaeFileFormat


def mindtct(image: Image) -> List[Minutia]:
    platform_name = platform.system()
    if platform_name == 'Windows':
        mindtct_path = Path(__file__).resolve().parent / 'mindtct.exe'
    elif platform_name == 'Linux':
        mindtct_path = Path(__file__).resolve().parent / 'mindtct'
    else:
        raise EnvironmentError(platform_name + " is a platform that is currently unsupported")

    # Create folder:
    folder = tempfile.mkdtemp(prefix='pyminview_')
    folder = Path(folder).resolve()

    # Save image
    image_path = folder / 'image.png'
    image.convert('L').save(str(image_path))

    # Execute mindtct
    output_path = folder / 'out'
    command = ' '.join([str(mindtct_path), '-m1', str(image_path), str(output_path)])
    os.system(command)

    reader = MinutiaeReader(MinutiaeFileFormat.NBIST)
    minutiae = reader.read(str(output_path) + '.min')

    # Clean up
    shutil.rmtree(str(folder))

    return minutiae
