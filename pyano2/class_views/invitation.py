from django.shortcuts import render, redirect
import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views import View

from pyano2.forms import InviteReviewerAnnotatorForm
from pyano2.models import Invitation


class InvitationView(View):
    template_name = 'pyano2/invite.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(to="{}?next=/invite".format(settings.LOGIN_URL))
        form = InviteReviewerAnnotatorForm()
        return render(request, template_name=self.template_name, context={"form": form})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/')
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
            invitation.job = job
            invitation.name = full_name
            invitation.save()
            try:
                self.email(job_name, full_name, user, recipient_list)
            except Exception as e:
                return render(request, template_name=self.template_name, context={"form": form, "error": e})
            return redirect('/')
        return render(request, template_name=self.template_name, context={"form": form})

    def email(self, job_name, full_name, user, recipient_list):
        subject = '{} invitation for Shoplifting prevention project'.format(job_name)
        message = 'Dear Dr. {},\n\n ' \
                  'I am {} {} from Shoplifting prevention project. ' \
                  'We are looking for a leading expert for the position {} of our project. ' \
                  'After a through checking, we believe that you are the best person to fit this position in ' \
                  'our project. With this position, you have the responsibility to serve our large community of users,' \
                  'who submits a massive amount of videos to help enhancement of shoplifting prevention systems.' \
                  'As an Annotator, you will have to annotate a number of videos following the instruction from Reviewer. ' \
                  'As a Reviewer, you will have to use your expertise to guide the annotator to learn how to annotate a video, then after the instruction, ' \
                  'annotators can annotate a large number of videos by themselves. \n\n' \
                  'For specific guidelines, please feel free to confirm the guideline at: \n\n' \
                  'To Accept this invitation, please head to http://13.58.121.50:8000/accept/.' \
                  'If you do not have an account, the above link will guide you to create one. ' \
                  'If you are busy or having some reasons not to accept this job, please head to http://13.58.121.50:8000/decline/ to decline the job offer. ' \
                  'You will be asked for the reasons of decline and the names of alternatives. ' \
                  'We appreciate if you can recommend others to fulfill this position.\n\n' \
                  'Finally, thank you very much for spending time to look through this invitation. ' \
                  'Please response before {} if you want to accept this offer. ' \
                  'After {}, we will consider as your decline. ' \
                  'If you want to correct your responses or having any further questions, please contact me at {}.\n\n' \
                  'Thank you very much,' \
                  '{} {}'.format(full_name, user.first_name, user.last_name,
                                 job_name, datetime.datetime.today().strftime('%Y-%m-%d'),
                                 (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d'),
                                 user.email, user.first_name, user.last_name)
        email_from = settings.EMAIL_HOST_USER
        send_mail(subject, message, email_from, recipient_list)
        return redirect('/')