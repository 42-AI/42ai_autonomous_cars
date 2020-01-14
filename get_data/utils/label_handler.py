import json
from pathlib import Path

from utils.path import SESSION_TEMPLATE_NAME, LABEL_TEMPLATE_FILE, HARDWARE_CONF_FILE


class Label:

    def __init__(self, car_setting=None, output_dir=None):
        self.template = self.get_label_template()
        self.output_dir = output_dir
        self.session_template = {} if self.output_dir is None else self.get_session_template_from_file(self.output_dir)
        self.car_setting = {} if car_setting is None else car_setting
        self.hardware_conf = self.get_hardware_conf()

    def set_output_dir(self, directory):
        self._output_dir = directory
        self.template["location"] = self._output_dir

    def get_output_dir(self):
        return self._output_dir

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
    output_dir = property(get_output_dir, set_output_dir)

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
    def get_hardware_conf(raise_error=True):
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
