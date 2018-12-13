from vision import ffmpeg
import os
import logging
import shutil
import uuid
from time import time
from PIL import Image
import math

import django
django.setup()
from pyano2.models import *

LOG_FILE = "./log/video_{}.log".format(time())
if not os.path.exists("./log"):
    os.makedirs("./log")
formatter = logging.Formatter(fmt="[%(asctime)s]\t[%(levelname)s]\t[%(message)s]")
logger = logging.getLogger("video")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(fmt=formatter)
logger.addHandler(hdlr=file_handler)


class VATICExtractor(object):
    def __init__(self, video_path, output_path,
                 width=720, height=480,
                 no_resize=False, no_cleanup=False):
        self.video_path = video_path
        self.output_path = output_path
        self.width = width
        self.height = height
        self.no_resize = no_resize
        self.no_cleanup = no_cleanup

    def __call__(self, *args, **kwargs):
        try:
            os.makedirs(self.output_path)
        except:
            pass
        sequence = ffmpeg.extract(path=self.video_path)
        try:
            for frame, image in enumerate(sequence):
                if frame % 100 == 0:
                    logger.debug ("Decoding frames {0} to {1}"
                        .format(frame, frame + 100))
                if not self.no_resize:
                    image.thumbnail((self.width, self.height), Image.BILINEAR)
                path = VATICVideo.getframepath(int(frame), self.output_path)
                try:
                    image.save(path)
                except IOError:
                    os.makedirs(os.path.dirname(path))
                    image.save(path)
        except:
            if not self.no_cleanup:
                logger.error("Aborted. Cleaning up...")
                shutil.rmtree(self.output_path)
            raise


def test_extract(video_id='fs-ifFsc8Bg', output_dir='./static/frames'):
    extractor = VATICExtractor(video_path='./static/videos/{}.mp4'.format(video_id),
                               output_path=os.path.join(output_dir, '{}'.format(video_id)))
    extractor()


