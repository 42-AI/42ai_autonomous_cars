import time

# noinspection PyUnresolvedReferences
from picamera.array import PiRGBArray
# noinspection PyUnresolvedReferences
from picamera import PiCamera
# noinspection PyUnresolvedReferences
from PIL import Image
from threading import Thread
from conf.path import HARDWARE_TEST_IMAGES_DIRECTORY
from conf.const import IMAGE_SIZE, FRAME_RATE, EXPOSURE_MODE


#initialize the camera
def init_cam():
    camera = PiCamera()
    camera.resolution = IMAGE_SIZE
    camera.framerate = FRAME_RATE
    camera.exposure_mode = EXPOSURE_MODE
    rawCapture = PiRGBArray(camera, size=IMAGE_SIZE)
    time.sleep(2)
    return camera, rawCapture


class PiVideoStream:
    def __init__(self):
        # initialize the camera and stream
        self.camera, self.rawCapture = init_cam()
        self.stream = self.camera.capture_continuous(self.rawCapture,
                                                     format="rgb", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

    def test(self):
        self.start()
        frame = self.read()
        img = Image.fromarray(frame)
        timestamp = time.time()
        img.save("{}test_{}.png".format(HARDWARE_TEST_IMAGES_DIRECTORY, timestamp))
        print("An image should have been saved: test_{}.png".format(timestamp))


if __name__ == '__main__':
    video_stream = PiVideoStream().start()
    video_stream.test()
    video_stream.stop()
