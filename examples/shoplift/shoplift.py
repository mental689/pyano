from django.utils.timezone import now, timedelta
import datetime
import uuid
import logging

from django.conf import settings
from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Count

from pyano2.models import *
from survey.models import *
from django.contrib.auth.models import User

SHOPLIFT_SRUVERY_ID=1

class ShopliftSummaryView(View):
    template_name = 'shoplift.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return render(request, template_name=self.template_name, context={'error': 'No permission.'})
        surveys = Survey.objects.filter(id=SHOPLIFT_SRUVERY_ID)
        if surveys.count() == 0:
            context = {'error': 'No survey found!'}
        else:
            survey = surveys[0]
            videos = Video.objects.filter(cat=survey.video_cat)\
                .annotate(num_responses=Count('responses'))\
                .annotate(num_bans=Count('bans'))\
                .filter(num_bans=0).filter(num_responses_gt=0)
            vids = []
            for v in videos:
                p = 0.
                res = v.responses
                for r in res.all():
                    ans = r.answers.all()
                    for a in ans:
                        a_ = a.body
                        q_ = a.question.text
                        if q_ == 'Did you find a shoplifting criminal in this video?':
                            if a_ == 'yes':
                                p += 1.
                            elif a_ == 'not-sure':
                                p += 0.5
                if p > 0: vids.append({'video': v, 'score': p})
            vids.sort(key=lambda k: -k['score'])
            context = {'survey': survey, 'videos': vids}
        return render(request, template_name=self.template_name, context=context)

