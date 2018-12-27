import logging

import vision
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now, timedelta
from django.utils.translation import ugettext_lazy as _
from survey.models import Survey, Video
from vision.track.interpolation import LinearFill

from pyano2.vatic.qa import tolerable
from pyano2.downloader.youtube import *


# For keyword search
class Topic(models.Model): # topics will be added by admins
    name = models.CharField(max_length=255, default="Shoplifting")
    created = models.DateTimeField(auto_created=True, default=now, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True)

class FreebaseTopic(models.Model):
    googleId = models.CharField(max_length=32, default="/m/01hrs3", unique=True) # default value is for shoplifting crime
    pyanoTopic = models.ManyToManyField(Topic, related_name="freebases", null=False)
    created = models.DateTimeField(auto_created=True, default=now, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True)

class Keyword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='keywords', null=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='keywords', null=True)
    content = models.CharField(max_length=255, default="")
    created = models.DateTimeField(auto_created=True, default=now, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True)

class SearchResult(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, related_name="searches")
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
    (2, _("Declined")),
    (3, _('Expired'))
)


class Invitation(models.Model):
    name = models.CharField(max_length=255, default="")
    job = models.IntegerField(choices=JOB_CHOICES, default=2)
    email = models.EmailField(max_length=254, blank=False, null=False)
    invitor = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False, related_name='invitors')
    invited = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='invitees')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, blank=False, null=False, related_name='surveys')
    message = models.TextField(blank=True, null=False, default='', auto_created=True, max_length=4096)
    uuid = models.CharField(_("Invitation unique identifier"), max_length=255, unique=True)
    done = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUSES, default=0)
    created = models.DateTimeField(auto_created=True, default=now, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True)

    def is_expired(self):
        if now() - self.created > timedelta(+7) or self.status == 3:
            self.status = 3
            self.save()
            return True
        return False


class Alternative(models.Model):
    name = models.CharField(max_length=255, default="", blank=True, null=False)
    email = models.EmailField(max_length=254, blank=True, null=False)
    invitation = models.ForeignKey(Invitation, blank=True, null=True, related_name="alternatives", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_created=True, default=now, blank=False, null=False)
    updated = models.DateTimeField(auto_now=True)


class Credit(models.Model):
    survey = models.ForeignKey(Survey, null=True, related_name='points', on_delete=models.CASCADE)
    point = models.FloatField(default=1.0, help_text=_("The number of credits user will be paid for a job done."))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


# For VATIC
class VATICVideo(models.Model):
    slug = models.CharField(max_length=250)
    width = models.IntegerField()
    height = models.IntegerField()
    totalframes = models.IntegerField()
    location = models.CharField(max_length=250)
    skip = models.IntegerField(default=0, null=False)
    perobjectbonus = models.FloatField(default=0)
    completionbonus = models.FloatField(default=0)
    pyano_video = models.ForeignKey(Video, related_name='vaticvideos', null=True, on_delete=models.CASCADE)
    isfortraining = models.BooleanField(default=False)
    blowradius = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def getframepath(frame, base=None):
        l1 = int(frame / 10000)
        l2 = int(frame / 100)
        path = "{0}/{1}/{2}.jpg".format(l1, l2, frame)
        if base is not None:
            path = "{0}/{1}".format(base, path)
        return path

    def cost(self):
        cost = 0
        for segment in self.segments.all():
            cost += segment.cost
        return cost

    def numjobs(self):
        count = 0
        for segment in self.segments.all():
            for job in segment.jobs.all():
                count += 1
        return count

    def numcompleted(self):
        count = 0
        for segment in self.segments.all():
            for job in segment.jobs.all():
                if job.completed:
                    count += 1
        return count