class VATICLoader(object):
    def __init__(self, location, labels, pyano_video_id,
                 length=300, overlap=20, skip=0, per_object_bonus=0, completion_bonus=0,
                 use_frames=None, start_frame=0, stop_frame=0, trainwith_id=None, for_training=False,
                 for_training_stop=0, for_training_start=0, for_training_overlap=0.25,
                 for_training_tolerance=0.2, for_training_mistakes=0, for_training_data=None, blow_radius=3):
        self.slug = uuid.uuid4()
        self.location = location
        self.labels = labels
        self.pyano_video_id = pyano_video_id
        self.overlap = overlap
        self.per_object_bonus = per_object_bonus
        self.completion_bonus = completion_bonus
        self.use_frames = use_frames
        self.start_frame = start_frame
        self.stop_frame = stop_frame
        self.trainwith_id = trainwith_id
        self.for_training = for_training
        self.for_training_start = for_training_start
        self.for_training_stop = for_training_stop
        self.for_training_overlap = for_training_overlap
        self.for_training_tolerance = for_training_tolerance
        self.for_training_mistakes = for_training_mistakes
        self.for_training_data = for_training_data
        self.blow_radius = blow_radius
        self.length = length
        self.skip = skip

    def title(self):
        return "Video annotation"

    def description(self):
        return "Draw boxes around objects moving around in a video."

    def cost(self):
        return 0.05

    def duration(self):
        return 7200 * 3

    def keywords(self):
        return "video, annotation, computer, vision"

    def __call__(self, group):
        logger.debug("Checking integrity...")
        # read first frame to get sizes
        path = VATICVideo.getframepath(0, self.location)
        try:
            im = Image.open(path)
        except IOError:
            logger.error("Cannot read {0}".format(path))
            return
        width, height = im.size

        logger.debug("Searching for last frame...")

        # search for last frame
        toplevel = max(int(x)
                       for x in os.listdir(self.location))
        secondlevel = max(int(x)
                          for x in os.listdir("{0}/{1}".format(self.location, toplevel)))
        maxframes = max(int(os.path.splitext(x)[0])
                        for x in os.listdir("{0}/{1}/{2}"
                                            .format(self.location, toplevel, secondlevel))) + 1

        logger.debug("Found {0} frames.".format(maxframes))

        # can we read the last frame?
        path = VATICVideo.getframepath(maxframes - 1, self.location)
        try:
            im = Image.open(path)
        except IOError:
            logger.error("Cannot read {0}".format(path))
            return

        # check last frame sizes
        if im.size[0] != width and im.size[1] != height:
            logger.debug("First frame dimensions differs from last frame")
            return

        if VATICVideo.objects.filter(slug=self.slug).count() > 0:
            logger.error("Video {0} already exists!".format(self.slug))
            return

        if self.trainwith_id:
            if self.for_training:
                logger.error("A training video cannot require training")
                return
            logger.debug("Looking for training video...")
            trainers = Video.objects.filter(id=self.trainwith_id)
            if trainers.count() == 0:
                logger.debug("Training video does not exist.")
                trainer = None
            else:
                trainer = trainers[0]
        else:
            trainer = None

        # Find the corresponding pyano video
        pv = Video.objects.filter(id=self.pyano_video_id)
        if pv.count() == 0:
            logger.error("Corresponding PYANO video is not found!")
            return
        p = pv[0]

        # create video
        video = VATICVideo()
        video.slug=self.slug
        video.location=os.path.abspath(self.location)
        video.width=width
        video.height=height
        video.totalframes=maxframes
        video.skip=self.skip
        video.perobjectbonus=self.per_object_bonus
        video.completionbonus=self.completion_bonus
        video.isfortraining=self.for_training
        video.blowradius=self.blow_radius
        video.pyano_video = p
        video.save() # save to database

        logger.debug("Assigning trainer ...")
        if trainer:
            train_of = VATICTrainingOf()
            train_of.video_train = trainer
            train_of.video_test = video
            train_of.save()

        logger.debug("Binding labels and attributes...")

        # create labels and attributes
        labelcache = {}
        attributecache = {}
        lastlabel = None
        for labeltext in self.labels:
            if labeltext[0] == "~":
                if lastlabel is None:
                    logger.error("Cannot assign an attribute without a label!")
                    return
                labeltext = labeltext[1:]
                attribute = VATICAttribute()
                attribute.text = labeltext
                attribute.label = lastlabel
                attribute.save()
                attributecache[labeltext] = attribute
            else:
                label = VATICLabel()
                label.text = labeltext
                label.video = video
                label.save()
                labelcache[labeltext] = label
                lastlabel = label

        logger.debug("Creating symbolic link...")
        symlink = os.path.abspath("./static/frames/{0}".format(video.slug))
        try:
            os.remove(symlink)
        except:
            pass
        os.symlink(video.location, symlink)

        logger.debug("Creating segments...")
        # create shots and jobs
        if self.for_training:
            segment = VATICSegment()
            segment.video = video
            if self.for_training_start:
                segment.start = self.for_training_start
                if segment.start < 0:
                    segment.start = 0
            else:
                segment.start = 0
            if self.for_training_stop:
                segment.stop = self.for_training_stop
                if segment.stop > video.totalframes - 1:
                    segment.stop = video.totalframes - 1
            else:
                segment.stop = video.totalframes - 1
            segment.save()
            job = VATICJob()
            job.segment = segment
            job.group = group
            job.ready = False
            job.save()
        elif self.use_frames:
            with open(self.use_frames) as useframes:
                for line in useframes:
                    ustart, ustop = line.split()
                    ustart, ustop = int(ustart), int(ustop)
                    validlength = float(ustop - ustart)
                    numsegments = math.ceil(validlength / self.length)
                    segmentlength = math.ceil(validlength / numsegments)

                    for start in range(ustart, ustop, int(segmentlength)):
                        stop = min(start + segmentlength + self.overlap + 1, ustop)
                        segment = VATICSegment()
                        segment.start = start
                        segment.stop = stop
                        segment.video = video
                        segment.save()
                        job = VATICJob()
                        job.segment = segment
                        job.group = group
                        job.save()
        else:
            startframe = self.start_frame
            stopframe = self.stop_frame
            if not stopframe:
                stopframe = video.totalframes - 1
            for start in range(startframe, stopframe, self.length):
                stop = min(start + self.length + self.overlap + 1, stopframe)
                segment = VATICSegment()
                segment.start = start
                segment.stop = stop
                segment.video = video
                segment.save()
                job = VATICJob()
                job.segment = segment
                job.group = group
                job.uuid = uuid.uuid4()
                job.save()

        # Handling bonuses
        bonus = 0
        if self.per_object_bonus:
            bonus += self.per_object_bonus
        if self.completion_bonus:
            bonus += self.completion_bonus
        job.bonus = bonus
        job.save()

        if self.for_training and self.for_training_data:
            logger.debug("Loading training ground truth annotations from {0}"
                  .format(self.for_training_data))
            with open(self.for_training_data, "r") as file:
                pathcache = {}
                for line in file:
                    (id, xtl, ytl, xbr, ybr,
                     frame, outside, occluded, generated,
                     label) = line.split(" ")

                    if int(generated):
                        continue

                    if id not in pathcache:
                        logger.debug("Imported new path {0}".format(id))
                        label = labelcache[label.strip()[1:-1]]
                        pl= VATICPath()
                        pl.job = job
                        pl.label = label
                        pathcache[id] = pl

                    box = VATICBox()
                    box.path = pathcache[id]
                    box.xtl = int(xtl)
                    box.ytl = int(ytl)
                    box.xbr = int(xbr)
                    box.ybr = int(ybr)
                    box.frame = int(frame)
                    box.outside = int(outside)
                    box.occluded = int(occluded)
                    box.save()

        if self.for_training:
            if self.for_training and self.for_training_data:
                logger.debug("Video and ground truth loaded.")
            else:
                logger.debug("Video loaded and ready for ground truth")
        else:
            logger.debug("Video loaded and ready for publication.")


def test_load():
    loader = VATICLoader(location=os.path.abspath('./static/frames/fs-ifFsc8Bg/'),
                         labels=['face', 'body', 'left_hand', 'right_hand'],
                         pyano_video_id=1)
    groups = VATICJobGroup.objects.all()
    if groups.count() == 0:
        group = VATICJobGroup()
        group.title = "A test group for STA job"
        group.duration = 100000
        credit = Credit()
        credit.point = 15.0
        credit.survey = None
        credit.save()
        group.cost = credit
        group.save()
    else:
        group = groups[0]
    loader(group=group)

if __name__ == '__main__':
    # test_extract()
    test_load()