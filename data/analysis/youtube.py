import youtube_dl
import logging
from time import time
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

LOG_FILE = "./log/youtube_{}.log".format(time())
if not os.path.exists("./log"):
    os.makedirs("./log")
formatter = logging.Formatter(fmt="[%(asctime)s]\t[%(levelname)s]\t[%(message)s]")
logger = logging.getLogger("youtube")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(fmt=formatter)
logger.addHandler(hdlr=file_handler)


def download_youtube_video(youtube_ids, download_caption=False, download_audio=False, output_folder=None):
    if output_folder is not None:
        assert os.path.exists(output_folder), "{} does not exist!".format(output_folder)
    else:
        current_time = time()
        output_folder = os.path.abspath("./{}".format(current_time))
        try:
            os.makedirs(output_folder)
        except Exception as e:
            logger.error(e)
            return

    if download_caption:
        allsubtitles = True
    else:
        allsubtitles = False
    if download_audio:
        fmt = "bestvideo[height>=720,width>=1080,filesize<=5G]+bestaudio"
    else:
        fmt = "bestvideo[height>=720,width>=1080,filesize<=5G]"
    options = {
        "format": fmt,  # download High-definition (HD) formats with less than 5GB in size only
        "verbose": True,  # print verbosity
        "min_views": 10,  # don't download videos with less than 10 views
        "age_limit": 18,  # videos which are not appropriate for children less than 18 yrs will be ignored
        "writesubtitles": download_caption,  # whether to download captions or not
        "allsubtitles": allsubtitles,
    # if download_caption is True, then download all available captions, otherwise, download nothing.
        "ignoreerrors": True,  # ip errors occur, skip to next video in the list
        "noplaylist": True,  # don't download playlists
        "outtmpl": output_folder + "/%(id)s.%(ext)s",
        "logger": logger  # logger object
    }
    url_list = []
    for idx in youtube_ids:
        logger.info("Starting download {} ...".format(url_list))
        url_list.append("https://www.youtube.com/watch?v={}".format(idx))
    with youtube_dl.YoutubeDL(options) as ydl:
        try:
            ydl.download(url_list=url_list)
        except Exception as e:
            logger.error(e)
            return
    return output_folder


def build_youtube_instance(dev_key):
    try:
        youtube = build("youtube", "v3", developerKey=dev_key)
    except Exception as e:
        logger.error(e)
        return None
    return youtube


def get_video_details(youtube, video_id):
    logger.debug("Getting details of {} ...".format(video_id))
    try:
        videos = youtube.videos()
    except Exception as e:
        logger.error(e)
        return None
    try:
        results = videos.list(
            id=video_id,
            part="contentDetails"
        ).execute(num_retries=5)
        if "pageInfo" in results and "items" in results and "totalResults" in results["pageInfo"]:
            if results["pageInfo"]["totalResults"] == 0 or len(results["items"]) == 0:
                return None
            items = results["items"]
            items.sort(key=lambda k: k["id"])
            return items[0]
        else:
            return None
    except HttpError as e:
        logger.error(e)
        return None


def check_details(details, check_words=["fake", "fool", "troll"], check_rating=True, youtube=None):
    pass


def search_youtube(youtube, q, download_cc_only=True, download_high_quality=True, check_in_details=True, duration_type="long"):
    try:
        searcher = youtube.search()
    except Exception as e:
        logger.error(e)
        return []
    # first request
    videos = []
    videoDefinition = "high" if download_high_quality else "any"
    videoLicense = "creativeCommon" if download_cc_only else "any"
    logger.debug("============= Downloading first response ...")
    try:
        responses = searcher.list(
            q=q,
            maxResults=50,
            type="video",
            part="id,snippet",
            videoDefinition=videoDefinition,
            videoLicense=videoLicense,
            videoDuration=duration_type
        ).execute()
    except HttpError as e:
        logger.error("Error while downloading first response ...")
        logger.error(e)
        return videos
    logger.debug("Found {} records ...".format(responses["pageInfo"]["totalResults"]))
    if check_in_details:
        for r in responses["items"]:
            if "id" in r and "videoId" in r["id"]:
                details = get_video_details(youtube, video_id=r["id"]["videoId"])
                if details is not None and "contentDetails" in details and \
                        "definition" in details["contentDetails"]:
                    if (details["contentDetails"]["definition"] != "hd" and download_high_quality):
                        continue
                    else:
                        logger.debug("Accepted {} ...".format(r["id"]["videoId"]))
                        videos.append(r)
    else:
        for r in responses["items"]:
            videos.append(r)
    count = 1
    while "nextPageToken" in responses:
        pageToken = responses["nextPageToken"]
        count += 1
        logger.debug("============= Downloading {}-th response with token {} ...".format(count, pageToken))
        try:
            responses = searcher.list(
                q=q,
                maxResults=50,
                type="video",
                part="id,snippet",
                videoDefinition=videoDefinition,
                videoLicense=videoLicense,
                pageToken=pageToken,
                videoDuration=duration_type
            ).execute()
        except HttpError as e:
            logger.error("Error while downloading {}-th response ...".format(count))
            logger.error(e)
            return videos
        if check_in_details:
            for r in responses["items"]:
                if "id" in r and "videoId" in r["id"]:
                    details = get_video_details(youtube, video_id=r["id"]["videoId"])
                    if details is not None and "contentDetails" in details and \
                            "definition" in details["contentDetails"]:
                        if (details["contentDetails"]["definition"] != "hd" and download_high_quality):
                            continue
                        else:
                            logger.debug("Accepted {} ...".format(r["id"]["videoId"]))
                            videos.append(r)
        else:
            for r in responses["items"]:
                videos.append(r)
    return videos
