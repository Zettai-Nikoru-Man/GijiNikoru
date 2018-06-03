from typing import Optional, List, Tuple

from sqlalchemy import text
from sqlalchemy.engine import ResultProxy

from src.app.models.dao_base import DAOBase
from src.app.models.shared import db


class Nicoru(db.Model):
    """擬似ニコる情報"""

    video_id = db.Column(db.String(100), primary_key=True)
    comment_id = db.Column(db.String(100), primary_key=True)
    nicoru = db.Column(db.Integer)

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
LIMIT 1
        """

        FIND_INCOMPLETE_COMMENT_RECORDS = """
SELECT video_id, comment_id
FROM nicoru n2
WHERE video_id = (
  SELECT n.video_id
  FROM nicoru n
  WHERE EXISTS (
    SELECT *
    FROM video v
    WHERE v.id = n.video_id
  )
  AND NOT EXISTS (
    SELECT *
    FROM irregular_video_id ivi
    WHERE ivi.video_id = n.video_id
  )
  AND NOT EXISTS (
    SELECT *
    FROM irregular_comment_id ici
    WHERE ici.video_id = n.video_id
    AND ici.comment_id = n.comment_id
  )
  AND NOT EXISTS (
    SELECT *
    FROM comment c
    WHERE c.video_id = n.video_id
    AND c.id = n.comment_id
  )
  LIMIT 1
)
AND NOT EXISTS (
  SELECT *
  FROM irregular_comment_id ici
  WHERE ici.video_id = n2.video_id
  AND ici.comment_id = n2.comment_id
)
AND NOT EXISTS (
  SELECT *
  FROM comment c
  WHERE c.video_id = n2.video_id
  AND c.id = n2.comment_id
)
        """

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

        GET_DATA_FOR_EXPORT = """
SELECT n.video_id, n.comment_id, c.text, n.nicoru, c.official_nicoru
FROM nicoru n
INNER JOIN comment c
  ON n.video_id = c.video_id
  AND n.comment_id = c.id
WHERE NOT EXISTS (
  SELECT *
  FROM irregular_video_id i
  WHERE n.video_id = i.video_id
)
        """

        GET_STATUS_OF_VIDEO_DATA_GETTING = """
SELECT d.*, concat((d.got + d.irregular) / d.total * 100, '%') as progress FROM (
SELECT
  (SELECT COUNT(*) FROM video) AS got,
  (SELECT COUNT(*) FROM irregular_video_id) AS irregular,
  (SELECT COUNT(*) FROM (SELECT * FROM nicoru GROUP BY video_id) n) AS total
FROM dual) d
        """

        GET_STATUS_OF_COMMENT_DATA_GETTING = """
SELECT d.*, concat((d.got + d.irregular1 + d.irregular2) / d.total * 100, '%') as progress FROM (
SELECT
  (SELECT COUNT(*) FROM comment) AS got,
  (SELECT COUNT(*) FROM nicoru n WHERE n.video_id IN (SELECT video_id FROM irregular_video_id)) AS irregular1,
  (SELECT COUNT(*) FROM irregular_comment_id) AS irregular2,
  (SELECT COUNT(*) FROM nicoru) AS total
FROM dual) d
            """

    def get_nicoru_for_video(self, video_id: str) -> dict:
        records = self.session.query(Nicoru).filter(Nicoru.video_id == video_id).all()  # type: List[Nicoru]
        return {record.comment_id: record.nicoru for record in records}

    def find_by_video_id_and_comment_id(self, video_id: str, comment_id: str) -> Optional[Nicoru]:
        return self.session.query(Nicoru).filter(
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

    def nicoru_from_csv(self, video_id: str, comment_id: str, nicoru: int) -> Nicoru:
        nicoru = int(nicoru)
        stored = self.find_by_video_id_and_comment_id(video_id, comment_id)
        if stored is None:
            new = self.__add(video_id, comment_id)
            new.nicoru = nicoru
            return new
        stored.nicoru += nicoru
        return stored

    def get_data_for_export(self) -> List[Tuple]:
        return self.session.execute(NicoruDAO.Query.GET_DATA_FOR_EXPORT).fetchall()

    def get_nicorareta(self, user_id: str) -> List[tuple]:
        records = self.session.execute(text(NicoruDAO.Query.GET_NICORARETA_DATA),
                                       {'user_id': user_id}).fetchall()  # type: ResultProxy
        if not records:
            return []
        return [tuple(record) for record in records]

    def get_status_of_video_data_getting(self) -> Tuple:
        record = self.session.execute(NicoruDAO.Query.GET_STATUS_OF_VIDEO_DATA_GETTING).fetchone()  # type: ResultProxy
        return tuple(record)

    def get_status_of_comment_data_getting(self) -> Tuple:
        record = self.session.execute(
            NicoruDAO.Query.GET_STATUS_OF_COMMENT_DATA_GETTING).fetchone()  # type: ResultProxy
        return tuple(record)

    def __add(self, video_id: str, comment_id: str) -> Nicoru:
        nicoru = Nicoru()
        nicoru.video_id = video_id
        nicoru.comment_id = comment_id
        nicoru.nicoru = 1
        self.session.add(nicoru)
        return nicoru