class VATICLabel(models.Model):
    text = models.CharField(max_length=250)
    video = models.ForeignKey(VATICVideo, related_name='labels', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class VATICAttribute(models.Model):
    text = models.CharField(max_length=250)
    label = models.ForeignKey(VATICLabel, related_name='attributes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


class VATICSegment(models.Model):
    """
    The original VATIC uses a segment as unit of jobs.
    """
    video = models.ForeignKey(VATICVideo, related_name='segments', on_delete=models.CASCADE)
    start = models.IntegerField(null=False)
    stop = models.IntegerField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def paths(self):
        paths = []
        for job in self.jobs.all():
            if job.useful:
                paths.extend(job.paths)
        return paths

    def cost(self):
        cost = 0
        for job in self.jobs.all():
            cost += job.cost
        return cost


class VATICJobGroup(models.Model):
    title = models.CharField(max_length=250, null=False)
    description = models.CharField(max_length=250, null=False)
    duration = models.IntegerField(null=False)
    cost = models.ForeignKey(Credit, related_name='jobgroups', on_delete=models.CASCADE)
    keywords = models.CharField(max_length=250, null=False)
    height = models.IntegerField(null=False, default=650)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class VATICJob(models.Model):
    segment = models.ForeignKey(VATICSegment, related_name='jobs', on_delete=models.CASCADE, help_text=_('Segment'))
    istraining = models.BooleanField(default=False, help_text=_('Is this job for training?'))
    group = models.ForeignKey(VATICJobGroup, related_name='jobs', on_delete=models.CASCADE, help_text=_('Group'))
    completed = models.BooleanField(default=False, help_text=_('Is the job completed?'))
    paid = models.BooleanField(default=False, help_text=_('Is the annotator paid?'))
    published = models.BooleanField(default=False, help_text=_('Is this published?'))
    ready = models.BooleanField(default=False, help_text=_('Whether if the job is ready.'))
    bonus = models.FloatField(default=0, help_text=_('Bonus'))
    uuid = models.CharField(_("Job unique identifier"), max_length=255, unique=True, help_text=_('UUID'))
    training_overlap = models.FloatField(default=0.25, null=False)
    training_tolerance = models.FloatField(default=0.2, null=False)
    training_mistakes = models.IntegerField(default=0, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def getpage(self):
        return "?id={0}".format(self.id)

    def markastraining(self):
        """
        Marks this job as the result of a training run. This will automatically
        swap this job over to the training video and produce a replacement.
        """
        replacement = VATICJob(segment=self.segment, group=self.group)
        self.segment = self.segment.video.trainwith.segments[0]
        self.group = self.segment.jobs[0].group
        self.istraining = True

        logging.debug("Job is now training and replacement built")

        return replacement

    def invalidate(self):
        """
        Invalidates this path because it is poor work. The new job will be
        respawned automatically for different workers to complete.
        """
        self.useful = False
        # is this a training task? if yes, we don't want to respawn
        if not self.istraining:
            return VATICJob(segment=self.segment, group=self.group)

    def trainingjob(self):
        train_of = VATICTrainingOf.objects.filter(video_test=self.segment.video)
        if len(train_of) > 0:
            return train_of[0]
        return None

    def validator(self):
        return tolerable(self.training_overlap, self.training_tolerance, self.training_mistakes)

    def cost(self):
        if not self.completed:
            return 0
        return self.group.cost.point + self.bonus

    def __iter__(self):
        return self.paths


class VATICPath(models.Model):
    job = models.ForeignKey(VATICJob, related_name='paths', on_delete=models.CASCADE)
    label = models.ForeignKey(VATICLabel, related_name='paths', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    interpolatecache = None

    def getboxes(self, interpolate=False, bind=False, label=False):
        result = [x.getbox() for x in self.boxes.all()]
        result.sort(key=lambda x: x.frame)
        if interpolate:
            if not self.interpolatecache:
                self.interpolatecache = LinearFill(result)
            result = self.interpolatecache

        if bind:
            result = VATICPath.bindattributes(self.attributes.all(), result)

        if label:
            for box in result:
                box.attributes.insert(0, self.label.text)

        return result

    def bindattributes(self, attributes, boxes):
        attributes = sorted(attributes, key=lambda x: x.frame)

        byid = {}
        for attribute in attributes:
            if attribute.attributeid not in byid:
                byid[attribute.attributeid] = []
            byid[attribute.attributeid].append(attribute)

        for attributes in byid.values():
            for prev, cur in zip(attributes, attributes[1:]):
                if prev.value:
                    for box in boxes:
                        if prev.frame <= box.frame < cur.frame:
                            if prev.attribute not in box.attributes.all():
                                box.attributes.append(prev.attribute)
            last = attributes[-1]
            if last.value:
                for box in boxes:
                    if last.frame <= box.frame:
                        if last.attribute not in box.attributes:
                            box.attributes.append(last.attribute)

        return boxes

    def __repr__(self):
        return "<Path {0}>".format(self.id)


class AttributeAnnotation(models.Model):
    path = models.ForeignKey(VATICPath, related_name='attributes', on_delete=models.CASCADE)
    attribute = models.ForeignKey(VATICAttribute, on_delete=models.CASCADE)
    frame = models.IntegerField()
    value = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return ("AttributeAnnotation(pathid = {0}, "
                "attributeid = {1}, "
                "frame = {2}, "
                "value = {3})").format(self.path.id,
                                       self.attribute.id,
                                       self.frame,
                                       self.value)


class VATICBox(models.Model):
    path = models.ForeignKey(VATICPath, related_name='boxes', on_delete=models.CASCADE)
    xtl = models.IntegerField()
    ytl = models.IntegerField()
    xbr = models.IntegerField()
    ybr = models.IntegerField()
    frame = models.IntegerField()
    occluded = models.BooleanField(default=False)
    outside = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def getbox(self):
        return vision.Box(self.xtl, self.ytl, self.xbr, self.ybr,
                          self.frame, self.outside, self.occluded, 0)


class VATICBoxAttribute(models.Model):
    box = models.ForeignKey(VATICBox, related_name='boxes2attributes', on_delete=models.CASCADE)
    attribute = models.ForeignKey(VATICBox, related_name='attributes2boxes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class VATICTrainingOf(models.Model):
    video_test = models.ForeignKey(VATICVideo, on_delete=models.CASCADE, related_name='testvideos')
    video_train = models.ForeignKey(VATICVideo, on_delete=models.CASCADE, related_name='trainvideos')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class VATICWorkerJob(models.Model):
    worker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='worker2jobs')
    job = models.ForeignKey(VATICJob, on_delete=models.CASCADE, related_name='job2workers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class VATICBid(models.Model):
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    job = models.ForeignKey(VATICJob, on_delete=models.CASCADE, related_name='bids')
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approved_bids', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


BAN_REASONS = (
    (1, _("Downloaded")),
    (2, _("Irrelevant")),
    (3, _("Bad quality")),
    (4, _("Duplicated or not novel"))
)


class BannedVideo(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=False, related_name='bans')
    why = models.IntegerField(choices=BAN_REASONS, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# TODO: think about bonuses


class BlockedChannel(models.Model):
    channelId = models.CharField(max_length=255, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(BlockedChannel, self).save(force_insert, force_update, using, update_fields)
        # Block all videos from this channel
        videos = Video.objects.filter(channelId=self.channelId)
        for video in videos:
            try:
                new_blocked_video = BannedVideo()
                new_blocked_video.video = video
                new_blocked_video.why = 2
                new_blocked_video.save()
            except:
                pass



