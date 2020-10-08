import argparse
import datetime
import logging
import os
import sys

import numpy
from PIL import Image

from PyV4L2Camera.camera import Camera
from PyV4L2Camera.controls import ControlIDs


DEFAULT_DIR = 'images'


def get_full_path(path):
    """Returns the full path to directory or file.

    If ``path`` is absolute - it returns as is. If ``path is relative`` - it joins to absolute path of running script.
    """
    if os.path.isabs(path):
        return path

    script_directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_directory, path)


def main():
    parser = argparse.ArgumentParser(
        description='This script polls web-cameras plugged into Raspberry Pi '
                    'and saves images to directory (specified or default)')
    parser.add_argument('-d', '--directory', action='store', default=DEFAULT_DIR, dest='image_directory',
                        help='path to the directory where images should be located. Can be either absolute or relative')
    args = parser.parse_args()

    logger = logging.getLogger("camshoter")

    image_directory = get_full_path(args.image_directory)
    if not os.path.exists(image_directory):
        try:
            os.makedirs(image_directory, exist_ok=True)
        except OSError as err:
            logger.error(f"error creating directory {image_directory}: {str(err)}")
            sys.exit(1)
    else:
        if not os.access(image_directory, os.W_OK):
            logger.error(f"no permissions to write into {image_directory}")
            sys.exit(1)

    current_time = datetime.datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

    os.makedirs(os.path.join(image_directory, current_time_str))

    camera = Camera('/dev/video0')

    frame = camera.get_frame()
    im = Image.frombytes('RGB', (camera.width, camera.height), frame, 'raw',
                         'RGB')
    arr = numpy.asarray(im)
    im = Image.fromarray(numpy.uint8(arr))
    im.show()
    camera.close()


if '__main__' == __name__:
    main()

