from utils import car_mapping
from conf.const import MAX_DIRECTION_LEFT, MAX_DIRECTION_RIGHT, MAX_SPEED, STOP_SPEED


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
    assert direction == STOP_SPEED


def test_car_mapping_linear_trigger_max():
    speed = car_mapping._linear_speed_trigger_mapping(1)
    assert speed == MAX_SPEED


def test_car_mapping_linear_trigger_middle():
    speed = car_mapping._linear_speed_trigger_mapping(0.5)
    assert speed == round((MAX_SPEED + STOP_SPEED) / 2)


def test_car_mapping_get_normalized_speed_middle():
    speed = (MAX_SPEED + STOP_SPEED) / 2
    assert 0.5 == car_mapping.get_normalized_speed(speed)


def test_car_mapping_get_normalized_speed_min():
    speed = STOP_SPEED
    assert 0 == car_mapping.get_normalized_speed(speed)


def test_car_mapping_get_normalized_speed_max():
    speed = MAX_SPEED
    assert 1 == car_mapping.get_normalized_speed(speed)


def test_car_mapping_get_normalized_dir_center():
    direction = (MAX_DIRECTION_RIGHT + MAX_DIRECTION_LEFT) / 2
    assert 0 == car_mapping.get_normalized_direction(direction)


def test_car_mapping_get_normalized_dir_right():
    direction = MAX_DIRECTION_RIGHT
    assert 1 == car_mapping.get_normalized_direction(direction)


def test_car_mapping_get_normalized_dir_left():
    direction = MAX_DIRECTION_LEFT
    assert -1 == car_mapping.get_normalized_direction(direction)
