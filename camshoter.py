import argparse
import contextlib
import datetime
import glob
import logging
import os
import sys
import threading
import time

import PIL.Image
import PyV4L2Camera.camera
import PyV4L2Camera.exceptions

DEFAULT_DIR = 'images'
DEFAULT_GPIO_PIN_NUMBER = 3
IMAGE_FORMAT = 'jpeg'

LOG = logging.getLogger("camshoter")


def get_full_path(path):
    """Returns the full path to directory or file.

    If ``path`` is absolute - it returns as is. If ``path is relative`` - it joins to absolute path of running script.
    """
    if os.path.isabs(path):
        return path

    script_directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_directory, path)


def save_frames(image_directory):
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
            LOG.warning('device {0} is unavailable'.format(video_device))
            continue

        image = PIL.Image.frombytes('RGB', (camera.width, camera.height), frame)
        image.save('{0}.{1}'.format(os.path.join(current_image_directory, str(device_number)), IMAGE_FORMAT),
                   format=IMAGE_FORMAT)
        device_number += 1


def main():
    parser = argparse.ArgumentParser(
        description='This script polls web-cameras plugged into Raspberry Pi '
                    'and saves images to directory (specified or default)')
    parser.add_argument('-d', '--directory', action='store', default=DEFAULT_DIR, dest='image_directory',
                        help='path to the directory where images should be located. Can be either absolute or relative')
    parser.add_argument('-i', '--instant', action='store_true', dest='instant',
                        help='frames from cameras will be captured instantly, without waiting for button press; '
                             'script will exit immediately after saving frames')
    parser.add_argument('-p', '--pin_number', action='store', default=DEFAULT_GPIO_PIN_NUMBER, dest='gpio_pin_number',
                        type=int, help='number of GPIO pin button connected to')
    args = parser.parse_args()

    image_directory = get_full_path(args.image_directory)
    if not os.path.exists(image_directory):
        try:
            os.makedirs(image_directory, exist_ok=True)
        except OSError as err:
            LOG.error('error creating directory {0}: {1}'.format(image_directory, str(err)))
            sys.exit(1)
    else:
        if not os.access(image_directory, os.W_OK):
            LOG.error('no permissions to write into {0}'.format(image_directory))
            sys.exit(1)

    video_devices = glob.glob('/dev/video*')
    if not video_devices:
        LOG.warning('there is no video devices in system')
        sys.exit(0)

    if args.instant:
        save_frames(image_directory)
    else:
        # RPi.GPIO can be imported only on Raspberry Pi
        import RPi.GPIO as GPIO

        def callback(channel):
            save_frames(image_directory)

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(args.gpio_pin_number, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(args.gpio_pin_number, GPIO.RISING, callback=callback)

        threading.Event().wait()


if '__main__' == __name__:
    main()
