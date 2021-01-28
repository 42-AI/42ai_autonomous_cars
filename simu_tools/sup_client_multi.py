import os
import random
import json
import time
from io import BytesIO
import base64
import logging
import argparse

from PIL import Image, ImageEnhance
import numpy as np
from gym_donkeycar.core.sim_client import SDClient

from tensorflow.keras.models import load_model
from numba import cuda

import conf

import matplotlib.pyplot as plt

from copy import deepcopy

###########################################

min_speed = 9.0

class SimpleClient(SDClient):

    THROTTLE = 0
    STEERING = 1

    def __init__(self, model, address, poll_socket_sleep_time=0.01):
        super().__init__(*address, poll_socket_sleep_time=poll_socket_sleep_time)
        self.last_image = None
        self.images_buf = []
        self.last_speed = None
        self.car_loaded = False
        self.model = model
        self.t = time.time()

    def on_msg_recv(self, json_packet):
        if json_packet['msg_type'] == "need_car_config":
            self.send_config()
        
        if json_packet['msg_type'] == "telemetry":
            self.last_speed = json_packet["speed"]
            imgString = json_packet["image"]
            self.last_image = Image.open(BytesIO(base64.b64decode(imgString)))#.convert('L')#.crop((0, conf.crop_top, conf.image_width, conf.image_height))#.convert('L')#.resize((conf.image_width, conf.image_height))#.crop((0, 120 - 96, conf.image_width, conf.image_height))

            if len(self.images_buf) == conf.seq_len:
                self.images_buf.pop(0)
            self.images_buf.append(self.last_image)

            #contrast = ImageEnhance.Contrast(self.last_image)
            #self.last_image = contrast.enhance(1.5)

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
        msg = '{ "msg_type" : "cam_config", "fov" : "150", "fish_eye_x" : "0.0", "fish_eye_y" : "0.0", \
                "img_w" : "' + str(conf.image_width) + '", "img_h" : "' + str(conf.image_height) + '", \
                "img_d" : "' + str(conf.image_depth) + '", "img_enc" : "JPG", \
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
        if len(self.images_buf) == conf.seq_len:
            buf = np.array([np.array(img) for img in self.images_buf])
            input_buf = None
            if conf.image_depth == 1:
                input_buf = np.expand_dims(buf[...,0] / 255.0, (0, 4))
            else:
                input_buf = np.expand_dims(buf / 255.0, 0)
            outputs = self.model.predict(input_buf)
            self.parse_outputs(outputs)

    def parse_outputs(self, outputs):
        steering = 0.0
        throttle = 0.0
        for iO, output in enumerate(outputs):           
            if iO == self.THROTTLE:
                speed_idx = np.argmax(output)
                # don't break if speed < min_speed
                if speed_idx == 0 and self.last_speed < min_speed:
                    speed_idx = 1
                throttle = conf.speed_idx[speed_idx] * conf.throttle_out_scale
            elif iO == self.STEERING:
                angle_idx = np.argmax(output)
                steering = conf.angle_idx[angle_idx] * conf.steering_out_scale
        self.send_controls(steering, throttle)

###########################################
## Make some clients and have them connect with the simulator

def test_clients(model):
    #logging.basicConfig(level=logging.DEBUG)

    # test params
    host = "127.0.0.1" # "trainmydonkey.com" for virtual racing server
    port = 9091
    time_to_drive = 0

    # Start Clients
    client = SimpleClient(model, address=(host, port))

    time.sleep(1)

    # Load Scene message. Only one client needs to send the load scene.
    msg = '{ "msg_type" : "load_scene", "scene_name" : "%s" }' % conf.track
    client.send_now(msg)
    client.send_config()

    # Send driving controls
    start = time.time()
    do_drive = True
    try:
        while (time_to_drive == 0 or time.time() - start < time_to_drive) and do_drive:
            client.update()
            #print(time.time() - client.t, flush=True)
            client.t = time.time()
            if client.aborted:
                print("Client socket problem, stopping driving.")
                do_drive = False
    except KeyboardInterrupt:
        cuda.close()

    time.sleep(3.0)

    # Exit Scene - optionally..
    # msg = '{ "msg_type" : "exit_scene" }'
    # clients[0].send_now(msg)

    # Close down clients
    print("waiting for msg loop to stop")
    client.stop()

    print("clients to stopped")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='prediction server')
    parser.add_argument('--model', type=str, help='model filename')
    args = parser.parse_args()

    model = load_model(args.model)

    test_clients(model)
