from time import sleep

import pytest

from src.app.batch.get_incomplete_comment_data import IncompleteCommentDataGetter
from src.app.batch.niconico_api_connector import CommentDataGetError
from src.app.models.job_log import JobLogDAO, JobLogStatus, JobLogType
from src.app.models.nicoru import NicoruDAO
from src.app.models.video import VideoDAO
from test.app.db_test_helper import db_test_session
from test.app.models.data import TestData


class TestIncompleteCommentDataGetter:
    class Test_execute:
        def test_previous_process_running(self):
            with db_test_session() as session:
                # setup
                JobLogDAO(session).add_or_update(JobLogType.COMMENT, JobLogStatus.RUNNING)
                session.commit()
                sleep(1)
                # run, verify
                assert IncompleteCommentDataGetter.execute() == IncompleteCommentDataGetter.ReturnCode.PREVIOUS_PROCESS_IS_RUNNING

        def test_no_incomplete_video(self):
            with db_test_session() as session:
                # run, verify
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
                with pytest.raises(CommentDataGetError):
                    assert IncompleteCommentDataGetter.execute() == IncompleteCommentDataGetter.ReturnCode.SUCCESS
                j_dao = JobLogDAO(session).find_by_type(JobLogType.COMMENT).status == JobLogStatus.ABORTED
