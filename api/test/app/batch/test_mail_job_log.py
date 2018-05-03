from src.app.batch.mail_job_log import JobLogMailer
from src.app.config.constants import Constants
from src.app.helpers.db_helper import db_session
from src.app.models.job_log import JobLogDAO, JobLogStatus, JobLogType


class TestJobLogMailer:
    class Test_get_job_log:
        def test(self):
            with db_session() as session:
                dao = JobLogDAO(session)
                dao.add_or_update(JobLogType.VIDEO, JobLogStatus.DONE)
                dao.add_or_update(JobLogType.COMMENT, JobLogStatus.DONE)
                session.commit()
            result = JobLogMailer.get_job_log()
            assert result[0].type == JobLogType.VIDEO
            assert result[0].status == JobLogStatus.DONE
            assert result[1].type == JobLogType.COMMENT
            assert result[1].status == JobLogStatus.DONE

    class Test_mail:
        """This send mail to configured address"""
        def test(self):
            with db_session() as session:
                dao = JobLogDAO(session)
                dao.add_or_update(JobLogType.VIDEO, JobLogStatus.DONE)
                dao.add_or_update(JobLogType.COMMENT, JobLogStatus.DONE)
                session.commit()
            JobLogMailer.mail(Constants.Mail.SENDER, Constants.Mail.RECIPIENTS)
