import re
from typing import Optional


class Util:
    @classmethod
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
