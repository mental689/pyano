import logging

from django.shortcuts import render, redirect
from django.conf import settings
from django.views import View
from django.http import JsonResponse

from pyano2.models import *
from survey.models import *


class LockChannelView(View):
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

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff: # Currently only staffs can block videos
            return JsonResponse({'error': 'No permission', 'status': 404})
        id = request.POST.get('id', None)
        if id is not None:
            videos = Video.objects.filter(id=id)
            if videos.count() == 0:
                return JsonResponse({'error': "Video's not found", 'status': 404})
            dev_key = self._get_dev_key()
            if dev_key is None:
                return JsonResponse({'error': 'Internal server error', 'status': 404})
            yt = build_youtube_instance(dev_key)
            item_details = get_video_details(yt, video_id=videos[0].vid)
            cid = item_details['snippet']['channelId']
            new_blocking = BlockedChannel()
            new_blocking.channelId = cid
            new_blocking.save()
        return JsonResponse({'status': 200})
