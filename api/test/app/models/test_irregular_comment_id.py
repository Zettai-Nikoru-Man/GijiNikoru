from typing import List

from src.app.models.irregular_comment_id import IrregularCommentId, IrregularCommentIdDAO
from test.app.db_test_helper import db_test_session
from test.app.models.data import TestData


class TestIrregularCommentIdDAO:
    class Test_add:
        def test(self):
            with db_test_session() as session:
                # run
                IrregularCommentIdDAO(session).add(
                    video_id=TestData.VIDEO_ID_1,
                    comment_ids=[TestData.COMMENT_ID_1, TestData.COMMENT_ID_2],
                )
                session.commit()

                # verify
                stored = session.query(IrregularCommentId).all()  # type: List[IrregularCommentId]
                assert len(stored) == 2
                assert stored[0].video_id == TestData.VIDEO_ID_1
                assert stored[0].comment_id == TestData.COMMENT_ID_1
                assert stored[1].video_id == TestData.VIDEO_ID_1
                assert stored[1].comment_id == TestData.COMMENT_ID_2
