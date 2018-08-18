"""test data"""
import os
from datetime import datetime, timedelta

from src.app.models.video import VideoDAO


class TestData:
    VIDEO_ID_1 = 'sm9'
    VIDEO_ID_2 = 'sm654749'
    VIDEO_ID_3 = 'sm893'
    COMMENT_ID_1 = '1'
    COMMENT_ID_2 = '2'
    COMMENT_ID_3 = '3'
    COMMENTED_AT_1 = '2014/08/11'
    COMMENTED_AT_2 = '2018/08/12'
    COMMENTED_POINT_1 = '8:10'
    COMMENTED_POINT_2 = '9:31'

    class Comment:
        TEXT_1 = 'ここすき'
        TEXT_2 = 'ここすすき'
        POSTED_AT_1 = datetime.now().replace(microsecond=0)
        POSTED_AT_2 = POSTED_AT_1 + timedelta(seconds=100)
        POSTED_AT_3 = POSTED_AT_2 + timedelta(seconds=100)
        POSTED_BY_1 = '512810'
        POINT_1 = '8:10'
        WAS_DELETED_1 = False
        OFFICIAL_NICORU_1 = 1

    class Video:
        TITLE_1 = 'ホモと学ぶ大物youtuber OFF会誰も来ずへこむ 1/2'
        TITLE_2 = 'ホモと学ぶ大物youtuber OFF会誰も来ずへこむ 2/2'
        THUMBNAIL_1 = 'http://aiueo700.com/sm9'
        THUMBNAIL_2 = 'http://aiueo700.com/sm654749'
        POSTED_AT_1 = datetime.now().replace(microsecond=0)
        LENGTH_1 = '1145:14'
        WATCH_URL_1 = 'http://www.nicovideo.jp/watch/sm9'
        WATCH_URL_2 = 'http://www.nicovideo.jp/watch/sm654749'
        POSTED_BY_1 = 'aiueo700'
        POSTED_BY_NAME_1 = 'aiueo700'
        UPDATED_AT_1 = datetime.now().replace(microsecond=0)

    class CommentObject:
        CO_1 = {
            'no': 1,
            'thread': 1,
            'mail': 1,
            'user_id': 1,
            'date': datetime.now().timestamp(),
            'vpos': 123,
            'nicoru': 1,
            'deleted': False,
            'content': '<sciprt>alert(1);</script>'
        }


class TestDataReal:
    class Response:
        """real response contents from api for test"""
        DATA = {
            "http://flapi.nicovideo.jp/api/getflv/sm9": "thread_id=1173108780&l=320&url=http%3A%2F%2Fsmile-pcm42.nicovideo.jp%2Fsmile%3Fv%3D9.0468&ms=http%3A%2F%2Fnmsg.nicovideo.jp%2Fapi%2F&ms_sub=http%3A%2F%2Fnmsg.nicovideo.jp%2Fapi%2F&user_id=542192&is_premium=1&nickname=ffeddc&time=1528011484421&done=true&ng_rv=384&userkey=1528013284.%7E1%7Ethu8Y0uMiK1Z5a6vFWBlpPcqR3onRiRZc9HQ7hkxPwg",
            "http://flapi.nicovideo.jp/api/getflv/abc": "error=invalid_thread&done=true",
            "http://ext.nicovideo.jp/api/getthumbinfo/sm9": """<?xml version="1.0" encoding="UTF-8"?>
<nicovideo_thumb_response status="ok">
  <thumb>
    <video_id>sm9</video_id>
    <title>新・豪血寺一族 -煩悩解放 - レッツゴー！陰陽師</title>
    <description>レッツゴー！陰陽師（フルコーラスバージョン）</description>
    <thumbnail_url>http://tn.smilevideo.jp/smile?i=9</thumbnail_url>
    <first_retrieve>2007-03-06T00:33:00+09:00</first_retrieve>
    <length>5:20</length>
    <movie_type>flv</movie_type>
    <size_high>21138631</size_high>
    <size_low>17436492</size_low>
    <view_counter>17167024</view_counter>
    <comment_num>4666040</comment_num>
    <mylist_counter>173582</mylist_counter>
    <last_res_body>wwwwwwwww 卯卯卯卯卯卯卯卯卯卯 その名は・・・ 神妙不可侵にて、釜山 カバ君の力ではどうし </last_res_body>
    <watch_url>http://www.nicovideo.jp/watch/sm9</watch_url>
    <thumb_type>video</thumb_type>
    <embeddable>1</embeddable>
    <no_live_play>0</no_live_play>
    <tags domain="jp">
      <tag lock="1">陰陽師</tag>
      <tag lock="1">レッツゴー！陰陽師</tag>
      <tag lock="1">公式</tag>
      <tag lock="1">音楽</tag>
      <tag lock="1">ゲーム</tag>
      <tag>最古の動画</tag>
      <tag>β時代の英雄</tag>
      <tag>ニコニコ文化を支えている人</tag>
      <tag>3月6日投稿動画</tag>
    </tags>
    <user_id>4</user_id>
    <user_nickname>中の</user_nickname>
    <user_icon_url>https://secure-dcdn.cdn.nimg.jp/nicoaccount/usericon/s/0/4.jpg?1271141672</user_icon_url>
  </thumb>
</nicovideo_thumb_response>""",
            "http://ext.nicovideo.jp/api/getthumbinfo/abc": """<?xml version="1.0" encoding="UTF-8"?>
<nicovideo_thumb_response status="fail">
  <error>
    <code>NOT_FOUND</code>
    <description>not found or invalid</description>
  </error>
</nicovideo_thumb_response>""",
        }


