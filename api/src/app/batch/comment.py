import html
from datetime import datetime

from src.app.batch.util import Util


class Comment:
    """コメントAPI返却値中のコメント1件を表すクラス"""

    def __init__(self, comment_object):
        # コメントID
        self.id = str(comment_object["no"])
        # スレッド
        self.thread = comment_object["thread"]
        # コマンド
        self.mail = comment_object.get("mail", "")
        # コメント投稿者ユーザID
        self.posted_by = comment_object.get("user_id", "")
        # コメント投稿日時
        self.posted_at = datetime.fromtimestamp(comment_object["date"])
        # コメントが投稿された動画内時点
        self.point = Util.translate_seconds_to_video_time_point(comment_object["vpos"] / 100)
        # 旧ニコられ数
        self.old_nicoru = int(comment_object.get("nicoru", 0))
        # 削除されているか
        self.was_deleted = bool(comment_object.get("deleted"))
        # コメント内容
        self.text = "このコメントは削除されました" if self.was_deleted else html.escape(comment_object["content"])
