import argparse
from collections import deque
import numpy as np
from queue import Queue
from threading import Thread
import time
from datetime import datetime
from pathlib import Path
import json

import Adafruit_PCA9685
# noinspection PyUnresolvedReferences
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model

from utils.pivideostream import PiVideoStream
from conf.const import HEAD_UP, HEAD_DOWN
from conf.path import DEFAULT_OUTPUT_DIRECTORY
from utils import car_mapping as cm
from get_data.src import init_picture_folder as init
from get_data.src import label_handler as lh
from get_data.src import utils_fct


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("model_path", type=str,
                        help="Provide the model path.\n")
    parser.add_argument("-o", "--output_dir", type=str, default=DEFAULT_OUTPUT_DIRECTORY,
                        help=f"Directory where to save pictures. Default is '{DEFAULT_OUTPUT_DIRECTORY}''")
    return parser.parse_args()


class RaceOn:
    def __init__(self, model_path):
        # Load configuration
        self.car_mapping = cm.CarMapping()
        self.dir_center_label = round(len(self.car_mapping.label_to_raw_dir_mapping) / 2)

        # Init label for debug mode
        self.meta_label = None
        self.l_label = {}

        # Racing_status
        self.racing = False
        self.pause = False

        # Load model
        self.model = load_model(model_path)

        # Init engines
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(50)

        # Create a *threaded *video stream, allow the camera sensor to warm_up
        self.video_stream = PiVideoStream().start()
        time.sleep(2)
        # self.video_stream.test()
        self.frame = self.video_stream.read()
        self.buffer = None

        # Debug and print
        self.start_time = 0
        self.elapsed_time = 0
        self.nb_pred = 0
        self.sampling = 0
        self.debug = 0

        print("RaceOn initialized")

    def _get_motor_direction(self, predicted_labels):
        return self.car_mapping.get_raw_dir_from_label(predicted_labels[1])

    def _get_motor_speed(self, predicted_labels):
        if predicted_labels[1] == self.dir_center_label and predicted_labels[0] > 0:
            return self.car_mapping.get_raw_speed_from_label(predicted_labels[0])
        return self.car_mapping.get_raw_speed_from_label(0)

    @staticmethod
    def _get_motor_head(predicted_labels):
        if predicted_labels[0] > 0:
            return HEAD_UP
        return HEAD_DOWN

    @tf.function
    def _graph_predict(self, image):
        return self.model(image)

    def _get_predictions(self, motor_speed):
        # Grab the self.frame from the threaded video stream
        self.frame = self.video_stream.read()
        image = tf.convert_to_tensor(np.array([self.frame]) / 255.0)  # [jj] Do we need to create a new array ? img = self.frame / 255. ?

        # Get model prediction
        predictions_raw = self._graph_predict(image)
        predicted_labels = [int(np.argmax(pred)) for pred in predictions_raw]

        motor_direction = self._get_motor_direction(predicted_labels)
        motor_head = self._get_motor_head(predicted_labels)
        motor_speed = self._get_motor_speed(predicted_labels)
        return predicted_labels, motor_direction, motor_head, motor_speed

    def _check_debug_mode(self, predicted_labels, motor_direction, motor_head, motor_speed):
        if self.debug > 0 and self.sampling > 1:
            self.sampling = 0
            t_stamp = datetime.now().strftime("%Y%m%dT%H-%M-%S-%f")
            picture_path = Path(self.meta_label.picture_dir) / f'{str(t_stamp)}#s{predicted_labels[0]}' \
                                                               f'_d{predicted_labels[1]}.jpg'
            self.meta_label.set_label(img_id=t_stamp,
                                      file_name=picture_path.name,
                                      timestamp=t_stamp,
                                      raw_direction=motor_direction,
                                      raw_speed=motor_speed,
                                      label_direction=predicted_labels[1],
                                      label_speed=predicted_labels[0])
            self.meta_label["car_setting"]["camera"]["camera_position"] = motor_head
            self.l_label[t_stamp] = self.meta_label.get_copy()
            sample = {
                "array": self.frame,
                "picture_file": picture_path.as_posix()
            }
            self.buffer.append(sample)
            if self.debug > 1:
                print("Predictions = {}, Direction = {}, Head = {}, Speed = {}".format(
                    predicted_labels, motor_direction, motor_head, motor_speed))

    def _run_engine(self, motor_direction, motor_speed, motor_head):
        self.pwm.set_pwm(0, 0, motor_direction)
        self.pwm.set_pwm(1, 0, motor_speed)
        self.pwm.set_pwm(2, 0, motor_head)

    def _treat_user_input(self, user_inp):
        if user_inp == 'q':
            self.elapsed_time += (time.time() - self.start_time)
            self.stop()
        elif user_inp == 'p':
            self.pwm.set_pwm(1, 0, 0)
            if self.pause is False:
                self.elapsed_time += (time.time() - self.start_time)
                self._print_info()
                self.elapsed_time, self.nb_pred = 0, 0
            else:
                print("Already paused.")
            self.pause = True
        elif user_inp == 'go':
            if self.pause is True:
                self.start_time = time.time()
            else:
                print("Already on the go.")
            self.pause = False

    def race(self, debug=0, buff_size=100, queue_input=None, picture_dir=None):
        self.buffer = deque(maxlen=buff_size)
        self.start_time = time.time()
        self.racing = True
        self.nb_pred = 0
        self.sampling = 0
        self.debug = debug
        motor_speed = self.car_mapping.get_raw_speed_from_label(0)
        if debug > 0:
            self.meta_label = lh.Label(picture_dir=picture_dir)

        while self.racing:
            if not self.pause:
                # Decide action and run motor
                predicted_labels, motor_direction, motor_head, motor_speed = self._get_predictions(motor_speed)
                self._run_engine(motor_direction, motor_speed, motor_head)
                self._check_debug_mode(predicted_labels, motor_direction, motor_speed, motor_head)
                self.nb_pred += 1
                self.sampling += 1
            if not queue_input.empty():
                self._treat_user_input(queue_input.get(block=False))

    def stop(self):
        self.racing = False
        self._print_info()
        time.sleep(2)  # TODO check without
        self.pwm.set_pwm(0, 0, 0)
        self.pwm.set_pwm(1, 0, 0)
        self.pwm.set_pwm(2, 0, 0)
        self.video_stream.stop()
        print("Stopped properly")

    def _print_info(self):
        # Performance status
        if self.elapsed_time > 0:
            pred_rate = self.nb_pred / float(self.elapsed_time)
            print(f'{self.nb_pred} prediction in {self.elapsed_time}s -> {pred_rate} pred/s')
        self._write_and_clear_buffer()

    def _write_and_clear_buffer(self):
        if self.buffer is not None and len(self.buffer) > 0:
            print(f'Saving buffer pictures to : "{self.meta_label.picture_dir}"')
            i = 0
            for i, img in enumerate(self.buffer):
                pic = Image.fromarray(img["array"], 'RGB')
                pic.save(img["picture_file"])
            print(f'{i + 1} pictures saved.')
            output_label = Path(self.meta_label.picture_dir) / "labels.json"
            if output_label.is_file():
                output_label = utils_fct.get_label_file_name(output_label)
            with output_label.open(mode='w', encoding='utf-8') as fp:
                json.dump(self.l_label, fp, indent=4)
            print(f'Labels saved to "{output_label}"')
            self.buffer.clear()


