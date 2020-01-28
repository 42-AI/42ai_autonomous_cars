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

from get_data.src import xbox
from get_data.src import label_handler
from conf.const import SPEED_NORMAL, IMAGE_SIZE, FRAME_RATE, EXPOSURE_MODE, DIRECTION_C, HEAD_DOWN
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
        self.head = HEAD_DOWN

        # Set head down
        self.pwm.set_pwm(2, 0, self.head)

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
        self.meta_label = label_handler.Label(picture_dir=output_dir, camera_position=self.head)

    def save_and_clear_buffer(self):
        print(f'Saving picture to "{self.meta_label.picture_dir}" ...', end=" ", flush=True)
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
            self.controls()
            if self.label[0] != -1 and time.time() - start > self.delay:
                im = Image.fromarray(image, 'RGB')
                t_stamp = datetime.now().strftime("%Y%m%dT%H-%M-%S-%f")
                picture_path = Path(self.meta_label.picture_dir) / f'{str(t_stamp)}#s{self.label[0]}_d{self.label[1]}.jpg'
                self.meta_label.set_label(img_id=t_stamp,
                                          file_name=picture_path.name,
                                          timestamp=t_stamp,
                                          raw_direction=self.direction,
                                          raw_speed=self.speed,
                                          label_direction=self.label[1],
                                          label_speed=self.label[0])
                self.meta_label.add_normalized_speed_dir()
                l_label.append(self.meta_label.get_copy())
                self.buffer.append((picture_path, im))
                if show_mode:
                    print(f'{i}: speed:x={self.trigger}|l={self.label[0]}|n={self.meta_label["label"]["normalized_speed"]}'
                          f' ; dir:x={self.x_cursor}|l={self.label[1]}|n={self.meta_label["label"]["normalized_direction"]}'
                          f' ; pic_path:"{picture_path}"')
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
                output_label = Path(self.meta_label.picture_dir) / "labels.json"
                with output_label.open(mode='w', encoding='utf-8') as fp:
                    json.dump(l_label, fp, indent=4)
                return

    def controls(self):
        # Get speed label
        self.trigger = round(self.joy.rightTrigger(), 2)  # Right trigger position (values 0 to 1.0)
        self.speed = car_mapping.get_speed_from_xbox_trigger(self.trigger)
        self.label[0] = car_mapping.get_label_from_speed(self.speed)
        # Get direction labels
        self.x_cursor = round(self.joy.leftX(), 2)  # X-axis of the left stick (values -1.0 to 1.0)
        self.direction = car_mapping.get_direction_from_xbox_joystick(self.x_cursor)
        self.label[1] = car_mapping.get_label_from_direction(self.direction)
        # Set motor direction and speed
        self.pwm.set_pwm(0, 0, self.direction)
        self.pwm.set_pwm(1, 0, self.speed)