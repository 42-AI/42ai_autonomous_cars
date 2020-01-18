import time
from datetime import datetime
from PIL import Image
from pathlib import Path
import json

# noinspection PyUnresolvedReferences
import Adafruit_PCA9685
# noinspection PyUnresolvedReferences
from picamera import PiCamera
# noinspection PyUnresolvedReferences
from picamera.array import PiRGBArray
# noinspection PyUnresolvedReferences

from get_data.utils import xbox
from get_data.utils import label_handler
from utils.const import SPEED_FAST, SPEED_NORMAL, IMAGE_SIZE, FRAME_RATE, EXPOSURE_MODE,\
    DIRECTION_C, DIRECTION_L, DIRECTION_L_M, DIRECTION_R, DIRECTION_R_M, HEAD_DOWN, HEAD_UP
from utils import car_mapping


class TrainingSession:
    def __init__(self, delay, output_dir, pwm_freq=50):
        self.delay = float(delay)
        self.label = [-1, 2]
        self.buffer = []

        # set controls
        self.x_cursor = 0
        self.trigger = 0
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(pwm_freq)

        # Init speed direction
        self.speed = SPEED_NORMAL
        self.direction = DIRECTION_C

        # Set head down
        self.pwm.set_pwm(2, 0, HEAD_DOWN)

        # Setup Camera
        self.camera = PiCamera()
        self.camera.resolution = IMAGE_SIZE
        self.camera.framerate = FRAME_RATE
        self.camera.exposure_mode = EXPOSURE_MODE
        self.rawCapture = PiRGBArray(self.camera, size=IMAGE_SIZE)
        time.sleep(2)

        # Setup xbox pad
        self.joy = xbox.Joystick()

        # Init Label
        self.meta_label = label_handler.Label(car_setting=self.get_car_setting(), output_dir=output_dir)

    def get_car_setting(self):
        car_setting = {
            "camera": {
                "resolution": self.camera.resolution,
                "frame_rate": str(self.camera.framerate),
                "exposure_mode": self.camera.exposure_mode
            },
            "constant": {
                "speed_normal": SPEED_NORMAL,
                "speed_fast": SPEED_FAST,
                "direction_l_m": DIRECTION_L_M,
                "direction_l": DIRECTION_L,
                "direction_c": DIRECTION_C,
                "direction_r": DIRECTION_R,
                "direction_r_m": DIRECTION_R_M,
                "head_up": HEAD_UP,
                "head_down": HEAD_DOWN
            }
        }
        return car_setting

    def create_label(self, img_id, file_name, timestamp):
        label = {
            "img_id": img_id,
            "file_name": file_name,
            "label": {
                "raw_direction": self.direction,
                "raw_speed": self.speed,
                "direction": self.label[1],
                "speed": self.label[0],
                "trigger": self.trigger,
                "x_cursor": self.x_cursor
            },
            "timestamp": timestamp
        }
        return label

    def save_and_clear_buffer(self):
        print(f'Saving picture to "{self.meta_label.output_dir}" ...', end=" ", flush=True)
        self.pwm.set_pwm(0, 0, 0)
        self.pwm.set_pwm(1, 0, 0)
        for picture_path, im in self.buffer:
            im.save(picture_path.as_posix())
        print(f'Done ! {len(self.buffer)} pictures saved !')
        self.buffer.clear()

    def run(self, show_mode=False, max_buff_size=100):
        # Loop over camera frames
        start = time.time()
        i = 0
        l_label = []
        for frame in self.camera.capture_continuous(self.rawCapture, format="rgb", use_video_port=True):
            # convert img as Array
            image = frame.array
            # control car
            self.controls(show_mode)
            if self.label[0] != -1 and time.time() - start > self.delay:
                im = Image.fromarray(image, 'RGB')
                t_stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                picture_path = Path(self.meta_label.output_dir) / f'{self.label[0]}_{self.label[1]}_{str(t_stamp)}.jpg'
                label = self.create_label(img_id=t_stamp, file_name=picture_path.name, timestamp=t_stamp)
                label = dict(self.meta_label.template, **label)  # shallow copy meta_label and add label key/val
                l_label.append(label)
                self.buffer.append((picture_path, im))
                if show_mode:
                    print(f'{i}: trigger:{self.trigger} ; joystick:{self.x_cursor} ; pic_path:"{picture_path}""')
                i += 1
                start = time.time()
                if len(self.buffer) > max_buff_size:
                    self.save_and_clear_buffer()
            # Clean image before the next comes
            self.rawCapture.truncate(0)
            if self.joy.A():  # Test state of the A button (1=pressed, 0=not pressed)
                self.pwm.set_pwm(0, 0, 0)
                self.pwm.set_pwm(1, 0, 0)
                self.save_and_clear_buffer()
                print("Stop")
                output_label = Path(self.meta_label.output_dir) / "labels.json"
                with output_label.open(mode='w', encoding='utf-8') as fp:
                    json.dump(l_label, fp)
                return

    def controls(self, show_mode):
        # Get speed label
        self.trigger = round(self.joy.rightTrigger(), 2)  # Right trigger position (values 0 to 1.0)
        self.speed = car_mapping.get_speed_from_xbox_trigger(self.trigger)
        self.label[0] = car_mapping.get_label_from_speed(self.speed)
        # Get direction labels
        self.x_cursor = round(self.joy.leftX(), 2)  # X-axis of the left stick (values -1.0 to 1.0)
        self.direction = car_mapping.get_direction_from_xbox_joystick(self.x_cursor)
        self.label[1] = car_mapping.get_label_from_direction(self.direction)
        if show_mode:
            print("""Trigger = {} and speed set to {}
            X_cursor = {} and direction set to {}""".format(
                self.trigger, self.speed, self.x_cursor, self.direction))
        # Set motor direction and speed
        self.pwm.set_pwm(0, 0, self.direction)
        self.pwm.set_pwm(1, 0, self.speed)
