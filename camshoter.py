import argparse
import contextlib
import datetime
import glob
import logging
import os
import sys
import time

import PIL.Image
import PyV4L2Camera.camera
import PyV4L2Camera.exceptions

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

    current_day = datetime.datetime.now()
    current_timestamp = int(time.time())
    current_day_str = current_day.strftime("%Y-%m-%d")
    current_image_directory = os.path.join(image_directory, current_day_str, str(current_timestamp))

    os.makedirs(current_image_directory, exist_ok=True)

    video_devices = glob.glob('/dev/video*')
    device_number = 1
    for video_device in video_devices:
        try:
            with contextlib.closing(PyV4L2Camera.camera.Camera(video_device)) as camera:
                frame = camera.get_frame()
        except PyV4L2Camera.exceptions.CameraError:
            continue

        image = PIL.Image.frombytes('RGB', (camera.width, camera.height), frame)
        image.save(f'{os.path.join(current_image_directory, str(device_number))}.jpg', format='JPEG')
        device_number += 1


if '__main__' == __name__:
    main()
