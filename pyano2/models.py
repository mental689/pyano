from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


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

# For invitation
JOB_CHOICES = (
    (1, _("Reviewer")),
    (2, _("Annotator"))
)


class Invitation(models.Model):
    name = models.CharField(max_length=255, default="")
    job = models.IntegerField(choices=JOB_CHOICES, default=2)
    email = models.EmailField(max_length=254, blank=False)


