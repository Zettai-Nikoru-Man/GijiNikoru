from sqlalchemy.orm import Session

from src.app.batch.get_incomplete_data import IncompleteDataGetter
from src.app.batch.niconico_api_connector import NiconicoAPIConnector, VideoDataGetError
from src.app.models.irregular_video_id import IrregularVideoIdDAO
from src.app.models.job_log import JobLogDAO, JobLogStatus, JobLogType
from src.app.models.nicoru import NicoruDAO
from src.app.models.video import VideoDAO
from src.app.util.gn_logger import GNLogger

logger = GNLogger.get_logger(__name__)


class IncompleteVideoDataGetter(IncompleteDataGetter):
    """Get video info from niconico API"""

    TYPE = JobLogType.VIDEO

    @classmethod
    def get_incomplete_data_key(cls, session: Session) -> str:
        incomplete_video_id = NicoruDAO(session).find_incomplete_video_id()
        if not incomplete_video_id:
            raise IncompleteDataGetter.NoIncompleteDataError
        return incomplete_video_id

    @classmethod
    def get_and_register_data(cls, session: Session, incomplete_data_key: str):
        api_connector = NiconicoAPIConnector()
        incomplete_video_id = incomplete_data_key
        try:
            video_info = api_connector.get_video_info(incomplete_video_id)
            video_api_info = api_connector.get_video_api_info(incomplete_video_id)
        except VideoDataGetError:
            IrregularVideoIdDAO(session).add(incomplete_video_id)
            JobLogDAO(session).add_or_update(JobLogType.VIDEO, JobLogStatus.ABORTED)
            session.commit()
            raise

        v_dao = VideoDAO(session)
        if v_dao.find(video_info.video_id):
            # case of "My Memory". e.g. sm1158689 and 1200835239(My Memory of sm1158689)
            # niconico API returns video id(sm1158689) when asking for My Memory id(1200835239).
            # this causes PK error of video table. so here replace returned video id with My Memory video id.
            video_info.video_id = incomplete_video_id

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
