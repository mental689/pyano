import unittest, os
from data.analysis.youtube import *
from glob import glob
import json


class TestYoutubeDownload(unittest.TestCase):
    def setUp(self):
        self.youtube_idx= [
            "j0r8aGIU6is", # HD, 1080p
            "7HcugJB4yv4" # Normal quality, 360p
        ]

    @unittest.skip("Tested!")
    def test_download(self):
        output_folder = download_youtube_video(self.youtube_idx,
                                               download_caption=False, # no captions
                                               download_audio=False, # no audio
                                               output_folder=None)
        downloaded = [os.path.basename(p) for p in glob(output_folder+"/*")]
        self.assertTrue(self.youtube_idx[0] in downloaded)
        # This will return errors as current version of Youtube-Dl do not filter low quality videos.
        # Instead, they convert the best videos and audios available to match the condition.
        # A little bit sad because we want to prevent them from downloading such artifacts.
        # To implement this feature, a solution is to use Google's official Youtube API v3 to search and filter out low quality works.
        self.assertFalse(self.youtube_idx[1] in downloaded)

    def test_youtube_api(self):
        dev_key = json.load(open("/home/tuananhn/PycharmProjects/SS/test/devKey.json"))
        print(dev_key)
        youtube = build_youtube_instance(dev_key["devKey"])
        results = search_youtube(youtube=youtube,
                                 q="AFC Asian cup 2011", # An examplar big event in the past
                                 download_cc_only=False, # We may need to see videos in default licenses.
                                 download_high_quality=True, # At least HD 720p is required.
                                 check_in_details=False, # whether to check the videos in details using /videos API.
                                 duration_type="long") # videos which are longer than 20 minutes are selected.
        print("# Accepted videos : {}".format(len(results))) # About >500 results are returned.
        for r in results:
            print(r)
        del youtube



