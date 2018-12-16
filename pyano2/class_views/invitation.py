from django.shortcuts import render, redirect
from django.utils.timezone import now, timedelta
import datetime
import uuid
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Count

from pyano2.forms import InviteReviewerAnnotatorForm
from pyano2.models import Invitation, Alternative
from survey.models import Survey, Video
from django.contrib.auth.models import User
from pyano.settings import SHOPLIFT_DOMAIN


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
                msg = form.cleaned_data.get('message')
                self.email(job_name, full_name, user, recipient_list, invitation.uuid, survey_id, msg)
                invitation.message = msg
                invitation.save()
            except Exception as e:
                return render(request, template_name=self.template_name, context={"form": form, "error": e})
            return redirect('/')
        return render(request, template_name=self.template_name, context={"form": form})

    def email(self, job_name, full_name, user, recipient_list, uuid, survey_id, msg):
        subject = '{} invitation for Shoplifting prevention project'.format(job_name)
        default_msg = 'Dear Dr. {},\n\n' \
                  'I am {} {} from Shoplifting prevention project. ' \
                  'We are looking for a leading expert for the position {} of our project. ' \
                  'After a thorough checking, we believe that you are the best person to fit this position in ' \
                  'our project. With this position, you have the responsibility to serve our large community of users, ' \
                  'who submits a massive amount of videos to help enhancement of shoplifting prevention systems.' \
                  'As an Annotator, you will have to annotate a number of videos following the instruction from Reviewer. ' \
                  'As a Reviewer, you will have to use your expertise to guide the annotator to learn how to annotate a video, then after the instruction, ' \
                  'annotators can annotate a large number of videos by themselves. ' \
                  'You need to register an account and login to see the contents in following URLs.\n\n' \
                  'For specific guidelines, please feel free to confirm the guideline at: http://{}:8000/survey/{} \n\n' \
                  'To Accept this invitation, please head to http://{}:8000/accept/?uuid={}. ' \
                  'If you do not have an account, the above link will guide you to create one. ' \
                  'If you are busy or having some reasons not to accept this job, please head to http://{}:8000/decline/?uuid={} to decline the job offer. ' \
                  'You will be asked for the reasons of decline and the names of alternatives. ' \
                  'We appreciate if you can recommend others to fulfill this position.\n\n' \
                  'Finally, thank you very much for spending time to look through this invitation. ' \
                  'Please response before {} if you want to accept this offer. ' \
                  'After {}, we will consider as your decline. ' \
                  'If you want to correct your responses or having any further questions, please contact me at {}.\n\n' \
                  'Thank you very much,\n' \
                  '{} {}'.format(full_name, user.first_name, user.last_name, job_name,
                                 SHOPLIFT_DOMAIN, survey_id, SHOPLIFT_DOMAIN, uuid, SHOPLIFT_DOMAIN, uuid,
                                 (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d'),
                                 (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d'),
                                 user.email, user.first_name, user.last_name)
        if len(msg) == 0:
            message = default_msg
        else:
            message = msg + '\n\n' + default_msg

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
            context = {'error': 'Cannot find this invitation in our database!', 'uuid': uuid}
            return render(request, template_name=self.template_name, context=context)
        if len(invitations) > 0:
            invitation = invitations[0]
            # Check if declined in the past?
            if invitation.done and invitation.status == 2:
                context = {'error': 'You declined this invitation in the past! '
                                    'Please contact your invitor if you changed your mind!', 'uuid': uuid}
                return render(request, template_name=self.template_name, context=context)
            if now() - invitation.created > timedelta(+7) and invitation.status != 1:
                context = {'error': 'The invitation has been expired! '
                                    'Please contact your invitor if you changed your mind!', 'uuid': uuid}
                invitation.done = False # expired but not done
                invitation.status = 3
                invitation.save()
                return render(request, template_name=self.template_name, context=context)
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
            prev_status = invitation.done
            invitation.done = True
            invitation.status = 1
            invitation.save()
            context = {"invitation": invitation, "n_videos": len(videos), "videos": videos,
                       "reviewers": reviewers, "annotators": annotators}
            # send email to invitor
            if not prev_status:
                try:
                    self.email_invitor(invitation)
                except Exception as e:
                    logging.error("Cannot send email to invitor with error: {}".format(e))
        else:
            context = {'error': 'No invitation found!'}
        context['request'] = request
        context['uuid'] = uuid
        return render(request, template_name=self.template_name, context=context)

    def email_invitor(self, invitation):
        if invitation.job == 1:
            job_name = 'Reviewer'
        else:
            job_name = 'Annotator'
        subject = '{} accepted your invitation for Shoplifting prevention project'.format(invitation.name)
        message = 'Dear Dr. {} {},\n\n' \
                  '{} accepted your invitation for position {} of Shoplifting prevention project. ' \
                  'The progresses can be seen in admin view. ' \
                  'The uuid of this job offer is {} and the job is {}. \n\n ' \
                  'Thank you very much,\n' \
                  'Shoplifting prevention project'.format(invitation.invitor.first_name, invitation.invitor.last_name,
                                                          invitation.name, job_name, invitation.uuid,
                                                          invitation.survey.get_absolute_url())
        email_from = settings.EMAIL_HOST_USER
        send_mail(subject, message, email_from, [invitation.invitor.email])


class DeclineInvitationView(View):
    template_name = 'pyano2/invite_decline.html'

    def get(self, request, *args, **kwargs):
        uuid = request.GET.get('uuid')
        try:
            invitations = Invitation.objects.filter(uuid=request.GET.get('uuid'))
        except Exception as e:
            context = {'error': 'Cannot find this invitation in our database!', 'uuid': uuid}
            return render(request, template_name=self.template_name, context=context)
        if len(invitations) > 0:
            for invitation in invitations:
                if request.user.is_authenticated and request.user != invitation.invited:
                    context = {'error': 'You are not invited for this job!', 'uuid': uuid}
                    return render(request, template_name=self.template_name, context=context)
                if invitation.done:
                    context = {'error': 'This invitation has been responded!', 'uuid': uuid}
                    return render(request, template_name=self.template_name, context=context)
                if now() - invitation.created > timedelta(+7):
                    invitation.status = 3
                    invitation.save()
                    context = {'error': 'The invitation has been expired! '
                                        'Please contact your invitor if you changed your mind!', 'uuid': uuid}
                    return render(request, template_name=self.template_name, context=context)
                invitation.done = True # change the state of all found invitations
                invitation.status = 2
                invitation.save()
        context = {'invitations': invitations}
        context['request'] = request
        context['uuid'] = uuid
        context['recommend_range'] = range(3)
        return render(request, template_name=self.template_name, context=context)


class AlternativeRecommendationView(View):
    template_name = 'pyano2/invite_recommend.html'

    def post(self, request, *args, **kwargs):
        uuid = request.POST.get('uuid')
        alternative_info = []
        for i in range(3):
            alternative_info.append({
                'name': request.POST.get('fullname_{}'.format(i)),
                'email': request.POST.get('email_{}'.format(i))
            })
        try:
            invitations = Invitation.objects.filter(uuid=uuid)
        except Exception as e:
            context = {'error': 'Cannot find this invitation in our database!', 'uuid': uuid}
            return render(request, template_name=self.template_name, context=context)
        if len(invitations) > 0:
            for invitation in invitations:
                if request.user.is_authenticated and request.user != invitation.invited:
                    context = {'error': 'You are not invited for this job!', 'uuid': uuid}
                    return render(request, template_name=self.template_name, context=context)
                if invitation.done and invitation.status == 1:
                    context = {'error': 'This invitation has been responded and you accepted it!', 'uuid': uuid}
                    return render(request, template_name=self.template_name, context=context)
                if now() - invitation.created > timedelta(+7):
                    context = {'error': 'The invitation has been expired! '
                                        'Please contact your invitor if you changed your mind!', 'uuid': uuid}
                    return render(request, template_name=self.template_name, context=context)
                # add recommended alternatives
                for info in alternative_info:
                    if info['name'] == "" or info['email'] == "" or not '@' in info['email']:
                        continue
                    a = Alternative()
                    a.name = info['name']
                    a.email = info['email']
                    a.invitation = invitation
                    a.save()
                alternatives = Alternative.objects.filter(invitation=invitation)
                # send email to invitor
                try:
                    self.email_invitor(invitation, alternatives)
                except Exception as e:
                    logging.error("Cannot send email to invitor with error: {}".format(e))
        context = {'invitations': invitations}
        context['request'] = request
        context['uuid'] = uuid
        context['recommend_range'] = range(3)
        return render(request, template_name=self.template_name, context=context)

    def email_invitor(self, invitation, alternatives):
        if invitation.job == 1:
            job_name = 'Reviewer'
        else:
            job_name = 'Annotator'
        subject = '{} declined your invitation for Shoplifting prevention project'.format(invitation.name)
        message = 'Dear Dr. {} {},\n\n' \
                  '{} declined your invitation for position {} of Shoplifting prevention project. ' \
                  'The uuid of this job offer is {} and the job is {}. ' \
                  '{} also suggested {} alternatives as bewllow:\n\n'.format(invitation.invitor.first_name, invitation.invitor.last_name,
                                                          invitation.name, job_name, invitation.uuid,
                                                          invitation.survey.get_absolute_url(), invitation.name, len(alternatives))
        for i, alternative in enumerate(alternatives):
            if alternative.invitation != invitation:
                continue
            message += 'Alternative {}:\n' \
                       '  Name: {}\n' \
                       '  Email: {}\n\n'.format(i, alternative.name, alternative.email)
        message += 'Thank you very much,\n' \
                  'Shoplifting prevention project'
        email_from = settings.EMAIL_HOST_USER
        send_mail(subject, message, email_from, [invitation.invitor.email])


