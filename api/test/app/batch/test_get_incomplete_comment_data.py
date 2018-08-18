"""
dc-test /usr/test/app/batch/test_get_incomplete_comment_data.py
"""
from datetime import datetime
from typing import List
from unittest import mock

import pytest
from datetime import timedelta

from src.app.batch.comment import Comment
from src.app.batch.comments import Comments
from src.app.batch.get_incomplete_comment_data import IncompleteCommentDataGetter
from src.app.batch.niconico_api_connector import VideoDataGetError, CommentDataGetError, NiconicoAPIConnector
from src.app.models import IrregularVideoId
from src.app.models.irregular_comment_id import IrregularCommentId
from src.app.models.job_log import JobLogDAO, JobLogStatus, JobLogType
from src.app.models.nicoru import NicoruDAO
from src.app.models.video import VideoDAO
from test.app.db_test_helper import db_test_session
from test.app.models.data import TestData, DummySession, TestDataUtil


class TestIncompleteCommentDataGetter:
    @staticmethod
    def get_dummy_comments() -> Comments:
        c = Comments([])
        c.comments = [Comment(TestData.CommentObject.CO_1), Comment(TestData.CommentObject.CO_1)]
        return c

    class Test_execute:
        def test_previous_process_running(self):
            with db_test_session() as session:
                # setup
                vid = TestData.VIDEO_ID_1
                job_log = JobLogDAO(session).add_or_update(JobLogType.COMMENT, JobLogStatus.RUNNING)
                job_log.updated_at == datetime.now() - timedelta(seconds=5)
                NicoruDAO(session).nicoru(video_id=vid, comment_id=TestData.COMMENT_ID_1)
                TestDataUtil.add_video(session)
                session.commit()

                # run, verify
                with mock.patch('requests.Session', DummySession):
                    assert IncompleteCommentDataGetter.execute() == IncompleteCommentDataGetter.ReturnCode.PREVIOUS_PROCESS_IS_RUNNING

        def test_no_incomplete_video(self):
            with db_test_session() as session:
                # run, verify
                with mock.patch('requests.Session', DummySession), \
                     mock.patch.object(NiconicoAPIConnector, 'get_comments',
                                       return_value=TestIncompleteCommentDataGetter.get_dummy_comments()):
                    assert IncompleteCommentDataGetter.execute() == IncompleteCommentDataGetter.ReturnCode.NO_INCOMPLETE_DATA

        def test_success(self):
            with db_test_session() as session:
                # setup
                JobLogDAO(session).add_or_update(JobLogType.COMMENT, JobLogStatus.DONE)
                session.commit()
                video_id = 'sm654749'
                v_dao = VideoDAO(session)
                v_dao.add(
                    id=video_id,
                    title=TestData.Video.TITLE_1,
                    thumbnail=TestData.Video.THUMBNAIL_1,
                    posted_at=TestData.Video.POSTED_AT_1,
                    length=TestData.Video.LENGTH_1,
                    watch_url=TestData.Video.WATCH_URL_1,
                    posted_by=TestData.Video.POSTED_BY_1,
                    posted_by_name=TestData.Video.POSTED_BY_NAME_1,
                )
                n_dao = NicoruDAO(session)
                n_dao.nicoru(video_id, TestData.COMMENT_ID_3)
                session.commit()

                # run, verify
                with mock.patch('requests.Session', DummySession), \
                     mock.patch.object(NiconicoAPIConnector, 'get_comments',
                                       return_value=TestIncompleteCommentDataGetter.get_dummy_comments()):
                    assert IncompleteCommentDataGetter.execute() == IncompleteCommentDataGetter.ReturnCode.SUCCESS

        def test_get_no_comment_data(self):
            with db_test_session() as session:
                # setup
                video_id = 'abc'
                v_dao = VideoDAO(session)
                v_dao.add(
                    id=video_id,
                    title=TestData.Video.TITLE_1,
                    thumbnail=TestData.Video.THUMBNAIL_1,
                    posted_at=TestData.Video.POSTED_AT_1,
                    length=TestData.Video.LENGTH_1,
                    watch_url=TestData.Video.WATCH_URL_1,
                    posted_by=TestData.Video.POSTED_BY_1,
                    posted_by_name=TestData.Video.POSTED_BY_NAME_1,
                )
                n_dao = NicoruDAO(session)
                n_dao.nicoru(video_id, '1')
                session.commit()

                # run, verify
                with mock.patch('requests.Session', DummySession), \
                     mock.patch.object(NiconicoAPIConnector, 'get_comments', side_effect=VideoDataGetError):
                    with pytest.raises(VideoDataGetError):
                        IncompleteCommentDataGetter.execute()

                # verify
                ivis = session.query(IrregularVideoId).all()  # type: List[IrregularVideoId]
                assert len(ivis) == 1
                assert ivis[0].video_id == video_id
                assert JobLogDAO(session).find_by_type(JobLogType.COMMENT).status == JobLogStatus.ABORTED

    class Test_get_and_register_data:
        def test_comment_data_get_error(self):
            with db_test_session() as session:
                # setup
                vid = 'sm654749'
                cid = ['1', '2']
                with mock.patch('requests.Session', DummySession), \
                     mock.patch.object(NiconicoAPIConnector, 'get_comments', side_effect=CommentDataGetError):
                    with pytest.raises(CommentDataGetError):
                        # run
                        IncompleteCommentDataGetter.get_and_register_data(session, (vid, cid))

                # verify
                stored_icis = session.query(IrregularCommentId).all()  # type: List[IrregularCommentId]
                assert len(stored_icis) == 2
                assert stored_icis[0].video_id == vid
                assert stored_icis[0].comment_id == cid[0]
                assert stored_icis[1].comment_id == cid[1]
                assert JobLogDAO(session).find_by_type(JobLogType.COMMENT).status == JobLogStatus.ABORTED

        def test_comment_data_duplicate(self):
            with db_test_session() as session:
                # setup
                vid = 'sm654749'
                cid = ['1', '2']

                with mock.patch('requests.Session', DummySession), \
                     mock.patch.object(NiconicoAPIConnector, 'get_comments',
                                       return_value=TestIncompleteCommentDataGetter.get_dummy_comments()):
                    # run
                    IncompleteCommentDataGetter.get_and_register_data(session, (vid, cid))
                    session.commit()

                # verify
                stored_icis = session.query(IrregularCommentId).all()  # type: List[IrregularCommentId]
                assert len(stored_icis) == 1
                assert stored_icis[0].video_id == vid
                assert stored_icis[0].comment_id == '2'
