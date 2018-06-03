"""
dc-test /usr/test/app/batch/test_niconico_api_connector.py
"""
import pytest
import requests

from src.app.batch.niconico_api_connector import NiconicoAPIConnector, VideoDataGetError, CommentDataGetError


class TestNiconicoAPIConnector:
    API_CONNECTOR = NiconicoAPIConnector()

#     @staticmethod
#     class DummyResponse:
#         def __init__(self):
#             self.content = None
#
#     @staticmethod
#     class DummySession:
#         def __init__(self):
#             self.cookies = {}
#
#         def post(self, url, json=None, data=None):
#             if url == "https://secure.nicovideo.jp/secure/login?site=niconico":
#                 return
#
#         def get(self, url):
#             if url == "http://ext.nicovideo.jp/api/getthumbinfo/sm9":
#                 r = TestNiconicoAPIConnector.DummyResponse()
#                 r.content = """<?xml version="1.0" encoding="UTF-8"?>
# <nicovideo_thumb_response status="ok">
#   <thumb>
#     <video_id>sm9</video_id>
#     <title>新・豪血寺一族 -煩悩解放 - レッツゴー！陰陽師</title>
#     <description>レッツゴー！陰陽師（フルコーラスバージョン）</description>
#     <thumbnail_url>http://tn.smilevideo.jp/smile?i=9</thumbnail_url>
#     <first_retrieve>2007-03-06T00:33:00+09:00</first_retrieve>
#     <length>5:20</length>
#     <movie_type>flv</movie_type>
#     <size_high>21138631</size_high>
#     <size_low>17436492</size_low>
#     <view_counter>17167024</view_counter>
#     <comment_num>4666040</comment_num>
#     <mylist_counter>173582</mylist_counter>
#     <last_res_body>wwwwwwwww 卯卯卯卯卯卯卯卯卯卯 その名は・・・ 神妙不可侵にて、釜山 カバ君の力ではどうし </last_res_body>
#     <watch_url>http://www.nicovideo.jp/watch/sm9</watch_url>
#     <thumb_type>video</thumb_type>
#     <embeddable>1</embeddable>
#     <no_live_play>0</no_live_play>
#     <tags domain="jp">
#       <tag lock="1">陰陽師</tag>
#       <tag lock="1">レッツゴー！陰陽師</tag>
#       <tag lock="1">公式</tag>
#       <tag lock="1">音楽</tag>
#       <tag lock="1">ゲーム</tag>
#       <tag>最古の動画</tag>
#       <tag>β時代の英雄</tag>
#       <tag>ニコニコ文化を支えている人</tag>
#       <tag>3月6日投稿動画</tag>
#     </tags>
#     <user_id>4</user_id>
#     <user_nickname>中の</user_nickname>
#     <user_icon_url>https://secure-dcdn.cdn.nimg.jp/nicoaccount/usericon/s/0/4.jpg?1271141672</user_icon_url>
#   </thumb>
# </nicovideo_thumb_response>"""
#                 return r
#             if url == "http://ext.nicovideo.jp/api/getthumbinfo/abc":
#                 r = TestNiconicoAPIConnector.DummyResponse()
#                 r.content = """<?xml version="1.0" encoding="UTF-8"?>
# <nicovideo_thumb_response status="fail">
#   <error>
#     <code>NOT_FOUND</code>
#     <description>not found or invalid</description>
#   </error>
# </nicovideo_thumb_response>"""
#                 return r

    class Test_get_video_info:
        def test(self):
            # requests.Session = TestNiconicoAPIConnector.DummySession
            result = NiconicoAPIConnector().get_video_info('sm9')
            assert int(result.comment_count) > 10000

        def test_not_found(self):
            with pytest.raises(VideoDataGetError):
                NiconicoAPIConnector().get_video_info('abc')

    class Test_get_video_api_info:
        def test(self):
            result = NiconicoAPIConnector().get_video_api_info('sm9')
            assert result.video_id == 'sm9'

    class Test_get_comments:
        def test_non_offical_video(self):
            result = NiconicoAPIConnector().get_comments('sm9')
            assert result.count > 100

        def test_offical_video(self):
            result = NiconicoAPIConnector().get_comments('1524623846')
            assert result.count > 100

        def test_comment_data_get_error(self):
            # setup
            NiconicoAPIConnector.get_video_api_info = lambda: 1 / 0

            # run, verify
            with pytest.raises(CommentDataGetError):
                NiconicoAPIConnector().get_comments('')
