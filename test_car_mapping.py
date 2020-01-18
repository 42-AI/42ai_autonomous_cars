from utils import car_mapping
from utils.const import MAX_DIRECTION_LEFT, MAX_DIRECTION_RIGHT, MAX_SPEED


def test_car_mapping_linear_joystick_full_right():
    direction = car_mapping._linear_direction_joystick_mapping(1)
    assert direction == MAX_DIRECTION_RIGHT


def test_car_mapping_linear_joystick_full_left():
    direction = car_mapping._linear_direction_joystick_mapping(-1)
    assert direction == MAX_DIRECTION_LEFT


def test_car_mapping_linear_joystick_center():
    direction = car_mapping._linear_direction_joystick_mapping(0)
    assert direction == round((MAX_DIRECTION_LEFT + MAX_DIRECTION_RIGHT) / 2)


def test_car_mapping_linear_trigger_min():
    direction = car_mapping._linear_speed_trigger_mapping(0)
    assert direction == 0


def test_car_mapping_linear_trigger_max():
    speed = car_mapping._linear_speed_trigger_mapping(1)
    assert speed == MAX_SPEED


def test_car_mapping_linear_trigger_middle():
    speed = car_mapping._linear_speed_trigger_mapping(0.5)
    assert speed == round((MAX_SPEED + STOP_SPEED) / 2)
