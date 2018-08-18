"""
dc-test /usr/test/app/batch/test_comments.py
"""

from src.app.batch.comment import Comment
from src.app.batch.comments import Comments
from test.app.models.data import TestData


class TestComments:
    class Test__init__:
        def test_empty_comments(self):
            assert Comments([]).comments == []

        def test_non_empty_comments(self):
            # setup
            comment_data = TestData.CommentObject.CO_1
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
            assert result[0].official_nicoru == comment.official_nicoru
            assert result[0].was_deleted == comment.was_deleted
            assert result[0].text == comment.text

        def test_regular_and_irregular_comments(self):
            # setup
            comment_data = TestData.CommentObject.CO_1
            comment = Comment(comment_data)

            # run
            result = Comments([{'chat': comment_data}, {}]).comments

            # verify
            assert result[0].id == comment.id
