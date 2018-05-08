from datetime import datetime

from src.app.models.job_log import JobLog, JobLogType, JobLogDAO
from src.app.models.job_log import JobLogStatus
from test.app.db_test_helper import db_test_session


class TestJobLog:
    class Test___repr__:
        def test(self):
            record = JobLog()
            record.status = JobLogStatus.DONE
            record.type = JobLogType.VIDEO
            record.updated_at = datetime.now()
            assert str(record) == '<JobLog {} {}>'.format(record.type, record.updated_at)


class TestJobLogDAO:
    class Test_find_video_type:
        def test_get_no_record(self):
            with db_test_session() as session:
                # run
                record = JobLogDAO(session).find_by_type(JobLogType.VIDEO)
                # verify
                assert record is None

        def test_get_one_record(self):
            with db_test_session() as session:
                # setup
                new = JobLog()
                new.type = JobLogType.VIDEO
                new.status = JobLogStatus.DONE
                session.add(new)
                session.commit()
                # run
                record = JobLogDAO(session).find_by_type(JobLogType.VIDEO)
                # verify
                assert record.type == JobLogType.VIDEO
                assert record.status == JobLogStatus.DONE

    class Test_add_or_update:
        def test_add(self):
            with db_test_session() as session:
                # setup
                before = datetime.now()
                # run
                record = JobLogDAO(session).add_or_update(JobLogType.VIDEO, JobLogStatus.DONE)
                # verify
                assert record.type == JobLogType.VIDEO
                assert record.status == JobLogStatus.DONE
                after = datetime.now()
                assert after > record.updated_at > before

        def test_update(self):
            with db_test_session() as session:
                # setup
                before = datetime.now()
                dao = JobLogDAO(session)
                dao.add_or_update(JobLogType.VIDEO, JobLogStatus.ABORTED)
                session.commit()
                # run
                record = dao.add_or_update(JobLogType.VIDEO, JobLogStatus.DONE)
                # verify
                assert record.type == JobLogType.VIDEO
                assert record.status == JobLogStatus.DONE
                after = datetime.now()
                assert after > record.updated_at > before
