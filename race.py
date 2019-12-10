import argparse
import numpy as np
import time

import Adafruit_PCA9685
# noinspection PyUnresolvedReferences
from keras.models import load_model

from pivideostream import PiVideoStream
from utils.const import SPEED_NORMAL, SPEED_FAST, HEAD_UP, HEAD_DOWN, \
    DIRECTION_R, DIRECTION_L, DIRECTION_C


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("model_path", type=str,
                        help="Provide the model path.\n")
    return parser.parse_args()


class RaceOn:
    def __init__(self, model_path):
        # Load model
        self.model = load_model(model_path)

        # Init engines
        # TODO: A quoi sert direction speed? ajouterhead pour initialiser
        self.speed = SPEED_FAST
        self.direction = DIRECTION_C
        self.head = HEAD_DOWN
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(50)

        # Create a *threaded *video stream, allow the camera sensor to warm_up
        self.video_stream = PiVideoStream().start()
        time.sleep(2)
        self.video_stream.test()
        self.frame = self.video_stream.read()

    @staticmethod
    def choose_direction(predictions):
        # TODO: Make it more modular so  it can handle 3 or 5 direction--> dictionnary or list in utils.const?
        if predictions[1] == 0:
            return DIRECTION_L
        elif predictions[1] == 1:
            return DIRECTION_C
        elif predictions[1] == 2:
            return DIRECTION_R

    @staticmethod
    def choose_speed(predictions):
        if predictions[1] == 1 and predictions[0] == 1:
            return SPEED_FAST
        return SPEED_NORMAL

    @staticmethod
    def choose_head(predictions, speed):
        if speed == SPEED_FAST and predictions[1] == 1 and predictions[0] == 1:
            return HEAD_UP
        return HEAD_DOWN

    def race(self):
        while True:
            # Grab the self.frame from the threaded video stream
            self.frame = self.video_stream.read()
            image = np.array([self.frame]) / 255.0

            # Get model prediction
            predictions_raw = self.model.predict(image)
            predictions = [np.argmax(pred, axis=1) for pred in predictions_raw]  # Why ?

            # Decide action
            direction = self.choose_direction(predictions)
            speed = self.choose_speed(predictions)
            head = self.choose_head(predictions, speed)

            # Apply values to engines
            self.pwm.set_pwm(0, 0, direction)
            self.pwm.set_pwm(1, 0, speed)
            self.pwm.set_pwm(2, 0, head)

    # TODO reinitialize to init values
    def stop(self):
        self.pwm.set_pwm(0, 0, 0)
        self.pwm.set_pwm(1, 0, 0)
        self.pwm.set_pwm(2, 0, 0)
        self.video_stream.stop()
        print("Stop")


if __name__ == '__main__':
    options = get_args()
    race_on = RaceOn(options.model_path)
    print("Ready ! press CTRL+C to START/STOP :")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass

    try:
        race_on.race()
    except KeyboardInterrupt:
        pass
    race_on.stop()
