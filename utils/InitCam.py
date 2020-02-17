import time
from picamera import PiCamera
from conf.const import IMAGE_SIZE, FRAME_RATE, EXPOSURE_MODE
from picamera.array import PiRGBArray



#initialize the camera

def InitCam():
    camera = PiCamera()
    camera.resolution = IMAGE_SIZE
    camera.framerate = FRAME_RATE
    camera.exposure_mode = EXPOSURE_MODE
    rawCapture = PiRGBArray(camera, size=IMAGE_SIZE)
    time.sleep(2)
    return camera, rawCapture
