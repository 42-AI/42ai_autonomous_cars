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
        data_path = os.path.join("media", self.user.username, "labels.json")
        if os.path.exists(data_path):
            with open(data_path) as f:
                self.data = f.read()
        
    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        err = None
        text_data_json = json.loads(text_data)
        img = text_data_json['img']
        img_name = img.split("/")[-1]
        if img_name not in self.data:
            self.data[img_name] = {}
        label = text_data_json['label']
        label_kind = text_data_json['label_kind']
        delete = text_data_json['delete']
        #retag
        if label != 'null':
            self.retag(img, img_name, err)
        #delete
        elif delete == 'true':
            self.delete(img, img_name, err)
        else:
            self.send(text_data=json.dumps({'full_label': self.data[img_name], 
                                            'count': None, 
                                            'err': err}))
    
    def retag(self, img, img_name, err):
        img_file = Photo.objects.filter(owner=self.user, file=img)
        # TODO process label
        self.send(text_data=json.dumps({'full_label': self.data[img_name], 
                                        'count': None, 
                                        'err': err}))

    def delete(self, img, img_name, err):
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
            #TODO remove label
        self.send(text_data=json.dumps({'full_label': self.data[img_name], 
                                        'count': len(photos_list), 
                                        'err': err}))
