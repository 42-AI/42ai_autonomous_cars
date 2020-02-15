from django.db import models
from django.contrib.auth.models import User

class Photo(models.Model):
    title = models.CharField(max_length=255, blank=True)
    owner = models.ForeignKey(User, related_name='photos', on_delete=models.CASCADE)
    file = models.FileField(upload_to='media/')
    to_delete = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
