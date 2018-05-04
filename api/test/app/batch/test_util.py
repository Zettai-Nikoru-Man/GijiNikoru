import re
from typing import Optional

from src.app.batch.util import Util


class TestUtil:
    class Test_translate_seconds_to_video_time_point:
        def test(self):
            assert Util.translate_seconds_to_video_time_point(114514) == '1908:34'

    class Test_get_minute_from_video_time_point:
        def test_regular(self):
            assert Util.get_minute_from_video_time_point('1145:14') == '1146'

        def test_irregular(self):
            assert Util.get_minute_from_video_time_point(':14') == '100'

    class Test_get_commented_point:
        def test(self):
            assert Util.get_commented_point('1145:14') == '0-1146'

    class Test_get_block_no:
        def test(self):
            assert Util.get_block_no(298) == 2
            assert Util.get_block_no(299) == 3
            assert Util.get_block_no(300) == 3

    def translate_seconds_to_video_time_point(self, seconds: int):
        """translate seconds to [mm:ss] string

        :param seconds: seconds
        :return: [mm:ss] string
            e.g. "123:45"
        """
        minutes = seconds // 60
        seconds %= 60
        return "%02d:%02d" % (minutes, seconds)

    @classmethod
    def get_minute_from_video_time_point(cls, video_time_point: str) -> Optional[str]:
        """extract minute string from [mm:ss] string

        :param video_time_point: [mm:ss] string
            e.g. "123:45"
        :return: string meaning minutes, or None
        """
        m = re.match(r'^(\d+):\d+$', video_time_point)
        if not m:
            return "100"
        return str(int(m.groups()[0]) + 1)

    @staticmethod
    def get_commented_point(video_length: str):
        return "0-" + Util.get_minute_from_video_time_point(video_length)

    @staticmethod
    def get_block_no(comment_num):
        return int(comment_num + 1) // 100
