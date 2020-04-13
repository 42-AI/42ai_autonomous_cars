class PiCamera:

    def __init__(self):
        self.picture_list = []

    def capture_continuous(self, rawCapture, format, use_video_port=True):
        for pic in self.picture_list:
            yield pic


class PiRGBArray:

    def __init__(self, camera, size):
        self.camera = camera
        self.image_size = size
        self.array = None

    def truncate(self, val):
        self.array = None
