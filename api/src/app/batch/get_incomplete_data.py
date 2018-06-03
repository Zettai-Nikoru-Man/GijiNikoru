from datetime import datetime
from time import sleep

from sqlalchemy.orm import Session

from src.app.helpers.db_helper import db_session
from src.app.models.job_log import JobLogDAO, JobLogStatus, JobLogType, JobLog
from src.app.util.gn_logger import GNLogger

logger = GNLogger.get_logger(__name__)


class IncompleteDataGetter:
    """Get info from niconico API"""

    class NoIncompleteDataError(Exception):
        pass

    SPAN_SECOND = 10

    class ReturnCode:
        SUCCESS = 0
        PREVIOUS_PROCESS_IS_RUNNING = 1
        NO_INCOMPLETE_DATA = 2
        DATA_NOT_FOUND = 3

    TYPE = None  # type: JobLogType

    @classmethod
    def previous_process_is_running(cls, job_log: JobLog):
        if job_log and job_log.status == JobLogStatus.RUNNING:
            if (datetime.now() - job_log.updated_at).seconds < 100:
                return True
        # if previous job log is running but old, assume that process was aborted and continue this one.
        return False

    @classmethod
    def wait_to_run_next_process(cls, job_log: JobLog):
        if job_log:
            span = (datetime.now() - job_log.updated_at).seconds
            if span < cls.SPAN_SECOND:
                wait = cls.SPAN_SECOND - span
                logger.debug('waiting {} seconds. span: {}'.format(wait, span))
                sleep(wait)

    @classmethod
    def get_incomplete_data_key(cls, session: Session):
        raise NotImplementedError

    @classmethod
    def get_and_register_data(cls, session: Session, incomplete_data_key):
        raise NotImplementedError

    @classmethod
    def execute(cls) -> int:
        with db_session() as session:
            try:
                job_log_dao = JobLogDAO(session)
                job_log = job_log_dao.find_by_type(cls.TYPE)

                # exit if previous process is running
                if cls.previous_process_is_running(job_log):
                    return cls.ReturnCode.PREVIOUS_PROCESS_IS_RUNNING

                try:
                    incomplete_data_key = cls.get_incomplete_data_key(session)
                except IncompleteDataGetter.NoIncompleteDataError:
                    # exit if there is no data to get
                    logger.debug('there is no data to get.')
                    return cls.ReturnCode.NO_INCOMPLETE_DATA

                # wait to run next process
                cls.wait_to_run_next_process(job_log)

                # mark the job as running
                job_log_dao.add_or_update(cls.TYPE, JobLogStatus.RUNNING)
                session.commit()

                # get and register data
                cls.get_and_register_data(session, incomplete_data_key)
                session.commit()

                # mark the job as running
                job_log_dao.add_or_update(cls.TYPE, JobLogStatus.DONE)
                session.commit()

                return cls.ReturnCode.SUCCESS

            except Exception:
                if session:
                    session.rollback()
                with db_session() as session_for_error:
                    # mark the job as aborted
                    JobLogDAO(session_for_error).add_or_update(cls.TYPE, JobLogStatus.ABORTED)
                    session_for_error.commit()
                raise
