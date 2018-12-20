import logging

from django.shortcuts import render, redirect
from django.conf import settings
from django.views import View
from survey.models import Video, VideoCategory
from django.utils.html import escape

from pyano2.downloader.youtube import search_youtube, build_youtube_instance
from pyano2.models import Topic, Keyword, SearchResult, SystemSetting, FreebaseTopic


class KeywordSearchView(View):
    template_name = "pyano2/keyword_search.html"

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

    def _search_youtube(self, keyword, user, topic, freebaseid, pref, cc=True, hd=False, duration="any"):
        k = keyword.strip()
        dev_key = self._get_dev_key()
        if dev_key is None:
            return None
        yt = build_youtube_instance(dev_key)
        results = search_youtube(youtube=yt, q=keyword, download_cc_only=cc, download_high_quality=hd, duration_type=duration, freebase_topic_id=freebaseid)
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
        record.content = escape(results)
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
        if not request.user.is_authenticated:
            return redirect(to="{}?next=/".format(settings.LOGIN_URL))
        logging.info(request.POST)
        keywords = request.POST.get("keywords").split(",")
        video_idx = []
        user = request.user
        # if user is None or isinstance(user, AnonymousUser):
        #     user = User()
        #     user.username = "Guest_{}".format(time())
        #     user.save()
        topic_id = request.POST.get("topic")
        freebaseid = request.POST.get("freebaseid")
        topics = Topic.objects.filter(id=topic_id)
        topic = topics[0]
        if freebaseid != "":
            found = False
            for freebase in topic.freebases.all():
                if freebase.gid == freebaseid:
                    found = True
                    break
            if not found:
                try:
                    f = FreebaseTopic()
                    f.gid = freebaseid
                    f.pyanoTopic = topic
                    f.save()
                except Exception as e:
                    logging.error(e)
        hd, cc, duration = False, False, "any"
        pref = []
        if request.POST.get("pref_hd"):
            pref.append(request.POST.get("pref_hd"))
            hd = True
        if request.POST.get("pref_cc"):
            pref.append(request.POST.get("pref_cc"))
            cc = True
        if request.POST.get("pref_long"):
            pref.append(request.POST.get("pref_long"))
            duration = "long"
        for keyword in keywords:
            if keyword is None or keyword == "":
                continue
            record = self._search_youtube(keyword=keyword,
                                          topic=topic,
                                          freebaseid=freebaseid,
                                          user=user,
                                          pref=pref,
                                          hd=hd, cc=cc, duration=duration)
            if record is None:
                video_idx = list(set(video_idx))
                context = {"video_idx": video_idx, "num_results": len(video_idx),
                           "keywords": request.POST.get("keywords"),
                           "error": "Cannot obtain your record after {} results!".format(len(video_idx))}
                return render(request, template_name=self.template_name, context=context)
            results = record.content
            for result in results:
                if not "id" in result or not "videoId" in result["id"]:
                    continue
                video_idx.append(result["id"]["videoId"])
        video_idx = list(set(video_idx))

        context = {"video_idx": video_idx, "num_results": len(video_idx),
                   "keywords": request.POST.get("keywords"), "error": None}
        # logging.info(request.POST.getlist("pref[]"))
        logging.info(len(video_idx))
        return render(request, template_name=self.template_name, context=context)
