from src.app.batch.mail_job_log import JobLogMailer
from src.app.models.job_log import JobLogDAO, JobLogStatus, JobLogType
from test.app.db_test_helper import db_test_session


class TestJobLogMailer:
    class Test_execute:
        """This send mail to configured address"""

        def test(self):
            with db_test_session() as session:
                # setup
                dao = JobLogDAO(session)
                dao.add_or_update(JobLogType.VIDEO, JobLogStatus.DONE)
                dao.add_or_update(JobLogType.COMMENT, JobLogStatus.DONE)
                session.commit()

                # run
                JobLogMailer.execute()
