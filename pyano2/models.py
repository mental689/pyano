from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from survey.models import Survey

from django.utils.timezone import now


# For keyword search
class Topic(models.Model): # topics will be added by admins
    name = models.CharField(max_length=255, default="Shoplifting")
    created = models.DateTimeField(auto_created=True, default=now, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True)

class Keyword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    content = models.CharField(max_length=255, default="")
    created = models.DateTimeField(auto_created=True, default=now, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True)

class SearchResult(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    pref = models.TextField(blank=True)
    created = models.DateTimeField(auto_created=True, default=now, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True)


# For Youtube
class SystemSetting(models.Model):
    name = models.CharField(max_length=255, default="youtube_dev_key")
    value = models.CharField(max_length=4096, blank=True, default="")

# For invitation
JOB_CHOICES = (
    (1, _("Reviewer")),
    (2, _("Annotator"))
)
STATUSES = (
    (0, _("Not decided")),
    (1, _("Accepted")),
    (2, _("Declined"))
)


class Invitation(models.Model):
    name = models.CharField(max_length=255, default="")
    job = models.IntegerField(choices=JOB_CHOICES, default=2)
    email = models.EmailField(max_length=254, blank=False, null=False)
    invitor = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False, related_name='invitors')
    invited = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='invitees')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, blank=False, null=False, related_name='surveys')
    uuid = models.CharField(_("Invitation unique identifier"), max_length=255, unique=True)
    done = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUSES, default=0)
    created = models.DateTimeField(auto_created=True, default=now, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True)


class Alternative(models.Model):
    name = models.CharField(max_length=255, default="", blank=True, null=False)
    email = models.EmailField(max_length=254, blank=True, null=False)
    invitation = models.ForeignKey(Invitation, blank=True, null=True, related_name="alternatives", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_created=True, default=now, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True)



