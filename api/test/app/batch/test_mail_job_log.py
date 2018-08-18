"""
dc-test /usr/test/app/batch/test_mail_job_log.py
"""
from unittest import mock

from src.app.batch.dropbox_uploader import DropboxUploader
from src.app.batch.mail_job_log import JobLogMailer, mail
from src.app.config.hard_constants import HardConstants
from src.app.models.job_log import JobLogDAO, JobLogStatus, JobLogType
from test.app.db_test_helper import db_test_session
from test.app.models.data import TestDataUtil


class TestJobLogMailer:
    class Test_execute:
        """This send mail to configured address"""

        def test(self):
            with db_test_session() as session:
                with mock.patch.object(mail, 'send', return_value=None):
                    # setup file
                    HardConstants.App = HardConstants.Test
                    TestDataUtil.make_test_file(HardConstants.App.DB_DUMP_ZIP, DropboxUploader.CHUNK_SIZE)

                    # setup DB
                    dao = JobLogDAO(session)
                    dao.add_or_update(JobLogType.VIDEO, JobLogStatus.DONE)
                    dao.add_or_update(JobLogType.COMMENT, JobLogStatus.DONE)
                    session.commit()

                    # run
                    JobLogMailer.execute()
