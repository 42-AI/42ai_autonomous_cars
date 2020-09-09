from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.conf import settings
from django.utils.encoding import smart_str
from wsgiref.util import FileWrapper
import mimetypes
import os
from PIL import Image
import json

from .forms import PhotoForm
from .models import Photo

class uploadView(View):
    def __init__(self, *args, **kwargs):
        
        super(uploadView, self).__init__(*args, **kwargs)
        self.labels = None
        self.labels_data = None
    
    def get(self, request):
        photos_list = Photo.objects.filter(owner=self.request.user)
        return render(self.request, 'labels/labels.html', {'photos': photos_list})

    def post(self, request):
        form = PhotoForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.title = photo.file.name.split(".")[0]
            photo.owner = self.request.user
            photo.file.name = os.path.join(photo.owner.username, photo.file.name)
            photo.save()
            #get labels and refresh value
            refresh = self.get_labels(request)
            data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url, 'refresh': refresh}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)

    def get_labels(self, request):
        refresh = False
        if self.labels == None:
            labels = Photo.objects.filter(owner=request.user, file__endswith=".json")
            if len(labels):
                self.labels = labels[0].file.name
                with open(self.labels, "r") as f:
                    self.labels_data = json.load(f)
        if self.labels_data != None:
            if len(Photo.objects.filter(owner=request.user).exclude(file__endswith=".json")) != len(self.labels_data):
                self.refresh_labels(request)
                refresh = True
        return refresh

    def refresh_labels(self, request):
        images = Photo.objects.filter(owner=request.user).exclude(file__endswith=".json")
        for image in images:
            img_id = image.file.name.split("/")[-1].split(".")[0]
            if img_id in self.labels_data:
                img_label = self.labels_data[img_id]
                image.to_delete = True if "to_delete" in img_label and img_label["to_delete"] == True else False
                image.edited = False if img_label["label"]["created_by"] == "auto" else True
                image.save()
            else:
                image.delete()
                try:
                    os.remove(image.file.name)
                except:
                    pass

@login_required
def delete_all(request):
    if request.method == 'POST':
        photos_list = Photo.objects.filter(owner=request.user)
        for item in photos_list:
            try:
                os.remove(item.file.name)
            except:
                pass
        photos_list.delete()
    return redirect('/labels/')

def edit_fingerprint(file_path):
    labels = None
    with open(file_path, "r") as f:
        labels = json.load(f)
    for label in labels:
        if "tmp_fingerprint" in labels[label] and \
                ("to_delete" not in labels[label] or labels[label]["to_delete"] == False):
            labels[label]["label_fingerprint"] = labels[label]["tmp_fingerprint"]
        labels[label].pop("tmp_fingerprint", None)
    with open(file_path, "w") as f:
        json.dump(labels, f, indent=4)

@login_required
def save(request):
    labels_file = Photo.objects.filter(owner=request.user, file__endswith=".json")
    if len(labels_file) == 1:
        file_name = labels_file[0].file.name
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        edit_fingerprint(file_path)
        file_wrapper = FileWrapper(open(file_path,'rb'))
        file_mimetype = mimetypes.guess_type(file_path)
        response = HttpResponse(file_wrapper, content_type=file_mimetype )
        response['X-Sendfile'] = file_path
        response['Content-Length'] = os.stat(file_path).st_size
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
        return response
    return redirect('/labels/')
