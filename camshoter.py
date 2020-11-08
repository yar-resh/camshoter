import argparse
import contextlib
import datetime
import glob
import os
import sys

import PIL.Image
import PyV4L2Camera.camera
import PyV4L2Camera.exceptions

DEFAULT_DIR = 'images'

IMAGE_FORMAT = 'jpeg'
BLACKLIST_NAME_PARTS = ['bcm2835']


def get_full_path(path):
    """Returns the full path to directory or file.

    If ``path`` is absolute - it returns as is.
    If ``path`` is relative - it joins to absolute path of directory of running script.
    """
    if os.path.isabs(path):
        return path

    script_directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_directory, path)


def get_device_name(device_number):
    """Return the name of video device pointed by its number"""
    with open('/sys/class/video4linux/video{0}/name'.format(device_number), 'r') as video_device_file:
        return video_device_file.readline()


def is_blacklisted(device_name):
    """Returns true if device name contains blacklisted name parts, false otherwise"""
    for name in BLACKLIST_NAME_PARTS:
        if name in device_name:
            return True
    return False


def save_frames(image_directory):
    """Saves frames, captured from available video devices, to specified directory.

    Directory with name of current date will be created additionally inside ``image_directory`` (if not exists yet).
    Frames will be saved inside directory with name of current UNIX timestamp located in directory mentioned above.
    """
    current_day = datetime.datetime.now()
    current_timestamp = current_day.strftime("%H:%M:%S")
    current_day_str = current_day.strftime("%Y-%m-%d")
    current_image_directory = os.path.join(image_directory, current_day_str, current_timestamp)

    os.makedirs(current_image_directory, exist_ok=True)

    video_devices = glob.glob('/dev/video*')
    device_number = 1
    for video_device in video_devices:
        device_name = get_device_name(video_device.replace('/dev/video', ''))
        if is_blacklisted(device_name):
            continue

        try:
            with contextlib.closing(PyV4L2Camera.camera.Camera(video_device)) as camera:
                frame = camera.get_frame()
        except PyV4L2Camera.exceptions.CameraError:
            print('device {0} is unavailable'.format(video_device))
            continue

        image = PIL.Image.frombytes('RGB', (camera.width, camera.height), frame)
        image.save('{0}.{1}'.format(os.path.join(current_image_directory, str(device_number)), IMAGE_FORMAT),
                   format=IMAGE_FORMAT)
        device_number += 1


def main():
    parser = argparse.ArgumentParser(
        description='This script polls web-cameras plugged into Raspberry Pi '
                    'and saves captured frames to directory (specified or default)')
    parser.add_argument('-d', '--directory', action='store', default=DEFAULT_DIR, dest='image_directory',
                        help='path to the directory where captured frames will be saved as images. '
                             'Can be either absolute or relative')
    args = parser.parse_args()

    image_directory = get_full_path(args.image_directory)
    if not os.path.exists(image_directory):
        try:
            os.makedirs(image_directory, exist_ok=True)
        except OSError as err:
            print('error creating directory {0}: {1}'.format(image_directory, str(err)))
            sys.exit(1)
    else:
        if not os.access(image_directory, os.W_OK):
            print('no permissions to write into {0}'.format(image_directory))
            sys.exit(1)

    video_devices = glob.glob('/dev/video*')
    if not video_devices:
        print('there is no video devices in system')
        sys.exit(0)

    save_frames(image_directory)


if '__main__' == __name__:
    main()
