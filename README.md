# camshoter

This script is intended to poll web-cameras plugged into Raspberry Pi and save images to directory (specified or default).

```text
usage: camshoter.py [-h] [-d IMAGE_DIRECTORY] [-i] [-p GPIO_PIN_NUMBER]
                    [-m MIN_HANDLE_INTERVAL]

This script polls web-cameras plugged into Raspberry Pi and saves captured frames to
directory (specified or default)

optional arguments:
  -h, --help            show this help message and exit
  -d IMAGE_DIRECTORY, --directory IMAGE_DIRECTORY
                        path to the directory where captured frames will be saved as images.
                        Can be either absolute or relative
  -i, --instant         frames from cameras will be captured instantly,
                        without waiting for button press; script will exit
                        immediately after saving frames
  -p GPIO_PIN_NUMBER, --pin_number GPIO_PIN_NUMBER
                        number of GPIO pin button connected to
  -m MIN_HANDLE_INTERVAL, --min_handle_interval MIN_HANDLE_INTERVAL
                        next frame saving allowed not sooner than previous
                        saving time plus this interval
```

### Requirements
At least Python 3.5 is required

```shell script
sudo apt-get install libjpeg-dev zlib1g-dev
sudo apt-get install python3-rpi.gpio
sudo apt-get install libv4l-dev
sudo pip3 install -r requirements.txt
```