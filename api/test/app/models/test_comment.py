from datetime import datetime

from src.app.helpers.db_helper import db_session
from src.app.models.comment import Comment, CommentDAO
from test.app.models.data import TestData


class TestComment:
    class Test___repr__:
        def test(self):
            record = Comment()
            record.id = TestCommentDAO.ID_1
            assert str(record) == '<Comment {}>'.format(record.id)


class TestCommentDAO:
    ID_1 = '1'
    VIDEO_ID_1 = 'sm114514'
    TEXT_1 = 'ここすき'
    POSTED_AT_1 = datetime.now()
    POSTED_BY_1 = '512810'
    POINT_1 = '8:10'
    WAS_DELETED_1 = True
    ORIGINAL_NICORARE_1 = 1
    UPDATED_AT_1 = datetime.now()

    class Test_add:
        def test(self):
            with db_session() as session:
                # setup
                session.query(Comment).delete()
                dao = CommentDAO(session)

                # run
                new = dao.add(
                    id=TestData.COMMENT_ID_1,
                    video_id=TestData.VIDEO_ID_1,
                    text=TestData.Comment.TEXT_1,
                    posted_at=TestData.Comment.POSTED_AT_1,
                    posted_by=TestData.Comment.POSTED_BY_1,
                    point=TestData.Comment.POINT_1,
                    was_deleted=TestData.Comment.WAS_DELETED_1,
                    original_nicorare=TestData.Comment.ORIGINAL_NICORARE_1,
                    updated_at=TestData.Comment.UPDATED_AT_1,
                )

                # verify
                assert new == dao.find(TestData.COMMENT_ID_1, TestData.VIDEO_ID_1)

    class Test_find:
        def test(self):
            with db_session() as session:
                # setup
                session.query(Comment).delete()
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
                    updated_at=TestData.Comment.UPDATED_AT_1,
                )

                # run
                stored = dao.find(TestData.COMMENT_ID_1, TestData.VIDEO_ID_1)

                # verify
                assert new == stored
