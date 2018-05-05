from datetime import datetime
from time import sleep

from src.app.batch.niconico_api_connector import NiconicoAPIConnector
from src.app.helpers.db_helper import db_session
from src.app.models.comment import CommentDAO
from src.app.models.job_log import JobLogDAO, JobLogStatus, JobLogType
from src.app.models.nicoru import NicoruDAO
from src.app.util.gn_logger import GNLogger

logger = GNLogger.get_logger(__name__)


class ProcessRunningError:
    """Error represents previous process is running"""
    pass


class IncompleteCommentDataGetter:
    """Get comment info from niconico API"""
    SPAN_SECOND = 10

    class ReturnCode:
        SUCCESS = 0
        PREVIOUS_PROCESS_IS_RUNNING = 1
        NO_INCOMPLETE_DATA = 2
        COMMENT_DATA_NOT_FOUND = 3

    @classmethod
    def execute(cls) -> int:
        with db_session() as session:
            try:
                dao = JobLogDAO(session)
                job_log = dao.find_by_type(JobLogType.COMMENT)

                if job_log and job_log.status == JobLogStatus.RUNNING:
                    if (datetime.now() - job_log.updated_at).seconds < 100:
                        return cls.ReturnCode.PREVIOUS_PROCESS_IS_RUNNING
                        # if previous job log is running but old, assume that process was aborted and continue this one.

                n_dao = NicoruDAO(session)
                video_id, comment_ids = n_dao.find_incomplete_comment_records()
                if not video_id or not comment_ids:
                    return cls.ReturnCode.NO_INCOMPLETE_DATA

                dao.add_or_update(JobLogType.COMMENT, JobLogStatus.RUNNING)
                session.commit()

                # wait to run next process
                if job_log:
                    span = (datetime.now() - job_log.updated_at).seconds
                    if span < cls.SPAN_SECOND:
                        wait = cls.SPAN_SECOND - span
                        logger.debug('waiting {} seconds. span: {}'.format(wait, span))
                        sleep(wait)

                # get latest comments
                api_connector = NiconicoAPIConnector()
                comments = api_connector.get_comments(video_id)

                completed_comment_ids = []
                for comment_id in comment_ids:
                    for comment in comments.comments:
                        if comment.id == comment_id:
                            CommentDAO(session).add(id=comment.id, video_id=video_id, text=comment.text,
                                                    posted_at=comment.posted_at, posted_by=comment.posted_by,
                                                    point=comment.point, was_deleted=comment.was_deleted,
                                                    original_nicorare=comment.old_nicoru)
                            completed_comment_ids.append(comment.id)
                            break
                n_dao.update_status_for_comment(video_id, comment_ids, completed_comment_ids)
                session.commit()

                dao.add_or_update(JobLogType.COMMENT, JobLogStatus.DONE)
                session.commit()

                logger.info('added v:{}, c:{}'.format(video_id, completed_comment_ids))
                return cls.ReturnCode.SUCCESS

            except Exception:
                with db_session() as session2:
                    JobLogDAO(session2).add_or_update(JobLogType.COMMENT, JobLogStatus.ABORTED)
                raise
