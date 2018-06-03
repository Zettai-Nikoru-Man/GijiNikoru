from typing import List

from src.app.models.dao_base import DAOBase
from src.app.models.shared import db


class IrregularCommentId(db.Model):
    """irregular (could not get regular data of it) comment id"""

    video_id = db.Column(db.String(100), primary_key=True)
    comment_id = db.Column(db.String(100), primary_key=True)


class IrregularCommentIdDAO(DAOBase):
    def add(self, video_id: str, comment_ids: List[str]):
        for comment_id in comment_ids:
            new = IrregularCommentId()
            new.video_id = video_id
            new.comment_id = comment_id
            self.session.add(new)
