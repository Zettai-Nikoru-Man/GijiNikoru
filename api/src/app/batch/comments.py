from typing import List

from src.app.batch.comment import Comment


class Comments:
    """コメントAPI返却値クラス"""

    def __init__(self, api_result):
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
