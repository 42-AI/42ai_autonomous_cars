"""
Aim of this file: concentrate all tests that check if hardware working fine:
motors, direction, head, camera, other captors...
These tests can potentially be linked to some calibration on hardware set.
In this case it should be clear.
"""

import time

# noinspection PyUnresolvedReferences
import Adafruit_PCA9685

from utils.const import HEAD_DOWN, HEAD_UP
from utils.pivideostream import PiVideoStream


class TestHardware:
    def __init__(self, pwm_freq=50):
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(pwm_freq)
        print("Starting tests...")

    def test_head(self, up=150, down=120):
        time.sleep(1)
        self.pwm.set_pwm(2, 0, up)
        print("Heads should be up (value of:{}".format(up))
        time.sleep(3)
        self.pwm.set_pwm(2, 0, down)
        print("Heads should be down (value of:{}".format(down))
        time.sleep(1)
        self.pwm.set_pwm(2, 0, 0)  # Why reinit on 0?
        print("End of head tests")

    def test_video_stream(self):
        video_stream = PiVideoStream()
        video_stream.test()
        time.sleep(3)
        video_stream.test()
        video_stream.stop()
        print("End of video-stream tests")


if __name__ == '__main__':
    test_hardware = TestHardware()
    test_hardware.test_head(up=HEAD_UP, down=HEAD_DOWN)
    test_hardware.test_video_stream()
