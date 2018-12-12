from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View

from pyano2.models import *

import json


class VATICIndexView(View):
    template_name = 'vatic/vatic.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(to="{}?next=/vatic".format(settings.LOGIN_URL))
        # Check if user is assigned to this job or not
        context = {}
        id = request.GET.get('id')
        if not id:
            logging.debug('No id is provided. Just go to the index page.')
        else:
            wjobs = request.user.worker2jobs.all()
            assigned = False
            for wjob in wjobs:
                if wjob.job.id == int(id):
                    assigned = True
            if not assigned:
                logging.debug('This user is not assigned to this job. Just go to the index page.')
                return redirect(to="/vatic/list")
        return render(request, template_name=self.template_name, context=context)

class VATICListView(View):
    template_name = 'vatic/list.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(to="{}?next=/vatic/list".format(settings.LOGIN_URL))
        jobs = VATICJob.objects.all()
        return render(request, template_name=self.template_name, context={'jobs': jobs})


class VATICJobView(View):  # equal to getjob in VATIC
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'No permission.'})
        id = request.GET.get('id')
        verified = request.GET.get('verified')
        logging.info('id: {}'.format(id))
        jobs = VATICJob.objects.filter(id=id)
        if len(jobs) > 0:
            job = jobs[0]
            logging.debug("Found job {0}".format(job.id))

            v = job.segment.video
            train_of = VATICTrainingOf.objects.filter(video_test=v)
            if int(verified) and len(train_of) > 0:
                # swap segment with the training segment
                training = True
                segment = train_of[0].segments[0]
                logging.debug("Swapping actual segment with training segment")
            else:
                training = False
                segment = job.segment

            video = segment.video
            labels = dict((l.id, l.text) for l in video.labels.all())

            attributes = {}
            for label in video.labels.all():
                attributes[label.id] = dict((a.id, a.text) for a in label.attributes.all())

            logging.debug("Giving user frames {0} to {1} of {2}".format(video.slug,
                                                                        segment.start,
                                                                        segment.stop))

            result = {"start": segment.start,
                      "stop": segment.stop,
                      "slug": video.slug,
                      "width": video.width,
                      "height": video.height,
                      "skip": video.skip,
                      "perobject": video.perobjectbonus,
                      "completion": video.completionbonus,
                      "blowradius": video.blowradius,
                      "jobid": job.id,
                      "training": int(training),
                      "labels": labels,
                      "attributes": attributes}
            return JsonResponse(result)
        return JsonResponse({'error': 'No job found.', 'request': request.GET})


class VATICBoxesForJobView(View):  # getboxesforjob
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'No permission.'})
        id = request.GET.get('id')
        jobs = VATICJob.objects.filter(id=id)
        result = []
        if len(jobs) > 0:
            job = jobs[0]
            for path in job.paths.all():
                attrs = [(x.attribute.id, x.frame, x.value) for x in path.attributes.all()]
                result.append({"label": path.label.id,
                               "boxes": [tuple(x) for x in path.getboxes()],
                               "attributes": attrs})
        return JsonResponse({'result': result})


class VATICSaveJobView(View):  # savejob
    def readpaths(self, job, tracks):
        logging.debug("Reading {0} total tracks".format(len(tracks)))
        for track in tracks:
            if len(track) < 3: continue
            label, track, attributes = track[0], track[1], track[2]
            path = VATICPath()
            path.job = job
            labels = VATICLabel.objects.filter(id=label)
            if len(labels) > 0:
                path.label = labels[0]
                path.save()
            else:
                logging.error("No such label with ID {0}".format(label))
                continue

            logging.debug("Received a {0} track".format(path.label.text))

            visible = False
            for frame, userbox in track.items():
                box = VATICBox()
                box.path = path
                box.xtl = max(int(userbox[0]), 0)
                box.ytl = max(int(userbox[1]), 0)
                box.xbr = max(int(userbox[2]), 0)
                box.ybr = max(int(userbox[3]), 0)
                box.occluded = int(userbox[4])
                box.outside = int(userbox[5])
                box.frame = int(frame)
                if not box.outside:
                    visible = True

                logging.debug("Received box {0}".format(str(box.getbox())))
                box.save()

            if not visible:
                logging.warning("Received empty path! Skipping")
                continue

            for attributeid, timeline in attributes.items():
                attribute = VATICAttribute.objects.filter(id=attributeid)
                for frame, value in timeline.items():
                    aa = AttributeAnnotation()
                    aa.attribute = attribute
                    aa.frame = frame
                    aa.value = value
                    aa.path = path
                    aa.save()
                    path.save()

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'No permission.'})
        id = request.POST.get('id')
        tracks = json.loads(request.POST.get('tracks'))
        jobs = VATICJob.objects.filter(id=id)
        if len(jobs) > 0:
            job = jobs[0]
            for path in job.paths.all():
                path.delete()
            self.readpaths(job, tracks)
            job.save()
        return JsonResponse({})


class VATICValidateJobView(View):  # validatejob: to validate whether if annotator did a training job good or not?
    def readpaths(self, tracks):
        paths = []
        logging.debug("Reading {0} total tracks".format(len(tracks)))
        for track in tracks:
            if len(track) < 3: continue
            label, track, attributes = track[0], track[1], track[2]
            path = VATICPath()
            labels = VATICLabel.objects.filter(id=label)
            if len(labels) > 0:
                path.label = labels[0]
            else:
                logging.error("No such label with ID {0}".format(label))
                continue

            logging.debug("Received a {0} track".format(path.label.text))

            visible = False
            for frame, userbox in track.items():
                box = VATICBox()
                box.path = path
                box.xtl = max(int(userbox[0]), 0)
                box.ytl = max(int(userbox[1]), 0)
                box.xbr = max(int(userbox[2]), 0)
                box.ybr = max(int(userbox[3]), 0)
                box.occluded = int(userbox[4])
                box.outside = int(userbox[5])
                box.frame = int(frame)
                if not box.outside:
                    visible = True

                logging.debug("Received box {0}".format(str(box.getbox())))

            if not visible:
                logging.warning("Received empty path! Skipping")
                continue

            for attributeid, timeline in attributes.items():
                attribute = VATICAttribute.objects.filter(id=attributeid)
                for frame, value in timeline.items():
                    aa = AttributeAnnotation()
                    aa.attribute = attribute
                    aa.frame = frame
                    aa.value = value
                    aa.path = path
            paths.append(path)
        return paths

    def post(self, request, *args, **kwargs):
        id = request.POST.get('id')
        tracks = json.loads(request.POST.get('tracks'))
        paths = self.readpaths(tracks)
        jobs = VATICJob.objects.filter(id=id)
        matched = False
        if len(jobs) > 0:
            job = jobs[0]
            matched = job.validator(paths, job.paths)
        return JsonResponse({'status': matched})
