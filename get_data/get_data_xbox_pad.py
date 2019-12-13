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
    DIRECTION_C, DIRECTION_L, DIRECTION_L_M, DIRECTION_R, DIRECTION_R_M
from utils.path import DATA_IMAGES_DIRECTORY


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

    def video_loop(self, show_mode=False):
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
                    picture_path = "{}/{}_{}_{}.jpg".format(DATA_IMAGES_DIRECTORY,
                                                            str(self.label[0]), str(self.label[1]), str(t_stamp))
                    im.save(picture_path)
                    if show_mode:
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
            self.controls(show_mode)

    def controls(self, show_mode):
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

        if show_mode:
            print("""Trigger = {} and speed set to {}
            X_cursor = {} and direction set to {}""".format(
                trigger, self.speed, x_cursor, self.direction))

        # Set motor direction and speed
        self.pwm.set_pwm(0, 0, self.direction)
        self.pwm.set_pwm(1, 0, self.speed)


if __name__ == "__main__":
    options = get_args()
    controller = None

    print("Are you ready to drive?")
    starting_prompt = """Press 'go' + enter to start.
    Press 'show' + enter to start with the printing mode.
    Press 'q' + enter to totally stop the race.
    """
    racing_prompt = """Press 'q' + enter to totally stop the race\n"""
    keep_going = True
    started = False

    try:
        while keep_going:
            try:  # This is for python2
                # noinspection PyUnresolvedReferences
                user_input = raw_input(racing_prompt) if started else raw_input(starting_prompt)
            except NameError:
                user_input = input(racing_prompt) if started else input(starting_prompt)
            if user_input == "go" and not started:
                print("Race is on.")
                controller = Controller(options.delay)
                controller.video_loop(show_mode=False)
                started = True
            elif user_input == "show" and not started:
                print("Race is on. test mode")
                controller = Controller(options.delay)
                controller.video_loop(show_mode=True)
                started = True
            elif user_input == "q":
                keep_going = False
    except KeyboardInterrupt:
        pass
    finally:
        if controller:
            controller.joy.close()
            controller.camera.close()
        print("Race is over.")
