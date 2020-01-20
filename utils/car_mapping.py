from utils.const import SPEED_NORMAL, SPEED_FAST, DIRECTION_L_M, DIRECTION_C, DIRECTION_L, DIRECTION_R, DIRECTION_R_M
from utils.const import MAX_DIRECTION_LEFT, MAX_DIRECTION_RIGHT, MAX_SPEED, STOP_SPEED


def _two_label_speed_mapping(speed):
    if speed == SPEED_FAST:
        return 1
    elif speed == SPEED_NORMAL:
        return 0
    else:
        return -1


def _two_speed_trigger_mapping(trigger):
    """Return raw speed from trigger position with: 0 < trigger < 1 """
    if 1 >= trigger >= 0.8:
        return SPEED_FAST
    elif trigger > 0:
        return SPEED_NORMAL
    else:
        return 0


def _five_label_direction_mapping(direction):
    if direction == DIRECTION_L_M:
        return 0
    elif direction == DIRECTION_L:
        return 1
    elif direction == DIRECTION_C:
        return 2
    elif direction == DIRECTION_R:
        return 3
    elif direction == DIRECTION_R_M:
        return 4


def _five_direction_joystick_mapping(joystick):
    """Return raw direction from joystick position with: -1 < joystick < 1 """
    if -1 <= joystick < -0.8:
        return DIRECTION_L_M
    elif joystick < -0.1:
        return DIRECTION_L
    elif joystick < 0.1:
        return DIRECTION_C
    elif joystick < 0.8:
        return DIRECTION_R
    elif joystick <= 1:
        return DIRECTION_R_M


def _linear_direction_joystick_mapping(joystick):
    """
    Linear mapping raw_direction = joystick_pos * a + b where a and b coef are calculated at the 1st function call
    :param joystick:    [float]     -1 (full left) < joystick position < 1 (full right)
    :return:            [int]       raw direction value
    """
    if "a" not in _linear_direction_joystick_mapping.__dict__:
        _linear_direction_joystick_mapping.b = (MAX_DIRECTION_LEFT + MAX_DIRECTION_RIGHT) / 2
        _linear_direction_joystick_mapping.a = MAX_DIRECTION_RIGHT - _linear_direction_joystick_mapping.b
    return round(_linear_direction_joystick_mapping.a * joystick + _linear_direction_joystick_mapping.b)


def _linear_speed_trigger_mapping(speed):
    """
    Linear mapping raw_speed = trigger_pos * a + b where a and b coef are calculated at the 1st function call
    :param speed:      [float]     3xx (max speed) < trigger position < 321 (stop)
    :return:           [int]       raw speed value
    """
    if "a" not in _linear_speed_trigger_mapping.__dict__:
        _linear_speed_trigger_mapping.b = STOP_SPEED
        _linear_speed_trigger_mapping.a = MAX_SPEED - _linear_speed_trigger_mapping.b
    return round(_linear_speed_trigger_mapping.a * speed + _linear_speed_trigger_mapping.b)


def get_normalized_direction(direction):
    """
    -1 = MAX_DIRECTION_LEFT * a + b
    1 = MAX_DIRECTION_RIGHT * a + b
    --> 2 = (MAX_DIRECTION_RIGHT - MAX_DIRECTION_LEFT) * a
    --> b = 1 - MAX_RIGHT * a
    """
    if "a" not in get_normalized_direction.__dict__:
        get_normalized_direction.a = 2 / (MAX_DIRECTION_RIGHT - MAX_DIRECTION_LEFT)
        get_normalized_direction.b = 1 - MAX_DIRECTION_RIGHT * get_normalized_direction.a
    return round(get_normalized_direction.a * direction + get_normalized_direction.b, 2)


def get_normalized_speed(speed):
    """
    0 = STOP_SPEED * a + b
    1 = MAX_SPEED * a + b
    --> 1 = (MAX_SPEED - STOP_SPEED) * a
    --> b = -STOP_SPEED * a
    """
    if "a" not in get_normalized_speed.__dict__:
        get_normalized_speed.a = 1 / (MAX_SPEED - STOP_SPEED)
        get_normalized_speed.b = -STOP_SPEED * get_normalized_speed.a
    return round(get_normalized_speed.a * speed + get_normalized_speed.b, 2)


def get_speed_from_xbox_trigger(trigger):
    return _linear_speed_trigger_mapping(trigger)


def get_direction_from_xbox_joystick(joystick):
    return _linear_direction_joystick_mapping(joystick)


def get_label_from_speed(speed):
    return _two_label_speed_mapping(speed)


def get_label_from_direction(direction):
    return _five_label_direction_mapping(direction)
