from src.app.util.gn_logger import GNLogger

logger = GNLogger.get_logger(__name__)


class VideoInfo:
    def __init__(self, video_info_object):
        self.video_id = video_info_object["video_id"]
        self.title = video_info_object["title"]
        self.thumbnail_url = video_info_object["thumbnail_url"]
        self.length = video_info_object["length"]
        self.view_count = video_info_object["view_counter"]
        self.comment_count = video_info_object["comment_num"]
        self.mylist_count = video_info_object["mylist_counter"]
        self.watch_url = video_info_object["watch_url"]
        self.tags = video_info_object["tags"]
        self.author_user_id = video_info_object.get("user_id")
        self.author_nickname = video_info_object.get("user_nickname")
        self.author_icon_url = video_info_object.get("user_icon_url")
