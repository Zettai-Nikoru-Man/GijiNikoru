"""
dc-test /usr/test/app/batch/test_get_incomplete_video_data.py
"""
from datetime import datetime, timedelta
from typing import List
from unittest import mock

import pytest

from src.app.batch.get_incomplete_video_data import IncompleteVideoDataGetter
from src.app.batch.niconico_api_connector import VideoDataGetError, NiconicoAPIConnector
from src.app.batch.video_api_info import VideoAPIInfo
from src.app.batch.video_info import VideoInfo
from src.app.models import IrregularVideoId
from src.app.models.job_log import JobLogDAO, JobLogType, JobLogStatus
from src.app.models.nicoru import NicoruDAO
from src.app.models.video import Video
from test.app.db_test_helper import db_test_session
from test.app.models.data import TestData, TestDataLevel2, TestDataUtil, DummySession


class TestIncompleteVideoDataGetter:
    class Test_execute:
        def test_previous_process_running(self):
            with db_test_session() as session:
                # setup
                job_log = JobLogDAO(session).add_or_update(JobLogType.VIDEO, JobLogStatus.RUNNING)
                job_log.updated_at == datetime.now() - timedelta(seconds=5)
                session.commit()

                vid = TestData.VIDEO_ID_1
                video_api_info = VideoAPIInfo(video_id=vid, thread_id=1, user_id='aiueo700', ms='a', user_key='b')
                video_info = VideoInfo(TestDataLevel2.VideoObject.VO_1)
                assert video_api_info.video_id == video_info.video_id == vid

                with mock.patch('requests.Session', DummySession), \
                     mock.patch.object(NiconicoAPIConnector, 'get_video_info', return_value=video_info), \
                     mock.patch.object(NiconicoAPIConnector, 'get_video_api_info', return_value=video_api_info):
                    # run, verify
                    assert IncompleteVideoDataGetter.execute() == IncompleteVideoDataGetter.ReturnCode.PREVIOUS_PROCESS_IS_RUNNING

        def test_no_incomplete_video(self):
            with db_test_session() as session:
                assert IncompleteVideoDataGetter.execute() == IncompleteVideoDataGetter.ReturnCode.NO_INCOMPLETE_DATA

        def test_success_without_wait(self):
            with db_test_session() as session:
                # setup
                vid = TestData.VIDEO_ID_1
                video_api_info = VideoAPIInfo(video_id=vid, thread_id=1, user_id='aiueo700', ms='a', user_key='b')
                video_info = VideoInfo(TestDataLevel2.VideoObject.VO_1)
                assert video_api_info.video_id == video_info.video_id == vid
                NicoruDAO(session).nicoru(video_id=vid, comment_id='1')
                session.commit()

                # run, verify
                with mock.patch('requests.Session', DummySession), \
                     mock.patch.object(NiconicoAPIConnector, 'get_video_info', return_value=video_info), \
                     mock.patch.object(NiconicoAPIConnector, 'get_video_api_info', return_value=video_api_info):
                    assert IncompleteVideoDataGetter.execute() == IncompleteVideoDataGetter.ReturnCode.SUCCESS

    class Test_get_and_register_data:
        def test_got_data_id_exists_in_db(self):
            with db_test_session() as session:
                # setup
                vid = TestData.VIDEO_ID_1
                TestDataUtil.add_video(session, id=vid)
                video_api_info = VideoAPIInfo(video_id=vid, thread_id=1, user_id='aiueo700', ms='a', user_key='b')
                video_info = VideoInfo(TestDataLevel2.VideoObject.VO_1)
                assert video_api_info.video_id == video_info.video_id == vid

                with mock.patch('requests.Session', DummySession), \
                     mock.patch.object(NiconicoAPIConnector, 'get_video_info', return_value=video_info), \
                     mock.patch.object(NiconicoAPIConnector, 'get_video_api_info', return_value=video_api_info):
                    # run
                    IncompleteVideoDataGetter.get_and_register_data(session, TestData.VIDEO_ID_2)
                    session.commit()

                # verify
                stored = session.query(Video).all()  # type: List[Video]
                assert len(stored) == 2
                assert stored[0].id == TestData.VIDEO_ID_2
                assert stored[1].id == TestData.VIDEO_ID_1

        def test_video_data_get_error(self):
            with db_test_session() as session:
                # setup
                vid = TestData.VIDEO_ID_1
                TestDataUtil.add_video(session, id=vid)
                video_api_info = VideoAPIInfo(video_id=vid, thread_id=1, user_id='aiueo700', ms='a', user_key='b')
                video_info = VideoInfo(TestDataLevel2.VideoObject.VO_1)
                assert video_api_info.video_id == video_info.video_id == vid

                with mock.patch('requests.Session', DummySession), \
                     mock.patch.object(NiconicoAPIConnector, 'get_video_info', side_effect=VideoDataGetError), \
                     mock.patch.object(NiconicoAPIConnector, 'get_video_api_info', side_effect=VideoDataGetError):
                    with pytest.raises(VideoDataGetError):
                        # run
                        IncompleteVideoDataGetter.get_and_register_data(session, vid)

                # verify
                stored = session.query(IrregularVideoId).all()  # type: List[IrregularVideoId]
                assert len(stored) == 1
                assert stored[0].video_id == TestData.VIDEO_ID_1
                assert JobLogDAO(session).find_by_type(JobLogType.VIDEO).status == JobLogStatus.ABORTED
