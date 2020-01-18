import json
from pathlib import Path

from utils.path import SESSION_TEMPLATE_NAME, LABEL_TEMPLATE_FILE, HARDWARE_CONF_FILE
from utils.const import SPEED_FAST, SPEED_NORMAL, IMAGE_SIZE, FRAME_RATE, EXPOSURE_MODE, \
    DIRECTION_C, DIRECTION_L, DIRECTION_L_M, DIRECTION_R, DIRECTION_R_M, HEAD_DOWN, HEAD_UP, \
    MAX_SPEED, STOP_SPEED, MAX_DIRECTION_LEFT, MAX_DIRECTION_RIGHT


class Label:

    def __init__(self, picture_dir=None):
        self.template = self.get_label_template()
        self.picture_dir = picture_dir
        self.session_template = {} if self.picture_dir is None else self.get_session_template_from_file(self.picture_dir)
        self.car_setting = self.get_car_setting_from_const()
        self.hardware_conf = self.get_hardware_conf_from_file()

    def set_picture_dir(self, directory):
        self._picture_dir = directory
        self.template["location"] = self._picture_dir

    def get_picture_dir(self):
        return self._picture_dir

    def set_car_setting(self, d_car_setting):
        self._car_setting = d_car_setting
        self.template["car_setting"] = self._car_setting

    def get_car_setting(self):
        return self._car_setting

    def set_hardware_conf(self, d_hardware_conf):
        self._hardware_conf = d_hardware_conf
        self.template["hardware"] = self._hardware_conf

    def get_hardware_conf(self):
        return self._hardware_conf

    def set_session_template(self, d_session_template):
        self._session_template = d_session_template
        for key, value in self._session_template.items():
            self.template[key] = value

    def get_session_template(self):
        return self._session_template

    session_template = property(get_session_template, set_session_template)
    hardware_conf = property(get_hardware_conf, set_hardware_conf)
    car_setting = property(get_car_setting, set_car_setting)
    picture_dir = property(get_picture_dir, set_picture_dir)

    @staticmethod
    def create_label(img_id=None, file_name=None, timestamp=None,
                     raw_dir=None, raw_speed=None, label_dir=None, label_speed=None):
        label = {
            "img_id": img_id,
            "file_name": file_name,
            "file_type": file_name.split(".")[-1] if file_name is not None else None,
            "label": {
                "raw_direction": raw_dir,
                "raw_speed": raw_speed,
                "label_direction": label_dir,
                "label_speed": label_speed
            },
            "timestamp": timestamp
        }
        return label

    @staticmethod
    def get_car_setting_from_const(cam_resolution=IMAGE_SIZE, cam_framerate=FRAME_RATE,
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
        return car_setting

    @staticmethod
    def get_session_template_from_file(directory, raise_error=True):
        """Set the session template from the file located in 'directory' and named as per SESSION_TEMPLATE_NAME"""
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
                print(f'ERROR: File "{session_template_file}" could not be read because : {err}')
            except json.JSONDecodeError as err:
                print(f'JSON DECODE ERROR: in file "{session_template_file}" : {err}')
        return session_template

    @staticmethod
    def get_label_template(raise_error=True):
        """Initialize the label template from the LABEL_TEMPLATE_FILE"""
        label_template_json = LABEL_TEMPLATE_FILE
        label_template = {}

        def get_template(file):
            with Path(file).open(mode='r', encoding='utf-8') as fp:
                template = json.load(fp)
            template["raw"] = True
            return template

        if raise_error:
            label_template = get_template(label_template_json)
        else:
            try:
                label_template = get_template(label_template_json)
            except IOError as err:
                print(f'ERROR: File "{label_template_json}" could not be read because : {err}')
            except json.JSONDecodeError as err:
                print(f'JSON DECODE ERROR: in file "{label_template_json}" : {err}')
        return label_template

    @staticmethod
    def get_hardware_conf_from_file(raise_error=True):
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
        return hardware_conf
