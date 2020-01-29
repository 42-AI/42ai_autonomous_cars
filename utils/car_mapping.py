from conf.const import SPEED_NORMAL, SPEED_FAST, DIRECTION_L_M, DIRECTION_C, DIRECTION_L, DIRECTION_R, DIRECTION_R_M
from conf.const import MAX_DIRECTION_LEFT, MAX_DIRECTION_RIGHT, MAX_SPEED, STOP_SPEED
from conf.const import RAW_DIR_TO_LABEL_MAPPING, JOYSTICK_TO_RAW_DIR_MAPPING, LABEL_TO_RAW_DIR_MAPPING
from conf.const import TRIGGER_TO_RAW_SPEED_MAPPING, RAW_SPEED_TO_LABEL_MAPPING, LABEL_TO_RAW_SPEED_MAPPING


class CarMapping:

    @staticmethod
    def get_linear_coef(p1, p2):
        """
        Compute the slope and intercept of the linear function passing through point p1 and point p2.
        y1 = a * x1 + b
        y2 = a * x2 + b
        -> (y1 - y2) = a (x1 - x2) -> a = (y1 - y2) / (x1 - x2)
        -> b = y1 - a * x1
        :param p1:      [tuple]     point defined as a tuple: (x, y). 'x' and 'y' can be float or int
        :param p2:      [tuple]     point defined as a tuple: (x, y). 'x' and 'y' can be float or int
        :return:        [tuple]     (slope, intercept)
        """
        slope = (p1[1] - p2[1]) / (p1[0] - p2[0])
        intercept = p1[1] - slope * p1[0]
        return slope, intercept

    def __init__(self):
        self.joystick_to_raw_dir_mapping = JOYSTICK_TO_RAW_DIR_MAPPING
        self.raw_dir_to_label_mapping = RAW_DIR_TO_LABEL_MAPPING
        self.label_to_raw_dir_mapping = LABEL_TO_RAW_DIR_MAPPING
        self.trigger_to_raw_speed_mapping = TRIGGER_TO_RAW_SPEED_MAPPING
        self.raw_speed_to_label = RAW_SPEED_TO_LABEL_MAPPING
        self.label_to_raw_speed_mapping = LABEL_TO_RAW_SPEED_MAPPING
        if len(self.joystick_to_raw_dir_mapping) == 0:
            self.linear = True
            self.slope, self.intercept = self.get_linear_coef((-1, MAX_DIRECTION_LEFT), (1, MAX_DIRECTION_RIGHT))
        else:
            self.linear = False
            self.slope = self.intercept = None

    def get_label_from_raw_dir(self, direction):
        """
        Return the label value from the raw direction value according to the defined mapping.
        :param direction:       [int or float]  direction value (float accepted for linear mapping only)
        :return:                [int]           label value
        """
        if len(self.raw_dir_to_label_mapping) == 0:
            raise ValueError("Linear label mapping not yet implemented")
        try:
            return self.raw_dir_to_label_mapping.index(direction)
        except ValueError as err:
            err.args = (f'"{direction}" is not in the direction to label mapping : {self.raw_dir_to_label_mapping}',)
            raise

    def get_speed_from_xbox_trigger(trigger):
        return _linear_speed_trigger_mapping(trigger)

    def get_raw_dir_from_xbox_joystick(self, joystick):
        """
        Return the raw direction value from the xbox joystick position according to the defined mapping.
        :param joystick:        [float]         joystick position
        :return:                [int]           raw direction value
        """
        if self.linear:
            return self.slope * joystick + self.intercept
        for i, position in self.joystick_to_raw_dir_mapping:
            if joystick < position:
                return self.label_to_raw_dir_mapping[i]
        return self.label_to_raw_dir_mapping[-1]

    def get_label_from_speed(speed):
        return _two_label_speed_mapping(speed)


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
