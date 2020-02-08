from channels.generic.websocket import WebsocketConsumer
from labels.models import Photo
import json
import sys
import os

class LabelsConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.user = self.scope["user"]
        # load or create data dict
        self.data = {}
        self.data_path = os.path.join("media", self.user.username, "labels.json")
        
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
        img_name = img.split("/")[-1].split(".")[0]
        if img_name not in self.data:
            self.data[img_name] = {}
        label = text_data_json['label']
        delete = text_data_json['delete']
        #retag
        if label != 'null':
            self.retag(img, img_name, label, err)
        #delete
        elif delete == 'true':
            self.delete(img, img_name, err)
        else:
            self.send(text_data=json.dumps({'full_label': self.data[img_name], 
                                            'count': None, 
                                            'err': err}))
    
    def retag(self, img, img_name, label, err):
        # edit tag
        self.data[img_name] = label
        with open(self.data_path, "w") as f:
            json.dump(self.data, f)
        self.send(text_data=json.dumps({'full_label': self.data[img_name], 
                                        'count': None, 
                                        'err': err}))

    def delete(self, img, img_name, err):
        # remove tag
        self.data[img_name]["to_delete"] = True
        with open(self.data_path, "w") as f:
            json.dump(self.data, f)
        photos_list = []
        elem_list = Photo.objects.filter(owner=self.user, file=img)
        for elem in elem_list:
            elem.delete()
            try:
                os.remove(elem.file.name)
            except Exception as e:
                err = str(e)
                print(err)
            photos_list = Photo.objects.filter(owner=self.user)
        self.send(text_data=json.dumps({'full_label': None, 
                                        'count': len(photos_list), 
                                        'err': err}))
