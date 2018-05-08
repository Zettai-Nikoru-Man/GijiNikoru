from datetime import datetime

from src.app.models.comment import Comment, CommentDAO
from test.app.db_test_helper import db_test_session
from test.app.models.data import TestData


class TestComment:
    class Test___repr__:
        def test(self):
            record = Comment()
            record.id = TestCommentDAO.ID_1
            assert str(record) == '<Comment {}>'.format(record.id)


class TestCommentDAO:
    ID_1 = '1'

    class Test_add:
        def test(self):
            with db_test_session() as session:
                # run
                dao = CommentDAO(session)
                new = dao.add(
                    id=TestData.COMMENT_ID_1,
                    video_id=TestData.VIDEO_ID_1,
                    text=TestData.Comment.TEXT_1,
                    posted_at=TestData.Comment.POSTED_AT_1,
                    posted_by=TestData.Comment.POSTED_BY_1,
                    point=TestData.Comment.POINT_1,
                    was_deleted=TestData.Comment.WAS_DELETED_1,
                    original_nicorare=TestData.Comment.ORIGINAL_NICORARE_1,
                )
                session.commit()

                # verify
                assert new == dao.find(TestData.COMMENT_ID_1, TestData.VIDEO_ID_1)

    class Test_find:
        def test(self):
            with db_test_session() as session:
                # setup
                dao = CommentDAO(session)
                new = dao.add(
                    id=TestData.COMMENT_ID_1,
                    video_id=TestData.VIDEO_ID_1,
                    text=TestData.Comment.TEXT_1,
                    posted_at=TestData.Comment.POSTED_AT_1,
                    posted_by=TestData.Comment.POSTED_BY_1,
                    point=TestData.Comment.POINT_1,
                    was_deleted=TestData.Comment.WAS_DELETED_1,
                    original_nicorare=TestData.Comment.ORIGINAL_NICORARE_1,
                )
                session.commit()

                # run
                stored = dao.find(TestData.COMMENT_ID_1, TestData.VIDEO_ID_1)

                # verify
                assert new == stored
