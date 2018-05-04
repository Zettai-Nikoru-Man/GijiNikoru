from enum import Enum
from typing import Optional, List, Tuple

from src.app.models.dao_base import DAOBase
from src.app.models.shared import db


class Nicoru(db.Model):
    """擬似ニコる情報"""

    class Status(Enum):
        NEW = 0
        HAS_REGULAR_COMMENT_DATA = 1
        HAS_NO_REGULAR_COMMENT_DATA = -1

    video_id = db.Column(db.String(100), primary_key=True)
    comment_id = db.Column(db.String(100), primary_key=True)
    nicoru = db.Column(db.Integer)
    status = db.Column(db.SmallInteger)

    def __repr__(self):
        return '<Nicoru {}-{}>'.format(self.video_id, self.comment_id)


class NicoruDAO(DAOBase):
    class Query:
        FIND_INCOMPLETE_COMMENT_RECORDS = """
SELECT n2.video_id, n2.comment_id
FROM nicoru n2
INNER JOIN (
  SELECT n.video_id, COUNT(1) AS cnt
  FROM nicoru n
  INNER JOIN video v
    ON n.video_id = v.id
  WHERE n.status = {}
  GROUP BY n.video_id
  ORDER BY cnt DESC
  LIMIT 1) s
ON n2.video_id = s.video_id
        """.format(Nicoru.Status.NEW.value)

    def get_nicoru_for_video(self, video_id: str) -> dict:
        records = self.session.query(Nicoru).filter(Nicoru.video_id == video_id).all()  # type: List[Nicoru]
        return {record.comment_id: record.nicoru for record in records}

    def find_by_video_id_and_comment_id(self, video_id: str, comment_id: str) -> Optional[Nicoru]:
        return self.session.query(Nicoru).filter(
            Nicoru.video_id == video_id,
            Nicoru.comment_id == comment_id
        ).first()

    def find_incomplete_video_id(self) -> Optional[str]:
        stored = self.session.query(Nicoru).filter(Nicoru.status == Nicoru.Status.NEW.value).first()
        return stored.video_id if stored else None

    def find_incomplete_comment_records(self) -> Tuple[Optional[str], Optional[List[str]]]:
        records = self.session.execute(NicoruDAO.Query.FIND_INCOMPLETE_COMMENT_RECORDS).fetchall()
        if not records:
            return None, None
        return records[0][0], [cid for vid, cid in records]

    def nicoru(self, video_id: str, comment_id: str) -> Nicoru:
        stored = self.find_by_video_id_and_comment_id(video_id, comment_id)
        if stored is None:
            return self.__add(video_id, comment_id)
        stored.nicoru += 1
        return stored

    def update_status(self, video_id: str, comment_ids: List[str], completed_comment_ids: List[str]):
        nicorus = self.session.query(Nicoru).filter(
            Nicoru.video_id == video_id,
            Nicoru.comment_id.in_(comment_ids)).all()

        for nicoru in nicorus:
            if nicoru.comment_id in completed_comment_ids:
                nicoru.status = Nicoru.Status.HAS_REGULAR_COMMENT_DATA.value
            else:
                nicoru.status = Nicoru.Status.HAS_NO_REGULAR_COMMENT_DATA.value

    def delete(self, video_id: str):
        """delete records seems to be illegal"""
        self.session.query(Nicoru.comment_id, Nicoru.nicoru).filter(Nicoru.video_id == video_id).delete()

    def __add(self, video_id: str, comment_id: str) -> Nicoru:
        nicoru = Nicoru()
        nicoru.video_id = video_id
        nicoru.comment_id = comment_id
        nicoru.nicoru = 1
        nicoru.status = Nicoru.Status.NEW.value
        self.session.add(nicoru)
        return nicoru
