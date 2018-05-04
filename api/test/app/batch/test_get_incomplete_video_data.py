import pytest

from src.app.batch.get_incomplete_video_data import IncompleteVideoDataGetter
from src.app.batch.niconico_api_connector import VideoDataGetError
from src.app.helpers.db_helper import db_session
from src.app.models import Video
from src.app.models.job_log import JobLogDAO, JobLogType, JobLogStatus, JobLog
from src.app.models.nicoru import Nicoru, NicoruDAO


class TestIncompleteVideoDataGetter:
    class Test_execute:
        def test_previous_process_running(self):
            with db_session() as session:
                # setup
                JobLogDAO(session).add_or_update(JobLogType.VIDEO, JobLogStatus.RUNNING)
                session.commit()
                # run, verify
                assert IncompleteVideoDataGetter.execute() == IncompleteVideoDataGetter.ReturnCode.PREVIOUS_PROCESS_IS_RUNNING

        def test_no_incomplete_video(self):
            with db_session() as session:
                # setup
                session.query(JobLog).delete()
                session.query(Nicoru).delete()
                session.commit()
                # run, verify
                assert IncompleteVideoDataGetter.execute() == IncompleteVideoDataGetter.ReturnCode.NO_INCOMPLETE_DATA

        def test_video_data_not_found(self):
            with db_session() as session:
                # setup
                session.query(JobLog).delete()
                session.query(Nicoru).delete()
                session.commit()
                n_dao = NicoruDAO(session)
                n_dao.nicoru('abc', '1')
                n_dao.nicoru('abc', '2')
                session.commit()
                # run
                with pytest.raises(VideoDataGetError):
                    assert IncompleteVideoDataGetter.execute()
                # verify
                assert n_dao.find_by_video_id_and_comment_id('abc', '1') is None

        def test_success_with_wait(self):
            with db_session() as session:
                # setup
                session.query(JobLog).delete()
                session.query(Video).delete()
                session.query(Nicoru).delete()
                session.commit()
                JobLogDAO(session).add_or_update(JobLogType.VIDEO, JobLogStatus.DONE)
                session.commit()
                NicoruDAO(session).nicoru('sm654749', '3')
                session.commit()
                # run, verify
                assert IncompleteVideoDataGetter.execute() == IncompleteVideoDataGetter.ReturnCode.SUCCESS
