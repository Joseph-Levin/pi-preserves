from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import DateTimeField
from datetime import datetime

from .storage import PiStorage



# class File(models.Model):
#     # CHANGE maybe to FilePathField?
#     # Also look into FileField
#     name = models.CharField(max_length=255)
#     size = models.IntegerField()
#     author = models.ForeignKey(User, 
#         on_delete=models.CASCADE, related_name="file", null=True)

#     def __str__(self):
#         return self.name + ", " + str(self.size)

def unique_dir_path(model, filename):
    return 'user/{0}/{1}/{2}'.format(model.creator.id, datetime.now().strftime('%Y-%m-%d--%H-%M-%S'), filename)

class File(models.Model):
    description = models.CharField(max_length=255, blank=True)
    file = models.FileField(storage=PiStorage, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file', null=True)