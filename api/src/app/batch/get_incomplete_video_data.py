from datetime import datetime
from time import sleep

from src.app.batch.niconico_api_connector import NiconicoAPIConnector, VideoDataGetError
from src.app.helpers.db_helper import db_session
from src.app.models.job_log import JobLogDAO, JobLogStatus, JobLogType
from src.app.models.nicoru import NicoruDAO
from src.app.models.video import VideoDAO
from src.app.util.gn_logger import GNLogger

logger = GNLogger.get_logger(__name__)


class IncompleteVideoDataGetter:
    """Get video info from niconico API"""

    SPAN_SECOND = 10

    class ReturnCode:
        SUCCESS = 0
        PREVIOUS_PROCESS_IS_RUNNING = 1
        NO_INCOMPLETE_DATA = 2
        VIDEO_DATA_NOT_FOUND = 3

    @classmethod
    def execute(cls):
        logger.info('start')
        with db_session() as session:
            try:
                dao = JobLogDAO(session)
                job_log = dao.find_by_type(JobLogType.VIDEO)

                if job_log and job_log.status == JobLogStatus.RUNNING:
                    logger.warning('failed to start. previous process has not done.')
                    return cls.ReturnCode.PREVIOUS_PROCESS_IS_RUNNING

                incomplete_video_id = NicoruDAO(session).find_incomplete_video_id()
                if not incomplete_video_id:
                    logger.info('there is no incomplete video.')
                    return cls.ReturnCode.NO_INCOMPLETE_DATA

                dao.add_or_update(JobLogType.VIDEO, JobLogStatus.RUNNING)
                session.commit()

                # wait to run next process
                if job_log:
                    span = (datetime.now() - job_log.updated_at).seconds
                    if span < cls.SPAN_SECOND:
                        wait = cls.SPAN_SECOND - span
                        logger.debug('waiting {} seconds. span: {}'.format(wait, span))
                        sleep(wait)

                api_connector = NiconicoAPIConnector()
                try:
                    video_info = api_connector.get_video_info(incomplete_video_id)
                    video_api_info = api_connector.get_video_api_info(incomplete_video_id)
                except VideoDataGetError:
                    NicoruDAO(session).delete(incomplete_video_id)
                    raise

                v_dao = VideoDAO(session)
                v_dao.add(
                    id=video_info.video_id,
                    thumbnail=video_info.thumbnail_url,
                    posted_at=video_api_info.posted_at,
                    length=video_info.length,
                    title=video_info.title,
                    watch_url=video_info.watch_url,
                    posted_by=video_info.author_user_id,
                    posted_by_name=video_info.author_nickname,
                )

                dao.add_or_update(JobLogType.VIDEO, JobLogStatus.DONE)
                return cls.ReturnCode.SUCCESS

            except Exception:
                with db_session() as session2:
                    JobLogDAO(session2).add_or_update(JobLogType.VIDEO, JobLogStatus.ABORTED)
                raise
