import argparse
import numpy as np
import time
from PIL import Image
from collections import deque

import Adafruit_PCA9685
# noinspection PyUnresolvedReferences
from tensorflow.keras.models import load_model

from utils.pivideostream import PiVideoStream
from utils.const import SPEED_NORMAL, SPEED_FAST, HEAD_UP, HEAD_DOWN, \
    DIRECTION_R, DIRECTION_L, DIRECTION_C, DIRECTION_L_M, DIRECTION_R_M
from utils.path import OUTPUT_DIRECTORY


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("model_path", type=str,
                        help="Provide the model path.\n")
    return parser.parse_args()


class RaceOn:
    def __init__(self, model_path):
        # Racing_status
        self.racing = False

        # Load model
        self.model = load_model(model_path)

        # Init engines
        # TODO (pclement): A quoi sert direction speed? ajouterhead pour initialiser
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
        self.buffer = None
        self.nb_pred = 0
        self.start_time = 0
        print("RaceOn initialized")

    @staticmethod
    def choose_direction(predictions):
        # TODO (pclement): Make it more modular so it can handle 3 or 5 direction--> dictionnary or list in utils.const?
        if predictions[1] == 0:
            return DIRECTION_L_M
        elif predictions[1] == 1:
            return DIRECTION_L
        elif predictions[1] == 2:
            return DIRECTION_C
        elif predictions[1] == 3:
            return DIRECTION_R
        elif predictions[1] == 4:
            return DIRECTION_R_M

    @staticmethod
    def choose_speed(predictions):
        if predictions[1] == 1 and predictions[0] == 1:
            return SPEED_FAST
        return SPEED_NORMAL

    def choose_head(self, predictions, speed):
        if speed == self.choose_speed(predictions) == SPEED_FAST:
            return HEAD_UP
        return HEAD_DOWN

    def race(self, debug=0, buff_size=100):
        self.buffer = deque(maxlen=buff_size)
        self.start_time = time.time()
        self.racing = True
        self.nb_pred = 0
        sampling = 0
        speed = SPEED_NORMAL
        while self.racing:
            # Grab the self.frame from the threaded video stream
            self.frame = self.video_stream.read()
            image = np.array([self.frame]) / 255.0  # [jj] Do we need to create a new array ? img = self.frame / 255. ?

            # Get model prediction
            predictions_raw = self.model.predict(image)
            predictions = [np.argmax(pred, axis=1) for pred in predictions_raw]  # Why ?

            # Decide action
            direction = self.choose_direction(predictions)
            head = self.choose_head(predictions, speed)
            speed = self.choose_speed(predictions)

            # Debug mode
            if debug > 0 and sampling > 3:
                sampling = -1
                sample = {
                    "array": self.frame,
                    "direction": predictions[1][0],
                    "speed": 1 if speed == SPEED_FAST else 0
                }
                self.buffer.append(sample)
                if debug > 1:
                    print("Predictions = {}, Direction = {}, Head = {}, Speed = {}".format(
                        predictions, direction, head, speed))

            # Apply values to engines
            self.pwm.set_pwm(0, 0, direction)
            self.pwm.set_pwm(1, 0, speed)
            self.pwm.set_pwm(2, 0, head)
            self.nb_pred += 1
            sampling += 1

    # TODO (pclement) reinitialize to init values
    def stop(self):
        self.racing = False
        self.pwm.set_pwm(0, 0, 0)
        self.pwm.set_pwm(1, 0, 0)
        self.pwm.set_pwm(2, 0, 0)
        self.video_stream.stop()

        # Performance status
        elapse_time = time.time() - self.start_time
        pred_rate = self.nb_pred / float(elapse_time)
        print('{} prediction in {}s -> {} pred/s'.format(self.nb_pred, elapse_time, pred_rate))

        # Write buffer
        if self.buffer is not None and len(self.buffer) > 0:
            print('Saving buffer pictures to : "{}"'.format(OUTPUT_DIRECTORY))
            for i, img in enumerate(self.buffer):
                pic_file = '{}_image{}_{}_{}.jpg'.format(self.start_time, i, img["speed"], img["direction"])
                pic = Image.fromarray(img["array"], 'RGB')
                pic.save("{}{}".format(OUTPUT_DIRECTORY, pic_file))
            print('{} pictures saved.'.format(i + 1))
        print("Stop")


if __name__ == '__main__':
    options = get_args()
    debug_mode_list = [1, 2]
    race_on = None
    try:
        race_on = RaceOn(options.model_path)
        print("Are you ready ?")

        # TODO (pclement): other inputs to stop the motor & direct the wheels without having to reload the full model.

        starting_prompt = """Type 'go' to start.
        Type 'debug=$LEVEL_VAL' to start in debug mode of level LEVEL_VAL (LEVEL_VAL can be {})
        Type 'q' to totally stop the race.
        """.format(debug_mode_list)
        racing_prompt = """Press 'q' + enter to totally stop the race\n"""
        keep_going = True
        started = False
        while keep_going:
            try:  # This is for python2
                # noinspection PyUnresolvedReferences
                user_input = raw_input(racing_prompt) if started else raw_input(starting_prompt)
            except NameError:
                user_input = input(racing_prompt) if started else input(starting_prompt)
            if user_input == "go" and not started:
                print("Race is on.")
                race_on.race(debug=0)
                started = True
            elif user_input[:6] == "debug=" and not started:
                debug_lvl = int(user_input.split("=")[1])
                if debug_lvl not in debug_mode_list:
                    print("'{}' is not a valid debug mode. Please choose between:{}".format(debug_lvl, debug_mode_list))
                print("Race is on in Debug mode level {}".format(debug_lvl))
                race_on.race(debug=debug_lvl)
                started = True
            elif user_input == "q":
                keep_going = False
    except KeyboardInterrupt:
        pass
    finally:
        if race_on is not None:
            race_on.stop()
        print("Race is over.")
