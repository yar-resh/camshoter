import argparse
import time
import threading
import subprocess

# RPi.GPIO can be imported only on Raspberry Pi
import RPi.GPIO as GPIO

DEFAULT_DIR = 'images'
DEFAULT_GPIO_PIN_NUMBER = 10
DEFAULT_MIN_HANDLE_INTERVAL = 3  # in seconds
DEFAULT_BOUNCE_TIME = 300  # in milliseconds


def main():
    parser = argparse.ArgumentParser(
        description='This script polls web-cameras plugged into Raspberry Pi '
                    'and saves captured frames to directory (specified or default)')
    parser.add_argument('-d', '--directory', action='store', default=DEFAULT_DIR, dest='image_directory',
                        help='path to the directory where captured frames will be saved as images. '
                             'Can be either absolute or relative')
    parser.add_argument('-p', '--pin_number', action='store', default=DEFAULT_GPIO_PIN_NUMBER, dest='gpio_pin_number',
                        type=int, help='number of GPIO pin button connected to')
    parser.add_argument('-m', '--min_handle_interval', action='store', default=DEFAULT_MIN_HANDLE_INTERVAL,
                        dest='min_handle_interval', type=int,
                        help='next frame saving allowed not sooner than previous saving time plus this interval')
    args = parser.parse_args()

    prev_timestamp = 0

    def callback(channel):
        nonlocal prev_timestamp
        current_timestamp = int(time.time())
        if (current_timestamp - prev_timestamp) < args.min_handle_interval:
            return

        result = subprocess.run(['python3', 'camshoter.py', '-d', args.image_directory])
        prev_timestamp = current_timestamp

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(args.gpio_pin_number, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(args.gpio_pin_number, GPIO.RISING, callback=callback, bouncetime=DEFAULT_BOUNCE_TIME)

    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        GPIO.cleanup()
        print('closing application')



if '__main__' == __name__:
    main()
