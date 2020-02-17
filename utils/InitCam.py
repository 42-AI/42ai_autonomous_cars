import time
from picamera import PiCamera
from conf.const import IMAGE_SIZE, FRAME_RATE, EXPOSURE_MODE
from picamera.array import PiRGBArray


class InitCam:
    """initialize the camera"""
    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = IMAGE_SIZE
        self.camera.framerate = FRAME_RATE
        self.camera.exposure_mode = EXPOSURE_MODE
        self.rawCapture = PiRGBArray(self.camera, size=IMAGE_SIZE)
        time.sleep(2)
        return self.camera, self.rawCapture
