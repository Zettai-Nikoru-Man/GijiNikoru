import enum
from typing import Optional, List, Tuple

from sqlalchemy import text
from sqlalchemy.engine import ResultProxy

from src.app.models.dao_base import DAOBase
from src.app.models.shared import db


class NicoruStatus(enum.Enum):
    NEW = 0
    HAS_REGULAR_COMMENT_DATA = 1
    HAS_NO_REGULAR_COMMENT_DATA = -1


class Nicoru(db.Model):
    """擬似ニコる情報"""

    video_id = db.Column(db.String(100), primary_key=True)
    comment_id = db.Column(db.String(100), primary_key=True)
    nicoru = db.Column(db.Integer)
    status = db.Column(db.Enum(NicoruStatus), nullable=False)

    def __repr__(self):
        return '<Nicoru {}-{}>'.format(self.video_id, self.comment_id)


class NicoruDAO(DAOBase):
    class Query:
        FIND_INCOMPLETE_VIDEO_IDS = """
SELECT n.video_id
FROM nicoru n
WHERE NOT EXISTS (
  SELECT *
  FROM irregular_video_id ivi
  WHERE video_id = n.video_id
)
AND NOT EXISTS (
  SELECT *
  FROM video v
  WHERE v.id = n.video_id
)
        """
        FIND_INCOMPLETE_COMMENT_RECORDS = """
SELECT n.video_id, n.comment_id
FROM nicoru n
WHERE n.status = '{}'
AND EXISTS (
  SELECT *
  FROM video v
  WHERE v.id = n.video_id
)
        """.format(NicoruStatus.NEW.name)

        GET_NICORARETA_DATA = """
SELECT
  n.nicoru,
  n.video_id,
  c.text,
  DATE_FORMAT(c.posted_at, '%Y/%m/%d %H:%i:%s'),
  v.title,
  v.thumbnail,
  v.watch_url
FROM nicoru n
INNER JOIN comment c
  ON n.video_id = c.video_id
  AND n.comment_id = c.id
INNER JOIN video v
  ON n.video_id = v.id
WHERE c.posted_by = :user_id
ORDER BY
  c.posted_at DESC
        """

    def get_nicoru_for_video(self, video_id: str) -> dict:
        records = self.session.query(Nicoru).filter(Nicoru.video_id == video_id).all()  # type: List[Nicoru]
        return {record.comment_id: record.nicoru for record in records}

    def find_by_video_id_and_comment_id(self, video_id: str, comment_id: str) -> Optional[Nicoru]:
        return self.session.query(Nicoru).with_lockmode('update').filter(
            Nicoru.video_id == video_id,
            Nicoru.comment_id == comment_id
        ).first()

    def find_incomplete_video_id(self) -> Optional[str]:
        stored = self.session.execute(NicoruDAO.Query.FIND_INCOMPLETE_VIDEO_IDS).fetchone()
        return stored[0] if stored else None

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

    def update_status_for_comment(self, video_id: str, comment_ids: List[str], completed_comment_ids: List[str]):
        nicorus = self.session.query(Nicoru).filter(
            Nicoru.video_id == video_id,
            Nicoru.comment_id.in_(comment_ids)).all()

        for nicoru in nicorus:
            if nicoru.comment_id in completed_comment_ids:
                nicoru.status = NicoruStatus.HAS_REGULAR_COMMENT_DATA
            else:
                nicoru.status = NicoruStatus.HAS_NO_REGULAR_COMMENT_DATA

    def get_nicorareta(self, user_id: str) -> List[tuple]:
        records = self.session.execute(text(NicoruDAO.Query.GET_NICORARETA_DATA),
                                       {'user_id': user_id}).fetchall()  # type: ResultProxy
        if not records:
            return []
        return [tuple(record) for record in records]

    def __add(self, video_id: str, comment_id: str) -> Nicoru:
        nicoru = Nicoru()
        nicoru.video_id = video_id
        nicoru.comment_id = comment_id
        nicoru.nicoru = 1
        nicoru.status = NicoruStatus.NEW
        self.session.add(nicoru)
        return nicoru
