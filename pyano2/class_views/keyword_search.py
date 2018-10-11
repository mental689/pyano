from django.views import View
from pyano2.models import Topic, Keyword, SearchResult, SystemSetting, User
from survey.models import Video, VideoCategory, Response
from django.contrib.auth.models import AnonymousUser

from data.analysis.youtube import search_youtube, build_youtube_instance
import logging, json
from django.shortcuts import render
from time import time
import math


class KeywordSearchView(View):
    template_name = "keyword_search.html"

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

    def _search_youtube(self, keyword, user, topic, pref, cc=True, hd=False, duration="any"):
        k = keyword.strip()
        dev_key = self._get_dev_key()
        if dev_key is None:
            return None
        yt = build_youtube_instance(dev_key)
        results = search_youtube(youtube=yt, q=keyword, download_cc_only=cc, download_high_quality=hd, duration_type=duration)
        # insert data
        keys = Keyword.objects.filter(topic__id=topic.id, content=keyword, user__id=user.id)
        if len(keys) == 0:
            key = Keyword()
            key.content = keyword.strip()
            key.user = user
            key.topic = topic
            key.save()
        else:
            key = keys[0]
        record = SearchResult()
        record.keyword = key
        record.content = results
        record.pref = pref
        try:
            record.save()
        except Exception as e:
            logging.error(e)

        for r in results:
            if 'id' in r and 'kind' in r['id'] and 'videoId' in r['id'] and r['id']['kind'] == "youtube#video":
                v = Video()
                v.url = "https://youtube.com/watch?v={}".format(r['id']['videoId'])
                v.vid = r['id']['videoId']
                v.cat = VideoCategory.objects.filter(id=1)[0]
                v.type = 0
                v.start = 0
                v.end = 0
                try:
                    v.save()
                except Exception as e:
                    logging.error(e)
        return record

    def post(self, request, *args, **kwargs):
        # logging.info(request.POST)
        keywords = request.POST.get("keywords").split(",")
        video_idx = []
        user = request.user
        if user is None or isinstance(user, AnonymousUser):
            user = User()
            user.username = "Guest_{}".format(time())
            user.save()
        topic_txt = request.POST.get("topic")
        topics = Topic.objects.filter(name=topic_txt)
        if len(topics) == 0:
            topic = Topic()
            topic.name = topic_txt
            topic.save()
        else:
            topic = topics[0]
        hd, cc, duration = False, False, "any"
        if "hd" in request.POST.getlist("pref[]"):
            hd = True
        if "cc" in request.POST.getlist("pref[]"):
            cc = True
        if "long" in request.POST.getlist("pref[]"):
            duration = "long"
        for keyword in keywords:
            record = self._search_youtube(keyword=keyword,
                                          topic=topic,
                                          user=user,
                                          pref=request.POST.getlist("pref[]"),
                                          hd=hd, cc=cc, duration=duration)
            results = record.content
            for result in results:
                if not "id" in result or not "videoId" in result["id"]:
                    continue
                video_idx.append(result["id"]["videoId"])
        video_idx = list(set(video_idx))

        context = {"video_idx": video_idx, "num_results": len(video_idx), "keywords": request.POST.get("keywords")}
        # logging.info(request.POST.getlist("pref[]"))
        logging.info(len(video_idx))
        return render(request, template_name=self.template_name, context=context)
