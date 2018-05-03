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


class CommentInfoGetter:
    """Get comment info from niconico API"""

    SPAN_SECOND = 10

    @classmethod
    def execute(cls):
        logger.info('start')
        with db_session() as session:
            try:
                dao = JobLogDAO(session)
                job_log = dao.find_by_type(JobLogType.COMMENT)

                if job_log and job_log.status == JobLogStatus.RUNNING:
                    logger.warning('failed to start. previous process has not done.')
                    return

                incomplete_comment_info = NicoruDAO(session).find_incomplete_comment_info()
                if not incomplete_comment_info:
                    logger.info('there is no incomplete comment.')
                    return

                dao.add_or_update(JobLogType.COMMENT, JobLogStatus.RUNNING)

                # wait to run next process
                if job_log:
                    span = (datetime.now() - job_log.updated_at).seconds
                    if span < cls.SPAN_SECOND:
                        wait = cls.SPAN_SECOND - span
                        logger.debug('waiting {} seconds. span: {}'.format(wait, span))
                        sleep(wait)

                # first, get latest comments
                api_connector = NiconicoAPIConnector()
                video_id = incomplete_comment_info[0][0]
                comments = api_connector.get_comments(video_id)
                completed_comment_ids = []
                for ici in incomplete_comment_info:
                    for comment in comments.comments:
                        if comment.id == ici[1]:
                            CommentDAO(session).add(id=comment.id, video_id=video_id, text=comment.text,
                                                    posted_at=comment.posted_at, posted_by=comment.posted_by,
                                                    point=comment.point, was_deleted=comment.was_deleted,
                                                    original_nicorare=comment.old_nicoru)
                            completed_comment_ids.append(comment.id)
                            break

                additional_try_count = 0
                if len(incomplete_comment_info) != len(completed_comment_ids):
                    # 未取得のコメントがあれば、コメントの投稿ポイント・投稿日をヒントとして、1コメントずつピンポイント検索する
                    for ici in incomplete_comment_info:
                        comment_id = ici[1]
                        if comment_id in completed_comment_ids:
                            continue
                        additional_try_count += 1
                        sleep(cls.SPAN_SECOND)

                        comments = api_connector.get_comments(video_id, commented_at=ici[3], commented_point=ici[2])

                        for comment in comments.comments:
                            for ici2 in incomplete_comment_info:
                                if comment.id in completed_comment_ids:
                                    continue

                                if comment.id == ici2[1]:
                                    CommentDAO(session).add(id=comment.id, video_id=video_id, text=comment.text,
                                                            posted_at=comment.posted_at, posted_by=comment.posted_by,
                                                            point=comment.point, was_deleted=comment.was_deleted,
                                                            original_nicorare=comment.old_nicoru)
                                    completed_comment_ids.append(comment.id)
                                    break

                dao.add_or_update(JobLogType.COMMENT, JobLogStatus.DONE)

            except Exception:
                if session:
                    JobLogDAO(session).add_or_update(JobLogType.COMMENT, JobLogStatus.ABORTED)
                raise


if __name__ == "__main__":
    CommentInfoGetter.execute()
