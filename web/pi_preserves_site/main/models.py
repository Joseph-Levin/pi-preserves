from django.db import models


class File(models.Model):
    # CHANGE maybe to FilePathField?
    # Also look into FileField
    name = models.CharField(max_length=255)
    size = models.IntegerField()

    def __str__(self):
        return self.name + ", " + str(self.size)