def get_input_queue(out_q):
    racing_prompt = """Press 'q' + enter to totally stop the race
    Press 'p' + enter to pause the race
    Press 'go' + enter to resume race\n"""
    while True:
        user_inp = input(racing_prompt)
        out_q.put(user_inp)
        if user_inp == 'q':
            break


def run_threads(thread1, thread2):
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()


if __name__ == '__main__':
    options = get_args()
    debug_mode_list = [1, 2]
    race_on = None
    try:
        race_on = RaceOn(options.model_path)
        q = Queue()

        starting_prompt = f"""Type 'go' to start.
        Type 'debug=$LEVEL_VAL' to start in debug mode of level LEVEL_VAL (LEVEL_VAL can be {debug_mode_list})
        Type 'q' to totally stop the race.\n"""

        while True:
            user_input = input(starting_prompt)
            if user_input == "go":
                print("Race is on.")
                input_thread = Thread(target=get_input_queue, args=(q,))
                race_thread = Thread(target=race_on.race, kwargs={'debug': 0, 'queue_input': q})
                run_threads(input_thread, race_thread)
                break
            elif user_input[:6] == "debug=":
                init.init_picture_folder(options.output_dir)
                debug_lvl = int(user_input.split("=")[1])
                if debug_lvl not in debug_mode_list:
                    print("'{}' is not a valid debug mode. Please choose between:{}".format(debug_lvl, debug_mode_list))
                else:
                    print("Race is on in Debug mode level {}".format(debug_lvl))
                    input_thread = Thread(target=get_input_queue, args=(q,))
                    race_thread = Thread(target=race_on.race, kwargs={'debug': debug_lvl, 'queue_input': q,
                                                                      'picture_dir': options.output_dir})
                    run_threads(input_thread, race_thread)
                    break
            elif user_input == "q":
                break
    except KeyboardInterrupt:
        pass
    finally:
        if race_on is not None and race_on.racing is True:
            race_on.stop()
        print("Race is over.")
