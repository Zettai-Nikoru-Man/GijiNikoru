from typing import List

from src.app.batch.comment import Comment


class Comments:
    """コメントAPI返却値クラス"""

    def __init__(self, condition, api_result):
        if not api_result:
            raise Exception("コメントの取得に失敗しました。")
        thread = api_result[0]["thread"]

        # スレッド
        self.thread = thread["thread"]
        # チケット
        self.ticket = thread.get("ticket")
        # 動画情報
        self.video_info = condition["video_info"]
        # コメント投稿日時
        self.commented_at = condition["commented_at"]
        # コメント投稿動画内時点
        self.commented_point = condition["commented_point"]

        count = 0
        comments = []
        for data in api_result:
            chat = data.get("chat")
            if not chat:
                continue
            count += 1
            comments.append(Comment(chat))
        if comments:
            self.min_comment_id = comments[0].id
            self.max_comment_id = comments[-1].id
        else:
            self.min_comment_id = None
            self.max_comment_id = None
        self.comments = comments  # type: List[Comment]
        self.count = count
