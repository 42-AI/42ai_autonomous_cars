from channels.generic.websocket import WebsocketConsumer
from labels.models import Photo
import json
import sys
import os
from datetime import datetime

#from get_data.src import utils_fct

class LabelsConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.user = self.scope["user"]
        # load or create data dict
        self.data_path = os.path.join("media", self.user.username, "labels.json")
        self.data = {}
        
        
    def disconnect(self, close_code):
        pass

    def get_labels(self):
        if os.path.exists(self.data_path):
            with open(self.data_path) as f:
                self.data = json.loads(f.read())

    def receive(self, text_data):
        err = None
        self.get_labels()
        text_data_json = json.loads(text_data)
        img = text_data_json['img']
        if img != 'null':
            img_name = img.split("/")[-1].split(".")[0]
            if img_name not in self.data:
                self.data[img_name] = {}
        label = text_data_json['label']
        delete = text_data_json['delete']
        #retag
        if img != 'null' and label != 'null':
            self.retag(img, img_name, label, err)
        #delete
        elif img != 'null' and delete == 'true':
            self.delete(img, img_name, err)
        else:
            if img == 'null':
                full_label = 'null'
            else:
                full_label = self.data[img_name]
            self.send(text_data=json.dumps({'full_label': full_label, 'data_path': self.data_path, 'err': err}))
    
    def retag(self, img, img_name, label, err):
        # edit tag
        label["label"]["created_by"] = self.user.username
        label["label"]["created_on_date"] = datetime.now().strftime("%Y%m%dT%H-%M-%S%f")[:-2]
        label["dataset"] = []
        #label["label_fingerprint"] = utils_fct.get_label_finger_print(label)
        self.data[img_name] = label
        with open(self.data_path, "w") as f:
            json.dump(self.data, f)
        self.send(text_data=json.dumps({'full_label': self.data[img_name], 'data_path': self.data_path, 'err': err}))

    def delete(self, img, img_name, err):
        photo = Photo.objects.get(owner=self.user, title=img_name)
        photo.to_delete = not photo.to_delete
        self.data[img_name]["to_delete"] = photo.to_delete
        photo.save()
        with open(self.data_path, "w") as f:
            json.dump(self.data, f)
        self.send(text_data=json.dumps({'full_label': self.data[img_name], 'data_path': self.data_path, 'err': err}))
