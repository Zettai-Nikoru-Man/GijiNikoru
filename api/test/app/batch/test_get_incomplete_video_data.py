from time import sleep

import pytest

from src.app.batch.get_incomplete_video_data import IncompleteVideoDataGetter
from src.app.batch.niconico_api_connector import VideoDataGetError
from src.app.models import IrregularVideoId
from src.app.models.job_log import JobLogDAO, JobLogType, JobLogStatus
from src.app.models.nicoru import NicoruDAO
from test.app.db_test_helper import db_test_session


class TestIncompleteVideoDataGetter:
    class Test_execute:
        def test_previous_process_running(self):
            with db_test_session() as session:
                # setup
                JobLogDAO(session).add_or_update(JobLogType.VIDEO, JobLogStatus.RUNNING)
                session.commit()
                sleep(1)
                # run, verify
                assert IncompleteVideoDataGetter.execute() == IncompleteVideoDataGetter.ReturnCode.PREVIOUS_PROCESS_IS_RUNNING

        def test_no_incomplete_video(self):
            with db_test_session() as session:
                # run, verify
                assert IncompleteVideoDataGetter.execute() == IncompleteVideoDataGetter.ReturnCode.NO_INCOMPLETE_DATA

        def test_video_data_not_found(self):
            with db_test_session() as session:
                # setup
                n_dao = NicoruDAO(session)
                n_dao.nicoru('abc', '1')
                n_dao.nicoru('abc', '2')
                session.commit()
                # run
                with pytest.raises(VideoDataGetError):
                    assert IncompleteVideoDataGetter.execute()
                # verify
                assert session.query(IrregularVideoId).filter(IrregularVideoId.video_id == 'abc') is not None

        def test_success_with_wait(self):
            with db_test_session() as session:
                # setup
                JobLogDAO(session).add_or_update(JobLogType.VIDEO, JobLogStatus.DONE)
                session.commit()
                NicoruDAO(session).nicoru('sm654749', '3')
                session.commit()
                # run, verify
                assert IncompleteVideoDataGetter.execute() == IncompleteVideoDataGetter.ReturnCode.SUCCESS
