import os
import random
import json
import time
from io import BytesIO
import base64
import logging
import argparse

from PIL import Image
import numpy as np
from gym_donkeycar.core.sim_client import SDClient

from inputs import get_gamepad

import threading

import conf

###########################################

class SimpleClient(SDClient):

    def __init__(self, address, poll_socket_sleep_time=0.01):
        super().__init__(*address, poll_socket_sleep_time=poll_socket_sleep_time)
        self.last_image = None
        self.car_loaded = False
        self.steering = 0.0
        self.throttle = 0.0
        self.scale = 65535. / 2.
        self.idx = 0
        self.t = time.time()
        self.min_t = 0.01

    def on_msg_recv(self, json_packet):
        if json_packet['msg_type'] == "need_car_config":
            self.send_config()

        if json_packet['msg_type'] == "car_loaded":
            self.car_loaded = True
        
        if json_packet['msg_type'] == "telemetry":
            imgString = json_packet["image"]
            self.last_image = Image.open(BytesIO(base64.b64decode(imgString)))


            #don't have to, but to clean up the print, delete the image string.
            #del json_packet["image"]

            """if "imageb" in json_packet:
                imgString = json_packet["imageb"]
                image = Image.open(BytesIO(base64.b64decode(imgString)))
                image.save("camera_b.png")
                np_img = np.asarray(image)
                print("imgb:", np_img.shape)

                #don't have to, but to clean up the print, delete the image string.
                del json_packet["imageb"]"""

        #print("got:", json_packet)

    def send_config(self):
        '''
        send three config messages to setup car, racer, and camera
        '''
        racer_name = "Patate42"
        car_name = ""
        bio = "I race robots."
        country = "42"
        guid = "KeepCalm and rm -rf */*"

        # Racer info
        msg = {'msg_type': 'racer_info',
            'racer_name': racer_name,
            'car_name' : car_name,
            'bio' : bio,
            'country' : country,
            'guid' : guid }
        self.send_now(json.dumps(msg))
        time.sleep(0.2)
        
        # Car config
        # body_style = "donkey" | "bare" | "car01" choice of string
        # body_rgb  = (128, 128, 128) tuple of ints
        # car_name = "string less than 64 char"

        msg = '{ "msg_type" : "car_config", "body_style" : "bare", "body_r" : "0", "body_g" : "200", "body_b" : "50", "car_name" : "%s", "font_size" : "100" }' % (car_name)
        self.send_now(msg)

        #this sleep gives the car time to spawn. Once it's spawned, it's ready for the camera config.
        time.sleep(0.2)

        # Camera config
        # set any field to Zero to get the default camera setting.
        # this will position the camera right above the car, with max fisheye and wide fov
        # this also changes the img output to 255x255x1 ( actually 255x255x3 just all three channels have same value)
        # the offset_x moves camera left/right
        # the offset_y moves camera up/down
        # the offset_z moves camera forward/back
        # with fish_eye_x/y == 0.0 then you get no distortion
        # img_enc can be one of JPG|PNG|TGA        
        msg = '{ "msg_type" : "cam_config", "fov" : "' + str(conf.fov) + '", "fish_eye_x" : "0.0", "fish_eye_y" : "0.0", \
                "img_w" : "' + str(conf.image_width) + '", "img_h" : "' + str(conf.image_height) + '", \
                "img_d" : "3", "img_enc" : "JPG", \
                "offset_x" : "' + str(conf.cam_x) + '", "offset_y" : "' + str(conf.cam_y) + '", "offset_z" : "' + str(conf.cam_z) + '", \
                "rot_x" : "' + str(conf.cam_angle) + '" }'
        self.send_now(msg)
        time.sleep(0.2)


    def send_controls(self, steering, throttle):
        msg = { "msg_type" : "control",
                "steering" : steering.__str__(),
                "throttle" : throttle.__str__(),
                "brake" : "0.0" }
        self.send(json.dumps(msg))
        #this sleep lets the SDClient thread poll our message and send it out.
        time.sleep(self.poll_socket_sleep_sec)

    def update(self):
        changed = False
        # catch every X/Y change event from GamePad (Left Joystick)
        events = get_gamepad()
        for event in events:
            #print(event.ev_type, event.code, event.state)
            if event.ev_type == "Absolute":
                if event.code == "ABS_X":
                    if abs(self.steering - event.state / self.scale) > 0.01:
                        self.steering = event.state / self.scale
                        changed = True
                elif event.code == "ABS_Y":
                    if abs(self.throttle - event.state / self.scale) > 0.01:
                        self.throttle = event.state / self.scale
                        changed = True
        if changed:
            self.send_controls(self.steering, self.throttle)
        # Use threads to save current image (threading is needed to not block the main loop while image is writen)
        if time.time() - self.t > self.min_t:
            if threading.active_count() <= conf.max_threads:
                t = threading.Thread(target=self.save_data, args=[self.idx])
                t.start()
                self.idx += 1

    def save_data(self, idx):
        if self.last_image:
            self.last_image.save(os.path.join(conf.logs_dir, str(idx) + "_cam-image_array_.jpg"))
            data = {"cam/image_array": str(self.idx) + "_cam-image_array_.jpg",
                "user/throttle": self.throttle,
                "user/angle": self.steering}
            with open(os.path.join(conf.logs_dir, "record_" + str(idx) + ".json"), "w") as f:
                json.dump(data, f)

###########################################
## Make some clients and have them connect with the simulator

def test_clients():
    logging.basicConfig(level=logging.DEBUG)

    # test params
    host = "127.0.0.1" # "trainmydonkey.com" for virtual racing server
    port = 9091

    # Start Clients
    client = SimpleClient(address=(host, port))

    time.sleep(1)

    # Load Scene message. Only one client needs to send the load scene.
    msg = '{ "msg_type" : "load_scene", "scene_name" : "%s" }' % conf.track
    client.send_now(msg)
    client.send_config()

    # Send driving controls
    try:
        while True:
            client.update()
    except KeyboardInterrupt:
        pass
    

    time.sleep(3.0)

    # Exit Scene - optionally..
    # msg = '{ "msg_type" : "exit_scene" }'
    # clients[0].send_now(msg)

    # Close down clients
    print("waiting for msg loop to stop")
    client.stop()
    print("clients to stopped")


if __name__ == "__main__":
    test_clients()