class TestDataLevel2:
    class VideoObject:
        VO_1 = {
            "video_id": TestData.VIDEO_ID_1,
            "title": TestData.Video.TITLE_1,
            "thumbnail_url": TestData.Video.THUMBNAIL_1,
            "length": TestData.Video.LENGTH_1,
            "view_counter": 31674,
            "comment_num": 2783,
            "mylist_counter": 2613,
            "watch_url": TestData.Video.WATCH_URL_1,
            "tags": "サイコマルマイン",
            "user_id": TestData.Video.POSTED_BY_1,
            "user_nickname": TestData.Video.POSTED_BY_NAME_1,
            "user_icon_url": TestData.Video.THUMBNAIL_1,
        }


class TestDataUtil:
    @staticmethod
    def add_video(session, **update):
        data = {
            "id": TestData.VIDEO_ID_1,
            "title": TestData.Video.TITLE_1,
            "thumbnail": TestData.Video.THUMBNAIL_1,
            "posted_at": TestData.Video.POSTED_AT_1,
            "length": TestData.Video.LENGTH_1,
            "watch_url": TestData.Video.WATCH_URL_1,
            "posted_by": TestData.Video.POSTED_BY_1,
            "posted_by_name": TestData.Video.POSTED_BY_NAME_1,
        }
        if update is not None:
            data.update(update)
        v_dao = VideoDAO(session)
        v_dao.add(**data)
        session.commit()

    @staticmethod
    def get_pseudo_response(url: str):
        data = TestDataReal.Response.DATA.get(url)
        if data:
            return data
        if url == "http://flapi.nicovideo.jp/api/getthreadkey?thread=none":
            return ""
        if url.startswith("http://flapi.nicovideo.jp/api/getthreadkey?thread="):
            return "threadkey=114514810893&force_184=0"
        if url == "https://secure.nicovideo.jp/secure/login?site=niconico":
            return
        if url == "http://nmsg.nicovideo.jp/api.json/":
            return [{
                "chat": TestData.CommentObject.CO_1
            }]
        raise NotImplementedError

    @staticmethod
    def make_test_file(path: str, size: int):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write('1' * size)


class DummyResponse:
    def __init__(self):
        self.content = None
        self.text = None
        self.json_data = None

    def json(self):
        return self.json_data


class DummySession:
    def __init__(self):
        self.cookies = {}

    def post(self, url, json=None, data=None):
        r = DummyResponse()
        r.content = r.text = r.json_data = TestDataUtil.get_pseudo_response(url)
        return r

    def get(self, url):
        r = DummyResponse()
        r.content = r.text = r.json_data = TestDataUtil.get_pseudo_response(url)
        return r
