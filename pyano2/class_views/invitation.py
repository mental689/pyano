from django.shortcuts import render, redirect
import datetime
import uuid
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Count

from pyano2.forms import InviteReviewerAnnotatorForm
from pyano2.models import Invitation
from survey.models import Survey, Video, Response
from django.contrib.auth.models import User


class InvitationView(View):
    template_name = 'pyano2/invite.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(to="{}?next=/invite".format(settings.LOGIN_URL))
        form = InviteReviewerAnnotatorForm()
        return render(request, template_name=self.template_name, context={"form": form})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(to="{}?next=/invite".format(settings.LOGIN_URL))
        form = InviteReviewerAnnotatorForm(request.POST)
        if form.is_valid():
            job = int(form.cleaned_data.get('job'))
            if job == 1:
                job_name = 'Reviewer'
            else:
                job_name = 'Annotator'
            full_name = form.cleaned_data.get('name')
            user = request.user
            recipient_list = [form.cleaned_data.get('email')]
            invitation = Invitation()
            invitation.email = form.cleaned_data.get('email')
            survey_id = form.cleaned_data.get('survey')
            surveys = Survey.objects.filter(id=survey_id)
            if len(surveys) > 0:
                invitation.survey = surveys[0]
            invitation.job = job
            invitation.name = full_name
            invitation.uuid = uuid.uuid4().hex
            invitation.invitor = user
            # search if invited target is already on the system
            candidates = User.objects.filter(email=invitation.email)
            if len(candidates) > 0:
                invitation.invited = candidates[0]
            else:
                invitation.invited = None # If no record found, just put NULL into this field.
            invitation.save()
            try:
                self.email(job_name, full_name, user, recipient_list, invitation.uuid, survey_id)
            except Exception as e:
                return render(request, template_name=self.template_name, context={"form": form, "error": e})
            return redirect('/')
        return render(request, template_name=self.template_name, context={"form": form})

    def email(self, job_name, full_name, user, recipient_list, uuid, survey_id):
        subject = '{} invitation for Shoplifting prevention project'.format(job_name)
        message = 'Dear Dr. {},\n\n' \
                  'I am {} {} from Shoplifting prevention project. ' \
                  'We are looking for a leading expert for the position {} of our project. ' \
                  'After a thorough checking, we believe that you are the best person to fit this position in ' \
                  'our project. With this position, you have the responsibility to serve our large community of users, ' \
                  'who submits a massive amount of videos to help enhancement of shoplifting prevention systems.' \
                  'As an Annotator, you will have to annotate a number of videos following the instruction from Reviewer. ' \
                  'As a Reviewer, you will have to use your expertise to guide the annotator to learn how to annotate a video, then after the instruction, ' \
                  'annotators can annotate a large number of videos by themselves. \n\n' \
                  'For specific guidelines, please feel free to confirm the guideline at: http://13.58.121.50:8000/surveys/{} \n\n' \
                  'To Accept this invitation, please head to http://13.58.121.50:8000/accept/?uuid={}. ' \
                  'If you do not have an account, the above link will guide you to create one. ' \
                  'If you are busy or having some reasons not to accept this job, please head to http://13.58.121.50:8000/decline/?uuid={} to decline the job offer. ' \
                  'You will be asked for the reasons of decline and the names of alternatives. ' \
                  'We appreciate if you can recommend others to fulfill this position.\n\n' \
                  'Finally, thank you very much for spending time to look through this invitation. ' \
                  'Please response before {} if you want to accept this offer. ' \
                  'After {}, we will consider as your decline. ' \
                  'If you want to correct your responses or having any further questions, please contact me at {}.\n\n' \
                  'Thank you very much,\n' \
                  '{} {}'.format(full_name, user.first_name, user.last_name, job_name,
                                 survey_id, uuid, uuid,
                                 (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d'),
                                 (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d'),
                                 user.email, user.first_name, user.last_name)
        email_from = settings.EMAIL_HOST_USER
        send_mail(subject, message, email_from, recipient_list)
        return redirect('/')


class AcceptInvitationView(View):
    template_name = 'pyano2/invite_accept.html'

    def get(self, request, *args, **kwargs):
        logging.info(request.GET.get('uuid'))
        uuid = request.GET.get('uuid')
        try:
            invitations = Invitation.objects.filter(uuid=request.GET.get('uuid'))
        except Exception as e:
            context = {'error': e, 'uuid': uuid}
            return render(request, template_name=self.template_name, context=context)
        if len(invitations) > 0:
            invitation = invitations[0]
            # get the number of videos
            videos = Video.objects.filter(cat=invitation.survey.video_cat)
            videos = videos.annotate(num_responses=Count('responses'))
            # search if invited target is already on the system
            if invitation.invited is None:
                candidates = User.objects.filter(email=invitation.email)
                if len(candidates) > 0:
                    invitation.invited = candidates[0]
                    invitation.save()
            if request.user.is_authenticated and request.user != invitation.invited:
                context = {'error': 'You are not invited for this job!', 'uuid': uuid}
                return render(request, template_name=self.template_name, context=context)
            # Find other invited reviewers and annotators
            reviewers = Invitation.objects.filter(survey=invitation.survey, job=1)
            annotators = Invitation.objects.filter(survey=invitation.survey, job=2)
            context = {"invitation": invitation, "n_videos": len(videos), "videos": videos,
                       "reviewers": reviewers, "annotators": annotators}
        else:
            context = {'error': 'No invitation found!'}
        context['request'] = request
        context['uuid'] = uuid
        return render(request, template_name=self.template_name, context=context)

