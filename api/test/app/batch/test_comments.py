from datetime import datetime

from src.app.batch.comment import Comment
from src.app.batch.comments import Comments


class TestComments:
    class Test__init__:
        def test_empty_comments(self):
            assert Comments([]).comments == []

        def test_non_empty_comments(self):
            # setup
            comment_data = {
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
            comment = Comment(comment_data)
            # run
            result = Comments([{'chat': comment_data}]).comments
            # verify
            assert result[0].id == comment.id
            assert result[0].thread == comment.thread
            assert result[0].mail == comment.mail
            assert result[0].posted_by == comment.posted_by
            assert result[0].posted_at == comment.posted_at
            assert result[0].point == comment.point
            assert result[0].old_nicoru == comment.old_nicoru
            assert result[0].was_deleted == comment.was_deleted
            assert result[0].text == comment.text
