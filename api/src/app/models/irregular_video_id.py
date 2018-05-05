from src.app.models.dao_base import DAOBase
from src.app.models.shared import db


class IrregularVideoId(db.Model):
    """irregular video id"""

    video_id = db.Column(db.String(100), primary_key=True)


class IrregularVideoIdDAO(DAOBase):
    def add(self, video_id: str) -> IrregularVideoId:
        new = IrregularVideoId()
        new.video_id = video_id
        self.session.add(new)
        return new
