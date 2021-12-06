from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import DateTimeField
from datetime import datetime
from os.path import basename, splitext

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

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}/{2}'.format(instance.author.id, datetime.now().strftime('%Y-%m/%d'), filename)


class File(models.Model):
    description = models.CharField(max_length=255, blank=True)
    file = models.FileField(storage=PiStorage, upload_to=user_directory_path, null=True,)
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file', null=True)
    shared_to = models.ManyToManyField(User, blank=True, related_name='shared_files')
    public = models.BooleanField(default=False)
    parent_folder = models.ForeignKey('Folder', on_delete=models.CASCADE, related_name='file')
    size = models.IntegerField()
    hash = models.CharField(blank=True, max_length=32)

    @property
    def extension(self):
        root, ext = splitext(self.file.name)
        return str(ext.lower())

    @property
    def filename(self):
        return str(basename(self.file.name))
    

class Folder(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folder')
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name