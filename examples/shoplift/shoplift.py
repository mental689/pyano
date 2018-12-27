from django.db.models import Count
from django.views import View
from django.shortcuts import render, redirect
from pyano2.models import *
from django.http import JsonResponse
from django.conf import settings

SHOPLIFT_SRUVERY_ID=1


class ShopliftSummaryView(View):
    """
    This example view will show an admin a selection view to choose
    the videos which contain at least one crime scene (Shoplifting)
    from a list of videos which have been answered by user.
    """
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
                .filter(num_bans=0).filter(num_responses__gt=0)
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


class QBESearchView(View):
    template_name = 'pyano2/qbe.html'

    def _get_dev_key(self):
        try:
            dev_keys = SystemSetting.objects.filter(name="youtube_dev_key")
            if len(dev_keys) == 0:
                logging.error("No Youtube API devkeys found!")
                return None
            return dev_keys[0].value
        except Exception as e:
            logging.error(e)
            return None

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(to="{}?next=/examples/shoplift/qbe/".format(settings.LOGIN_URL))
        if not request.user.is_staff:
            return redirect(to="/")
        context = {}
        try:
            surveys = Survey.objects.filter(id=SHOPLIFT_SRUVERY_ID)
            if surveys.count() == 0:
                context = {'error': 'No survey found!'}
            else:
                survey = surveys[0]
                videos = Video.objects.filter(cat=survey.video_cat) \
                    .annotate(num_responses=Count('responses')) \
                    .annotate(num_bans=Count('bans')) \
                    .filter(num_bans=0).filter(num_responses__gt=0)
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
                context['videos'] = [v['video'] for v in vids]
        except Exception as e:
            context['error'] = 'Internal Server Error: {}'.format(e)
        return render(request, template_name=self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(to="{}?next=/qbe_search/".format(settings.LOGIN_URL))
        if not request.user.is_staff:
            return JsonResponse({'status': 404, 'error': "You don't have the permission to access this page."})
        devkey = self._get_dev_key()
        if devkey is None:
            return JsonResponse({'status': 404, 'error': "No API key."})
        yt = build_youtube_instance(devkey)
        vid = request.POST.get('vid')
        id = request.POST.get('id')
        if vid is None or id is None:
            return JsonResponse({'status': 404, 'error': 'Wrong format.'})
        videos = Video.objects.filter(id=id, vid=vid)
        if videos.count() < 1:
            return JsonResponse({'status': 404, 'error': 'No query video found.'})
        results = search_qbe(youtube=yt, vid=vid, hd_only=False)
        return JsonResponse({'status': 200, 'results': results})


