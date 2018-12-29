from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.core.mail import send_mail
from django.db.models import Count
from django.db.models import Q

from pyano2.models import *
from pyano2.downloader.youtube import download_youtube_video
from pyano2.downloader.video import *
from pyano import settings as pyano_settings
import json
from glob import glob


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
        # else:
        #     wjobs = request.user.worker2jobs.all()
        #     assigned = False
        #     for wjob in wjobs:
        #         if wjob.job.id == int(id):
        #             assigned = True
        #     if not assigned and not request.user.is_staff:
        #         logging.debug('This user is not assigned to this job and this user is not admin. Just go to the index page.')
        #         return redirect(to="/vatic/list")
        return render(request, template_name=self.template_name, context=context)


class VATICListView(View):
    template_name = 'vatic/list.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(to="{}?next=/vatic/list".format(settings.LOGIN_URL))
        jobs = VATICJob.objects.filter(completed=False).all()
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
            assignments = VATICWorkerJob.objects.filter(worker=request.user, job=job)
            if assignments.count() < 1:
                return JsonResponse({'error': 'User is not assigned for this job.'})
            if job.completed:
                return JsonResponse({'error': 'Job is completed. You cannot submit after a job is finalized.'})
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


class VATICBidJobView(View):
    template_name = 'vatic/bid.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(to="{}?next=/vatic/bid?id={}".format(settings.LOGIN_URL, request.GET.get('id')))
        context = {}
        try:
            id = request.GET.get('id')
            wjobs = request.user.worker2jobs.all()
            assigned = False
            for wjob in wjobs:
                if wjob.job.id == int(id):
                    assigned = True
            bids = VATICBid.objects.filter(job_id=id, candidate=request.user)
            if bids.count() > 0:
                if not assigned:
                    if not request.user.is_staff:
                        context['error'] = 'You already bid this job. Probably admins are still reviewing your application.'
            elif not assigned:
                job = VATICJob.objects.filter(id=id)[0]
                num_workers = job.job2workers.count()
                if num_workers > 0:
                    context['error'] = 'This position is filled.'
                elif job.completed:
                    context['error'] = 'This job is completed. You cannot bid.'
                else:
                    bid = VATICBid()
                    bid.candidate = request.user
                    bid.job = job
                    bid.approved = False
                    bid.approved_by = None
                    bid.save()
        except Exception as e:
            context['error'] = 'Internal Server Error: {}'.format(e)
        context['assigned'] = assigned
        return render(request, template_name=self.template_name, context=context)


class VATICListJobApplicationView(View):
    template_name = 'vatic/job_applications.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(to="{}?next=/vatic/job_applications/".format(settings.LOGIN_URL))
        if not request.user.is_staff:
            return redirect(to="/")
        context = {}
        try:
            bids = VATICBid.objects.filter(approved=False)
            context['bids'] = bids
        except Exception as e:
            context['error'] = 'Internal Server Error: {}'.format(e)
        return render(request, template_name=self.template_name, context=context)


class VATICApproveBidView(View):
    template_name = 'vatic/approve_bid.html'

    def email(self, bid, sender):
        subject = 'Your bid for job ID {} in Shoplifting prevention project is approved'.format(bid.job.id)
        message = 'Dear {},\n\n' \
                  'I am {} {} from Shoplifting prevention project. ' \
                  'Our admins have approved your bid for the job /vatic?id={}. ' \
                  'You can start to work by following this URL: http://13.58.121.50:8000/vatic/?id={} . \n\n' \
                  'Thank you very much,\n' \
                  '{} {}'.format(bid.candidate.username, sender.first_name, sender.last_name,
                                 bid.job.id, bid.job.id,
                                 sender.first_name, sender.last_name)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [bid.candidate.email]
        send_mail(subject, message, email_from, recipient_list)
        return redirect('/')

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(to="{}?next=/vatic/approve_bid/?id=".format(settings.LOGIN_URL, request.GET.get('id')))
        if not request.user.is_staff:
            return redirect(to="/")
        context = {}
        try:
            bids = VATICBid.objects.filter(id=request.GET.get('id'))
            for bid in bids.all():
                if bid.approved: continue
                assignments = VATICWorkerJob.objects.filter(worker=bid.candidate, job=bid.job)
                if len(assignments) > 0 or bid.job.completed:
                    context['error'] = 'This job has been assigned to another user or is already completed. ' \
                                       'This bid cannot be approved!'
                else:
                    bid.approved = True
                    bid.approved_by = request.user
                    assignment = VATICWorkerJob()
                    assignment.worker = bid.candidate
                    assignment.job = bid.job
                    bid.save()
                    assignment.save()
                    self.email(bid, request.user) # send email to the candidate
                    # remove other applications for the same job
                    other_bids = VATICBid.objects.filter(job=bid.job)
                    for o in other_bids.all():
                        if o.candidate != bid.candidate:
                            o.delete()
            if bids.count() == 0:
                context['error'] = 'No bid found.'
            else:
                context['bid'] = bids[0]
        except Exception as e:
            context['error'] = 'Internal Server Error: {}'.format(e)
        return render(request, template_name=self.template_name, context=context)


