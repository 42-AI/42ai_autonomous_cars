import os
import random
import json
import time
from io import BytesIO
import base64
import logging
import argparse

from PIL import Image, ImageEnhance
#import cv2
import numpy as np
from gym_donkeycar.core.sim_client import SDClient

from tensorflow.keras.models import load_model
from numba import cuda

import conf

import matplotlib.pyplot as plt

import keyboard

###########################################

class SimpleClient(SDClient):

    THROTTLE = 0
    STEERING = 1

    def __init__(self, model, visu, address, poll_socket_sleep_time=0.01):
        super().__init__(*address, poll_socket_sleep_time=poll_socket_sleep_time)
        self.last_image = None
        self.last_speed = None
        self.car_loaded = False
        self.visu = visu
        self.model = model
        self.t = time.time()
        self.got_img = False

    def send_config(self):
        '''
        send three config messages to setup car, racer, and camera
        '''
        racer_name = "Patate42"
        car_name = "Patate"
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
                "img_d" : "' + str(conf.image_depth) + '", "img_enc" : "JPG", \
                "offset_x" : "' + str(conf.cam_x) + '", "offset_y" : "' + str(conf.cam_y) + '", "offset_z" : "' + str(conf.cam_z) + '", \
                "rot_x" : "' + str(conf.cam_angle) + '" }'
        self.send_now(msg)
        time.sleep(0.2)
        
    def on_msg_recv(self, json_packet):
        if json_packet['msg_type'] == "need_car_config":
            self.send_config()
        
        if json_packet['msg_type'] == "telemetry":
            self.last_speed = json_packet["speed"]
            imgString = json_packet["image"]
            self.last_image = Image.open(BytesIO(base64.b64decode(imgString)))
            #self.last_image = cv2.imdecode(np.frombuffer(base64.b64decode(imgString), np.uint8), cv2.IMREAD_COLOR)
            
            self.got_img = True
            """#don't have to, but to clean up the print, delete the image string.
            del json_packet["image"]
            
        if "imageb" in json_packet:
            imgString = json_packet["imageb"]
            image = Image.open(BytesIO(base64.b64decode(imgString)))
            image.save("camera_b.png")
            np_img = np.asarray(image)
            print("imgb:", np_img.shape)
            #don't have to, but to clean up the print, delete the image string.
            del json_packet["imageb"]
            
        #print("got:", json_packet)"""

    def send_controls(self, steering, throttle):
        msg = { "msg_type" : "control",
                "steering" : steering.__str__(),
                "throttle" : throttle.__str__(),
                "brake" : "0.0" }
        self.send(json.dumps(msg))
        #this sleep lets the SDClient thread poll our message and send it out.
        time.sleep(self.poll_socket_sleep_sec)

    #n = 0
    def update(self):

        if keyboard.is_pressed('r'):
            self.reset_car()
            
        if self.got_img:

            img = self.last_image
            
            #ret, thresh = cv2.threshold(img, conf.thresh, 255, cv2.THRESH_BINARY)

            """input_img = np.empty((1, 2, conf.image_height - conf.crop_top, conf.image_width, conf.image_depth), dtype=np.float32)
            input_img[0,0] = np.expand_dims(np.array(img)[...,0], (0, 3))
            input_img[0,1] = np.expand_dims(np.array(thresh)[...,0], (0, 3))"""
            
            if conf.image_depth == 3:
                input_img = np.expand_dims(np.asarray(img) / 255.0, 0)
            elif conf.image_depth == 1:
                input_img = np.expand_dims(np.asarray(img.convert("L")) / 255.0, 0)

            #m = 120. / 255.
            #input_img[input_img < m] = np.mean(input_img)
            
            outputs = self.model.predict(input_img)
            
            self.got_img = False # prevent multiples inferences on same img

            # check image and predicted direction
            if self.visu:
                try:
                    plt.cla()
                    if conf.image_depth == 1:
                        plt.imshow(np.squeeze(input_img), cmap="gray")
                    else:
                        plt.imshow(np.squeeze(input_img))
                    plt.plot((conf.image_width // 2, np.argmax(outputs[1]) * conf.image_width  // (len(conf.angle_idx) - 1)), (conf.image_height, 0))
                    plt.pause(0.01)
                    plt.draw()
                except Exception as e:
                    print("exception : %s" % str(e))
            
            self.parse_outputs(outputs)

            #label = np.argmax(outputs[1])
            #img.save(os.path.join("tmp", str(self.n) + "_" + str(label) + ".jpg"))
            #self.n += 1

    def parse_outputs(self, outputs):
        speed_idx = np.argmax(outputs[self.THROTTLE])
        # don't brake if speed < min_speed
        if speed_idx == 0 and self.last_speed < conf.min_speed:
            speed_idx = 1
        throttle = conf.speed_idx[speed_idx] * conf.throttle_out_scale
        angle_idx = np.argmax(outputs[self.STEERING])
        steering = conf.angle_idx[angle_idx] * conf.steering_out_scale
 
        self.send_controls(steering, throttle)

    def reset_car(self):
        msg = {"msg_type": "reset_car"}
        self.send(json.dumps(msg))

###########################################
## Make some clients and have them connect with the simulator

def test_clients(model, visu):
    #logging.basicConfig(level=logging.DEBUG)

    # test params
    host = "127.0.0.1" #"127.0.0.1"# "trainmydonkey.com" for virtual racing server
    port = 9091

    # Start Clients
    client = SimpleClient(model, visu, address=(host, port))

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
    parser.add_argument('--v', action='store_true')
    args = parser.parse_args()

    model = load_model(args.model)

    test_clients(model, args.v)
