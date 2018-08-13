from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Provider(models.Model):
    name = models.CharField(max_length=255, default="PYANO")
    url = models.URLField(max_length=255)
    is_3rdparty = models.BooleanField(default=False)

class Video(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    videoId = models.CharField(max_length=255)
    annotations = models.TextField(max_length=200000)


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=200000)


class Object(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    label = models.ForeignKey(Category, on_delete=models.CASCADE)


class BoundingBox(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    objectId = models.ForeignKey(Object, on_delete=models.CASCADE)
    timestamp = models.FloatField(default=0.0)
    top = models.FloatField(default=0.0)
    left = models.FloatField(default=0.0)
    width = models.FloatField(default=0.0)
    height = models.FloatField(default=0.0)


# For keyword search
class Topic(models.Model): # topics will be added by admins
    name = models.CharField(max_length=255, default="Shoplifting")

class Keyword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    content = models.CharField(max_length=255, default="")

class SearchResult(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    pref = models.TextField(blank=True)

# For Youtube
class SystemSetting(models.Model):
    name = models.CharField(max_length=255, default="youtube_dev_key")
    value = models.CharField(max_length=4096, blank=True, default="")

class SearchResultPage(models.Model):
    video_idx = models.TextField()

