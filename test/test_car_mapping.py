import pytest
import random

from utils import car_mapping as cm
from conf.const import MAX_DIRECTION_LEFT, MAX_DIRECTION_RIGHT, MAX_SPEED, STOP_SPEED
from conf.const import LABEL_TO_RAW_SPEED_MAPPING, LABEL_TO_RAW_DIR_MAPPING


def test_car_mapping_linear_joystick_full_right():
    car_mapping = cm.CarMapping()
    direction = car_mapping.get_raw_dir_from_xbox_joystick(1)
    assert direction == MAX_DIRECTION_RIGHT


def test_car_mapping_linear_joystick_full_left():
    car_mapping = cm.CarMapping()
    direction = car_mapping.get_raw_dir_from_xbox_joystick(-1)
    assert direction == MAX_DIRECTION_LEFT


def test_car_mapping_linear_joystick_center():
    car_mapping = cm.CarMapping()
    direction = car_mapping.get_raw_dir_from_xbox_joystick(0)
    assert direction == round((MAX_DIRECTION_LEFT + MAX_DIRECTION_RIGHT) / 2)


def test_car_mapping_linear_trigger_min():
    car_mapping = cm.CarMapping()
    speed = car_mapping.get_raw_speed_from_xbox_trigger(0)
    assert speed == STOP_SPEED


def test_car_mapping_linear_trigger_max():
    car_mapping = cm.CarMapping()
    speed = car_mapping.get_raw_speed_from_xbox_trigger(1)
    assert speed == MAX_SPEED


def test_car_mapping_linear_trigger_middle():
    car_mapping = cm.CarMapping()
    speed = car_mapping.get_raw_speed_from_xbox_trigger(0.5)
    assert speed == round((MAX_SPEED + STOP_SPEED) / 2)


def test_car_mapping_get_normalized_speed_middle():
    car_mapping = cm.CarMapping()
    speed = (MAX_SPEED + STOP_SPEED) / 2
    assert 0.5 == car_mapping.get_normalized_speed(speed)


def test_car_mapping_get_normalized_speed_min():
    car_mapping = cm.CarMapping()
    speed = STOP_SPEED
    assert 0 == car_mapping.get_normalized_speed(speed)


def test_car_mapping_get_normalized_speed_max():
    car_mapping = cm.CarMapping()
    speed = MAX_SPEED
    assert 1 == car_mapping.get_normalized_speed(speed)


def test_car_mapping_get_normalized_dir_center():
    car_mapping = cm.CarMapping()
    direction = (MAX_DIRECTION_RIGHT + MAX_DIRECTION_LEFT) / 2
    assert 0 == car_mapping.get_normalized_direction(direction)


def test_car_mapping_get_normalized_dir_right():
    car_mapping = cm.CarMapping()
    direction = MAX_DIRECTION_RIGHT
    assert 1 == car_mapping.get_normalized_direction(direction)


def test_car_mapping_get_normalized_dir_left():
    car_mapping = cm.CarMapping()
    direction = MAX_DIRECTION_LEFT
    assert -1 == car_mapping.get_normalized_direction(direction)


def test_car_mapping_get_raw_speed_from_label_0():
    car_mapping = cm.CarMapping()
    raw_speed = LABEL_TO_RAW_SPEED_MAPPING[0]
    assert raw_speed == car_mapping.get_raw_speed_from_label(0)


def test_car_mapping_get_raw_speed_from_label_1():
    car_mapping = cm.CarMapping()
    raw_speed = LABEL_TO_RAW_SPEED_MAPPING[1]
    assert raw_speed == car_mapping.get_raw_speed_from_label(1)


def test_car_mapping_get_raw_direction_from_label_0():
    car_mapping = cm.CarMapping()
    raw_dir = LABEL_TO_RAW_DIR_MAPPING[0]
    assert raw_dir == car_mapping.get_raw_dir_from_label(0)


def test_car_mapping_get_raw_direction_from_label_1():
    car_mapping = cm.CarMapping()
    raw_dir = LABEL_TO_RAW_DIR_MAPPING[1]
    assert raw_dir == car_mapping.get_raw_dir_from_label(1)


def test_car_mapping_get_raw_direction_from_label_outofrange():
    car_mapping = cm.CarMapping()
    i = len(car_mapping.label_to_raw_dir_mapping) + 1
    with pytest.raises(IndexError):
        raw_dir = car_mapping.get_raw_dir_from_label(i)


def test_car_mapping_get_raw_speed_from_label_outofrange():
    car_mapping = cm.CarMapping()
    i = len(car_mapping.label_to_raw_speed_mapping) + 1
    with pytest.raises(IndexError):
        raw_speed = car_mapping.get_raw_speed_from_label(i)


def test_label_from_speed_valueerror():
    car_mapping = cm.CarMapping()
    val = 111
    while val in car_mapping.raw_speed_to_label_mapping:
        val = random.random() * 1000
    with pytest.raises(ValueError):
        raw_speed = car_mapping.get_label_from_raw_speed(val)


def test_label_from_dir_valueerror():
    car_mapping = cm.CarMapping()
    val = 111
    while val in car_mapping.raw_dir_to_label_mapping:
        val = random.random() * 1000
    with pytest.raises(ValueError):
        raw_dir = car_mapping.get_label_from_raw_dir(val)
