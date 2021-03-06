import bisect

from conf.const import MAX_DIRECTION_LEFT, MAX_DIRECTION_RIGHT, MAX_SPEED, STOP_SPEED
from conf.const import RAW_DIR_TO_LABEL_MAPPING, JOYSTICK_TO_RAW_DIR_MAPPING, LABEL_TO_RAW_DIR_MAPPING
from conf.const import TRIGGER_TO_RAW_SPEED_MAPPING, RAW_SPEED_TO_LABEL_MAPPING, LABEL_TO_RAW_SPEED_MAPPING


class CarMapping:

    @staticmethod
    def get_linear_coef(p1, p2):
        """
        Compute the joystick_slope and joystick_intercept of the joystick_linear_mapping function passing through point p1 and point p2.
        y1 = a * x1 + b
        y2 = a * x2 + b
        -> (y1 - y2) = a (x1 - x2) -> a = (y1 - y2) / (x1 - x2)
        -> b = y1 - a * x1
        :param p1:      [tuple]     point defined as a tuple: (x, y). 'x' and 'y' can be float or int
        :param p2:      [tuple]     point defined as a tuple: (x, y). 'x' and 'y' can be float or int
        :return:        [tuple]     (joystick_slope, joystick_intercept)
        """
        slope = (p1[1] - p2[1]) / (p1[0] - p2[0])
        intercept = p1[1] - slope * p1[0]
        return slope, intercept

    @staticmethod
    def get_closest_value_index_in_sorted_list(value, list_):
        """
        Assumes 'list_' is sorted. Returns closest item index to 'value'.

        If two numbers are equally close, return the smallest index.
        """
        if value <= list_[0]:
            return 0
        if value >= list_[-1]:
            return len(list_) - 1
        pos = bisect.bisect_left(list_, value)
        before = list_[pos - 1]
        after = list_[pos]
        if after - value < value - before:
            return pos
        else:
            return pos - 1

    def __init__(self):
        self.joystick_to_raw_dir_mapping = JOYSTICK_TO_RAW_DIR_MAPPING
        self.raw_dir_to_label_mapping = RAW_DIR_TO_LABEL_MAPPING
        self.label_to_raw_dir_mapping = LABEL_TO_RAW_DIR_MAPPING
        self.trigger_to_raw_speed_mapping = TRIGGER_TO_RAW_SPEED_MAPPING
        self.raw_speed_to_label_mapping = RAW_SPEED_TO_LABEL_MAPPING
        self.label_to_raw_speed_mapping = LABEL_TO_RAW_SPEED_MAPPING
        self.joystick_linear_mapping = self.trigger_linear_mapping = False
        self.joystick_slope, self.joystick_intercept = self.get_linear_coef((-1, MAX_DIRECTION_LEFT),
                                                                            (1, MAX_DIRECTION_RIGHT))
        self.trigger_slope, self.trigger_intercept = self.get_linear_coef((0, STOP_SPEED),
                                                                          (1, MAX_SPEED))
        self.normal_joystick_slope, self.normal_joystick_intercept = self.get_linear_coef((MAX_DIRECTION_LEFT, -1),
                                                                                          (MAX_DIRECTION_RIGHT, 1))
        self.normal_trigger_slope, self.normal_trigger_intercept = self.get_linear_coef((STOP_SPEED, 0),
                                                                                        (MAX_SPEED, 1))
        if len(self.joystick_to_raw_dir_mapping) == 0:
            self.joystick_linear_mapping = True
        if len(self.trigger_to_raw_speed_mapping) == 0:
            self.trigger_linear_mapping = True

    def get_label_from_raw_dir(self, direction):
        """
        Return the direction label associated to the raw direction value based on the defined mapping.
        :param direction:       [int or float]  raw direction value (float accepted for joystick_linear_mapping mapping only)
        :return:                [int]           direction label value
        """
        return CarMapping.get_closest_value_index_in_sorted_list(direction, self.raw_dir_to_label_mapping)

    def get_label_from_raw_speed(self, speed, stop_speed_label=None):
        """
        Return the speed label associated to the raw speed value based on the defined mapping.
        :param speed:           [int or float]  raw speed value (float accepted for joystick_linear_mapping mapping only)
        :param stop_speed_label:[int]           Label value if speed == STOP_SPEED.
                                                If None, will return 0 when speed == STOP_SPEED.
        :return:                [int]           speed label value
        """
        if stop_speed_label is not None and speed >= STOP_SPEED:
            return stop_speed_label
        return CarMapping.get_closest_value_index_in_sorted_list(speed, self.raw_speed_to_label_mapping)

    def get_raw_speed_from_xbox_trigger(self, trigger):
        """
        Return the raw speed value from the xbox trigger position according to the defined mapping.
        :param trigger:         [float]         trigger position
        :return:                [int]           raw direction value
        """
        if self.trigger_linear_mapping:
            return round(self.trigger_slope * trigger + self.trigger_intercept)
        for i, position in self.trigger_to_raw_speed_mapping:
            if trigger < position:
                return self.label_to_raw_speed_mapping[i]
        return self.label_to_raw_speed_mapping[-1]

    def get_raw_dir_from_xbox_joystick(self, joystick):
        """
        Return the raw direction value from the xbox joystick position according to the defined mapping.
        :param joystick:        [float]         joystick position
        :return:                [int]           raw direction value
        """
        if self.joystick_linear_mapping:
            return round(self.joystick_slope * joystick + self.joystick_intercept)
        for i, position in self.joystick_to_raw_dir_mapping:
            if joystick < position:
                return self.label_to_raw_dir_mapping[i]
        return self.label_to_raw_dir_mapping[-1]

    def get_normalized_direction(self, direction):
        """
        Return the normalized direction from a raw direction value.
        Normalized value is between -1 and 1.
        :param direction:   [int]   Raw direction value
        :return:            [float] Normalized direction
        """
        return round(self.normal_joystick_slope * direction + self.normal_joystick_intercept, 2)

    def get_normalized_speed(self, speed):
        """
        Return the normalized speed from a raw speed value.
        Normalized value is between 0 and 1.
        :param speed:       [int]   Raw speed value
        :return:            [float] Normalized speed
        """
        return round(self.normal_trigger_slope * speed + self.normal_trigger_intercept, 2)

    def get_raw_dir_from_label(self, label):
        """
        Return the raw direction value from the from the predicted label according to the defined mapping.
        :param label:           [int]   predicted label
        :return:                [int]   raw direction value
        """
        try:
            return self.label_to_raw_dir_mapping[label]
        except IndexError as err:
            err.args = (f'Label "{label}" is not a valid index of the mapping : {self.label_to_raw_dir_mapping}',)
            raise

    def get_raw_speed_from_label(self, label):
        """
        Return the raw speed value from the from the predicted label according to the defined mapping.
        :param label:           [int]   predicted label
        :return:                [int]   raw speed value
        """
        try:
            return self.label_to_raw_speed_mapping[label]
        except IndexError as err:
            err.args = (f'Label "{label}" is not a valid index of the mapping : {self.label_to_raw_speed_mapping}',)
            raise
