import json
from pathlib import Path
from datetime import datetime

from utils import car_mapping as cm
from conf.path import SESSION_TEMPLATE_NAME, HARDWARE_CONF_FILE
from conf.const import SPEED_FAST, SPEED_NORMAL, IMAGE_SIZE, FRAME_RATE, EXPOSURE_MODE, \
    DIRECTION_C, DIRECTION_L, DIRECTION_L_M, DIRECTION_R, DIRECTION_R_M, HEAD_DOWN, HEAD_UP, \
    MAX_SPEED, STOP_SPEED, MAX_DIRECTION_LEFT, MAX_DIRECTION_RIGHT


class Label:

    def __init__(self, picture_dir=None, camera_position="unknown", raise_error=True):
        self._template = {}
        self.picture_dir_key = "location"
        self.picture_dir = picture_dir
        self.init_label_template(camera_position, raise_error=raise_error)

    def __str__(self):
        return json.dumps(self._template, indent=4)

    def __getitem__(self, item):
        return self._template[item]

    def __setitem__(self, key, value):
        if key == self.picture_dir_key:
            self._picture_dir = value
        self._template[key] = value

    def set_picture_dir(self, directory):
        self._picture_dir = directory
        self._template[self.picture_dir_key] = self._picture_dir

    def get_picture_dir(self):
        return self._picture_dir

    def get_template(self):
        return self._template

    picture_dir = property(get_picture_dir, set_picture_dir)
    template = property(get_template)

    def init_label_template(self, camera_position="unknown", raise_error=True):
        self.init_car_setting_from_const(cam_position=camera_position)
        self.init_hardware_conf_from_file(raise_error=raise_error)
        self.init_session_template_from_file(directory=self.picture_dir, raise_error=raise_error)
        self._template["raw"] = True
        self._template["upload_date"] = None
        self.set_label()

    def init_car_setting_from_const(self, cam_resolution=IMAGE_SIZE, cam_framerate=FRAME_RATE,
                                    cam_exposure_mode=EXPOSURE_MODE, cam_position="unknown"):
        car_setting = {
            "camera": {
                "resolution": cam_resolution,
                "frame_rate": cam_framerate,
                "exposure_mode": cam_exposure_mode,
                "camera_position": cam_position
            },
            "constant": {
                "max_speed": MAX_SPEED,
                "stop_speed": STOP_SPEED,
                "max_direction_l": MAX_DIRECTION_LEFT,
                "max_direction_r": MAX_DIRECTION_RIGHT,
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
        self._template["car_setting"] = car_setting

    def init_session_template_from_file(self, directory, raise_error=True):
        """Init the session _template from the file named SESSION_TEMPLATE_NAME and located in 'directory'"""
        if directory is None:
            session_template = Label.get_default_session_template()
        else:
            session_template_file = Path(directory) / SESSION_TEMPLATE_NAME
            session_template = {}

            def get_template(file):
                with Path(file).open(mode='r', encoding='utf-8') as fp:
                    template = json.load(fp)
                return template

            if raise_error:
                session_template = get_template(session_template_file)
            else:
                try:
                    session_template = get_template(session_template_file)
                except IOError as err:
                    print(f'ERROR: Session _template file "{session_template_file}" could not be read because : {err}')
                except json.JSONDecodeError as err:
                    print(f'JSON DECODE ERROR: in session _template file "{session_template_file}" : {err}')
        for key, val in session_template.items():
            self._template[key] = val

    def init_hardware_conf_from_file(self, raise_error=True):
        """Initialize the hardware conf with the HARDWARE_CONF_FILE"""
        hardware_conf_file = HARDWARE_CONF_FILE
        hardware_conf = {}
        if raise_error:
            with Path(hardware_conf_file).open(mode='r', encoding='utf-8') as fp:
                hardware_conf = json.load(fp)
        else:
            try:
                with Path(hardware_conf_file).open(mode='r', encoding='utf-8') as fp:
                    hardware_conf = json.load(fp)
            except IOError as err:
                print(f'ERROR: File "{hardware_conf_file}" could not be read because : {err}')
            except json.JSONDecodeError as err:
                print(f'JSON DECODE ERROR: in file "{hardware_conf_file}" : {err}')
        self._template["hardware_conf"] = hardware_conf

    def set_label(self, img_id=None, file_name="", timestamp=None,
                  raw_direction=MAX_DIRECTION_LEFT, raw_speed=STOP_SPEED, label_direction=None, label_speed=None):
        label = {
            "img_id": img_id,
            "file_name": file_name,
            "file_type": file_name.split(".")[-1],
            "raw_value": {
                "raw_direction": raw_direction,
                "raw_speed": raw_speed,
                "normalized_speed": cm.get_normalized_speed(raw_speed),
                "normalized_direction": cm.get_normalized_direction(raw_direction),
            },
            "label": [
                {
                    "direction": label_direction,
                    "speed": label_speed,
                    "nb_of_direction": 5,
                    "nb_of_speed": 2,
                    "created_by": "auto",
                    "created_date": datetime.now().strftime("%Y%m%dT%H-%M-%S-%f")
                }
            ],
            "timestamp": timestamp
        }
        for key, val in label.items():
            self._template[key] = val

    def get_copy(self):
        return self._template.copy()

    @staticmethod
    def get_default_session_template():
        return {
            "event": "",
            "track": "",
            "track_picture": "",
            "track_type": "",
            "dataset": [
                {
                    "name": "",
                    "comment": "",
                    "query": None,
                }
            ],
            "comment": ""
        }
