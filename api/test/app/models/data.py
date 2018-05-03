"""test data"""
from datetime import datetime


class TestData:
    VIDEO_ID_1 = 'sm114514'
    VIDEO_ID_2 = 'sm512810'
    VIDEO_ID_3 = 'sm893'
    COMMENT_ID_1 = '1'
    COMMENT_ID_2 = '2'
    COMMENTED_AT_1 = '2014/08/11'
    COMMENTED_AT_2 = '2018/08/12'
    COMMENTED_POINT_1 = '8:10'
    COMMENTED_POINT_2 = '9:31'

    class Comment:
        TEXT_1 = 'ここすき'
        POSTED_AT_1 = datetime.now()
        POSTED_BY_1 = '512810'
        POINT_1 = '8:10'
        WAS_DELETED_1 = False
        ORIGINAL_NICORARE_1 = 1
        UPDATED_AT_1 = datetime.now()

    class Video:
        TITLE_1 = 'ホモと学ぶ大物youtuber OFF会誰も来ずへこむ 1/2'
        THUMBNAIL_1 = 'http://aiueo700.com/sm114514'
        POSTED_AT_1 = datetime.now()
        LENGTH_1 = '1145:14'
        WATCH_URL_1 = 'http://www.nicovideo.jp/watch/sm114514'
        POSTED_BY_1 = 'aiueo700'
        POSTED_BY_NAME_1 = 'aiueo700'
        UPDATED_AT_1 = datetime.now()