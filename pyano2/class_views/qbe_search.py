import json

from django.shortcuts import render, redirect
from django.conf import settings
from django.views import View
from survey.models import Video, VideoCategory
from django.db.models import Count
from django.http import JsonResponse

from pyano2.downloader.youtube import build_youtube_instance, search_qbe
from pyano2.models import *
from survey.models import *


class QBEVideoSearchView(View):
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
            return redirect(to="{}?next=/qbe_search/".format(settings.LOGIN_URL))
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
                videos = videos.filter(num_responses__gte=0) # videos with more than 1 answers will be used.
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
        videos = Video.objects.filter(id=id,vid=vid)
        if videos.count() < 1:
            return JsonResponse({'status': 404, 'error': 'No query video found.'})
        results = search_qbe(youtube=yt, vid=vid, hd_only=False)
        return JsonResponse({'status': 200, 'results': results})
