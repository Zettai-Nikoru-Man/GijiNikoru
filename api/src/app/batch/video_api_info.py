from datetime import datetime

from src.app.util.gn_logger import GNLogger

logger = GNLogger.get_logger(__name__)


class VideoAPIInfo:
    def __init__(self, video_id: str, thread_id: int, user_id: str, ms: str, user_key: str):
        self.video_id = video_id
        self.thread_id = thread_id
        self.user_id = user_id
        self.comment_server_url = ms
        self.comment_server_url_json = self.comment_server_url.replace("/api/", "/api.json/")
        self.posted_at = datetime.fromtimestamp(self.thread_id).strftime('%Y-%m-%d %H:%M:%S')
        self.user_key = user_key
