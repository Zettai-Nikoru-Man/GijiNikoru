from typing import Tuple, List

from sqlalchemy.orm import Session

from src.app.batch.get_incomplete_data import IncompleteDataGetter
from src.app.batch.niconico_api_connector import NiconicoAPIConnector, VideoDataGetError, CommentDataGetError
from src.app.models.comment import CommentDAO
from src.app.models.irregular_comment_id import IrregularCommentIdDAO
from src.app.models.irregular_video_id import IrregularVideoIdDAO
from src.app.models.job_log import JobLogType, JobLogDAO, JobLogStatus
from src.app.models.nicoru import NicoruDAO
from src.app.util.gn_logger import GNLogger

logger = GNLogger.get_logger(__name__)


class IncompleteCommentDataGetter(IncompleteDataGetter):
    """Get comment info from niconico API"""

    TYPE = JobLogType.COMMENT

    @classmethod
    def get_incomplete_data_key(cls, session: Session) -> Tuple[str, List[str]]:
        n_dao = NicoruDAO(session)
        video_id, comment_ids = n_dao.find_incomplete_comment_records()
        if not video_id or not comment_ids:
            raise IncompleteDataGetter.NoIncompleteDataError
        return video_id, comment_ids

    @classmethod
    def get_and_register_data(cls, session: Session, incomplete_data_key: Tuple[str, List[str]]):
        target_video_id, target_comment_ids = incomplete_data_key
        api_connector = NiconicoAPIConnector()
        try:
            comments = api_connector.get_comments(target_video_id)
        except VideoDataGetError:
            IrregularVideoIdDAO(session).add(target_video_id)
            JobLogDAO(session).add_or_update(cls.TYPE, JobLogStatus.ABORTED)
            session.commit()
            raise
        except CommentDataGetError:
            IrregularCommentIdDAO(session).add(target_video_id, target_comment_ids)
            JobLogDAO(session).add_or_update(cls.TYPE, JobLogStatus.ABORTED)
            session.commit()
            raise

        completed_comment_ids = []
        for target_comment_id in target_comment_ids:
            for comment in comments.comments:
                if comment.id in completed_comment_ids:
                    # for case that comments has duplicate comments
                    continue
                if comment.id == target_comment_id:
                    CommentDAO(session).add(id=comment.id, video_id=target_video_id, text=comment.text,
                                            posted_at=comment.posted_at, posted_by=comment.posted_by,
                                            point=comment.point, was_deleted=comment.was_deleted,
                                            official_nicoru=comment.official_nicoru)
                    completed_comment_ids.append(comment.id)
                    break
        IrregularCommentIdDAO(session).add(target_video_id,
                                           [x for x in target_comment_ids if x not in completed_comment_ids])