class VATICFinalizeJobView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(to="{}?next=/vatic/finalize/".format(settings.LOGIN_URL))
        if not request.user.is_staff:
            return redirect(to="/")
        context = {}
        id = request.GET.get('id')
        try:
            jobs = VATICJob.objects.filter(id=id)
            for job in jobs.all():
                if job.completed: continue
                job.completed = True
                job.save()
                break
        except Exception as e:
            logging.error('Internal Server Error: {}'.format(e))
        return redirect(to="/vatic/list")


class VATICCrawlerView(View):
    template_name = 'vatic/crawler.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(to="{}?next=/vatic/crawler/".format(settings.LOGIN_URL))
        if not request.user.is_staff:
            return redirect(to="/")
        context = {}
        try:
            gid = request.GET.get('gid')
            context['gid'] = gid
            groups = VATICJobGroup.objects.filter(id=gid)
            if len(groups) > 0:
                group = groups[0]
                context['group'] = group
                videos = Video.objects.annotate(num_responses=Count('responses'))
                videos = videos.filter(num_responses__gt=0)
                videos = videos.annotate(num_locks=Count('bans'))
                videos = videos.filter(num_locks=0)
                context['videos'] = videos
            else:
                context['error'] = 'No group found.'
        except Exception as e:
            context['error'] = 'Internal Server Error: {}'.format(e)
        return render(request, template_name=self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': 404, 'error': 'No user'})
        if not request.user.is_staff:
            return JsonResponse({'status': 404, 'error': 'No staff'})
        try:
            id = request.POST.get('id')
            vid = request.POST.get('vid')
            gid = request.POST.get('gid')
            groups = VATICJobGroup.objects.filter(id=gid)
            if len(groups) == 0:
                return JsonResponse({'status': 404, 'error': 'No group'})
            else:
                group = groups[0]
            videos = Video.objects.filter(id=id)
            # Check if the video is locked or not
            if len(videos) > 0:
                locks = BannedVideo.objects.filter(video=videos[0])
                if len(locks) > 0:
                    return JsonResponse({'status': 404, 'error': 'Locked videos'})
            else:
                return JsonResponse({'status': 404, 'error': 'No video found'})
            download_youtube_video(youtube_ids=[vid],
                                   output_folder=os.path.join(pyano_settings.BASE_DIR, 'static/videos'))

            files = glob(os.path.join(pyano_settings.BASE_DIR, 'static/videos/{}'.format(request.POST.get('vid'))) + '.*')
            if len(files) > 0:
                f = files[0]
                output_path = os.path.join(pyano_settings.BASE_DIR, 'static/frames/{}'.format(request.POST.get('vid')))
                extractor = VATICExtractor(video_path=f, output_path=output_path)
                extractor()
                labels = request.POST.get('labels').split(',')
                print(labels)
                loader = VATICLoader(location=output_path,
                                     labels=labels,
                                     pyano_video_id=id)
                loader(group)
            # After having all of this process done, we should lock the video to prevent downloading again.
            if len(videos) > 0:
                lock = BannedVideo()
                lock.video = videos[0]
                lock.why = 1
                lock.save()
        except Exception as e:
            return JsonResponse({'status': 404, 'error': e})
        return JsonResponse({'status': 200})


class VideoAnswerView(View):
    def post(self, request, vid, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': 404, 'error': 'No user'})
        if not request.user.is_staff:
            return JsonResponse({'status': 404, 'error': 'No staff'})
        answers = {}
        try:
            videos = Video.objects.filter(id=vid)
            if len(videos) > 0:
                video = videos[0]
                responses = video.responses.all()
                for i, response in enumerate(responses):
                    answers[i] = {'uname': '', 'questions': []}
                    if not response.user:
                        answers[i]['uname'] = 'Unknown'
                    else:
                        answers[i]['uname'] = response.user.username
                    ans = response.answers.all()
                    for an in ans:
                        q = an.question.text
                        a = an.body
                        answers[i]['questions'].append({'question': q, 'answer': a})
        except Exception as e:
            return JsonResponse({'status': 404, 'error': e})
        return JsonResponse({'status': 200, 'answers': answers})


class VATICAssignWorker(View):
    template_name = 'vatic/assignment.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(to="{}?next=/vatic/list".format(settings.LOGIN_URL))
        if not request.user.is_staff:
            return redirect(to="/")
        jobs = VATICJob.objects.filter(completed=False).all()
        users = User.objects.filter(~Q(email=''))
        return render(request, template_name=self.template_name, context={'jobs': jobs, 'users': users})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(to="/")
        jobs = VATICJob.objects.filter(completed=False).all()
        uid = request.POST.get('uid', None)
        print(uid)
        if uid is not None:
            users = User.objects.filter(id=uid)
            if users.count() > 0:
                user = users[0]
                for job in jobs:
                    assign = VATICWorkerJob()
                    assign.worker = user
                    assign.job = job
                    assign.save()
                user.email_user(subject='You have job offers!',
                                message="Admins have assigned some important jobs to you. Congratulation! "
                                        "You can login and visit http://13.58.121.50:8000/vatic/list/ to see the list of jobs you have been offered. ")
        return redirect(to="/")


