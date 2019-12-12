import argparse
import time

import Adafruit_PCA9685
# noinspection PyUnresolvedReferences
from picamera import PiCamera
# noinspection PyUnresolvedReferences
from picamera.array import PiRGBArray
# noinspection PyUnresolvedReferences
from PIL import Image

from get_data import xbox
from utils.const import SPEED_FAST, SPEED_NORMAL, IMAGE_SIZE, \
    DIRECTION_C, DIRECTION_L, DIRECTION_L_M, DIRECTION_R, DIRECTION_R_M, RASPBERRY_ROOT_FOLDER


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("delay", type=float,
                        help="Provide the delay between 2 capture of images.\n")
    return parser.parse_args()


class Controller:
    def __init__(self, delay, pwm_freq=50, camera_framerate=60):
        self.delay = float(delay)
        self.label = [-1, 2]

        # set controls
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(pwm_freq)

        # Init speed direction
        self.speed = SPEED_NORMAL
        self.direction = DIRECTION_C
        # why not head ?

        # Setup Camera
        self.camera = PiCamera()
        self.camera.resolution = IMAGE_SIZE
        self.camera.framerate = camera_framerate
        self.rawCapture = PiRGBArray(self.camera, size=IMAGE_SIZE)
        time.sleep(0.5)

        # Setup xbox pad
        self.joy = xbox.Joystick()

    def video_loop(self):
        # Loop over camera frames
        start = time.time()
        i = 0
        for frame in self.camera.capture_continuous(self.rawCapture, format="rgb", use_video_port=True):
            # convert img as Array
            image = frame.array
            # take a pic
            if self.label[0] != -1:
                if time.time() - start > self.delay:
                    im = Image.fromarray(image, 'RGB')
                    t_stamp = time.time()
                    picture_path = "{}/images/{}_{}_{}.jpg".format(RASPBERRY_ROOT_FOLDER,
                        str(self.label[0]), str(self.label[1]), str(t_stamp))
                    im.save(picture_path)
                    print("{} - snap : {}".format(i, picture_path))
                    i += 1
                    start = time.time()
            # Clean image before the next comes
            self.rawCapture.truncate(0)

            if self.joy.A():  # Test state of the A button (1=pressed, 0=not pressed)
                self.pwm.set_pwm(0, 0, 0)
                self.pwm.set_pwm(1, 0, 0)
                print("Stop")
                return
            self.controls()

    def controls(self):
        # Get speed label
        trigger = self.joy.rightTrigger()  # Right trigger position (values 0 to 1.0)
        self.label[0] = round(trigger, 2)
        if 1 >= trigger >= 0.8:
            self.speed = SPEED_FAST
        elif trigger > 0:
            self.speed = SPEED_NORMAL
        else:
            self.speed = 0
            self.label[0] = -1

        # Get direction labels
        x_cursor = self.joy.leftX()  # X-axis of the left stick (values -1.0 to 1.0)
        if -1 <= x_cursor < -0.8:
            self.direction = DIRECTION_L_M
        elif x_cursor < -0.1:
            self.direction = DIRECTION_L
        elif x_cursor < 0.1:
            self.direction = DIRECTION_C
        elif x_cursor < 0.8:
            self.direction = DIRECTION_R
        elif x_cursor <= 1:
            self.direction = DIRECTION_R_M
        self.label[1] = round(x_cursor, 2)

        # Set motor direction and speed
        self.pwm.set_pwm(0, 0, self.direction)
        self.pwm.set_pwm(1, 0, self.speed)


if __name__ == "__main__":
    options = get_args()
    print("Press Ctrl+C to start/stop...")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass
    controller = Controller(options.delay)
    controller.video_loop()
    controller.joy.close()
    controller.camera.close()
