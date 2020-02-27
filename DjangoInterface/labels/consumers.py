from channels.generic.websocket import WebsocketConsumer
from labels.models import Photo
import json
import sys
import os
from datetime import datetime

from get_data.src import utils_fct

class LabelsConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.user = self.scope["user"]
        self.data_path = None
        self.data = {}
        
        
    def disconnect(self, err):
        self.send(text_data=json.dumps({'retaged': False, 'img': None, 'full_label': None, 'data_path': None, 'err': err}))

    def get_labels(self):
        if self.data_path == None:
            if os.path.exists(os.path.join("media", self.user.username)):
                for f in os.listdir(os.path.join("media", self.user.username)):
                    if f.endswith(".json"):
                        self.data_path = os.path.join("media", self.user.username, f)
            else:
                return False
        if self.data_path != None:
            with open(self.data_path, "r") as f:
                self.data = json.load(f)
        elif len(os.listdir(os.path.join("media", self.user.username))):
            self.disconnect("No JSON file found")
            return False
        return True

    def receive(self, text_data):
        err = None
        if self.get_labels() == True:
            text_data_json = json.loads(text_data)
            img = text_data_json['img']
            img_name = None
            if img != 'null':
                img_name = img.split("/")[-1].split(".")[0]
                if img_name not in self.data:
                    self.data[img_name] = {}
            label = text_data_json['label']
            to_delete = text_data_json['to_delete']
            #retag
            if img != 'null' and label != 'null':
                self.retag(img, img_name, label, err)
            #delete
            elif img != 'null' and to_delete == 'true':
                self.delete(img, img_name, err)
            else:
                if img == 'null':
                    full_label = 'null'
                else:
                    full_label = self.data[img_name]
                self.send(text_data=json.dumps({'retaged': False, 'img': None, 'full_label': full_label, 'data_path': self.data_path, 'err': err}))
    
    def retag(self, img, img_name, label, err):
        photo = Photo.objects.get(owner=self.user, title=img_name)
        photo.edited = True
        photo.save()
        # edit tag
        label["label"]["created_by"] = self.user.username
        label["label"]["created_on_date"] = datetime.now().strftime("%Y%m%dT%H-%M-%S-%f")
        label["dataset"] = []
        label["tmp_fingerprint"] = utils_fct.get_label_finger_print(label)
        self.data[img_name] = label
        with open(self.data_path, "w") as f:
            json.dump(self.data, f)
        self.send(text_data=json.dumps({'retaged': True, 'img': img, 'full_label': self.data[img_name], 'data_path': self.data_path, 'err': err}))

    def delete(self, img, img_name, err):
        photo = Photo.objects.get(owner=self.user, title=img_name)
        photo.to_delete = not photo.to_delete
        self.data[img_name]["to_delete"] = photo.to_delete
        photo.save()
        with open(self.data_path, "w") as f:
            json.dump(self.data, f)
        self.send(text_data=json.dumps({'retaged': False, 'img': None, 'full_label': self.data[img_name], 'data_path': self.data_path, 'err': err}))