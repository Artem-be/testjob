from django.db import models

class DiskFile(models.Model):
    name = models.CharField(max_length=255)
    download_link = models.URLField()