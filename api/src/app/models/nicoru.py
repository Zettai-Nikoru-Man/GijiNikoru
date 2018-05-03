from typing import Optional

from src.app.models.dao_base import DAOBase
from src.app.models.shared import db


class Nicoru(db.Model):
    """擬似ニコる情報"""
    video_id = db.Column(db.String(100), primary_key=True)
    comment_id = db.Column(db.String(100), primary_key=True)
    nikorare = db.Column(db.Integer)
    commented_at = db.Column(db.String(20))
    commented_point = db.Column(db.String(10))

    def __repr__(self):
        return '<Nicoru {}-{}>'.format(self.video_id, self.comment_id)


class NicoruDAO(DAOBase):
    QUERY_GET_INCOMPLETE_VIDEO_INFO = """
SELECT
  video_id
FROM
  nicoru n
WHERE NOT EXISTS (
  SELECT
    *
  FROM
    video v
  WHERE
    v.id = n.video_id
)
    """

    QUERY_GET_INCOMPLETE_COMMENT_INFO = """
SELECT
  n.video_id,
  n.comment_id,
  n.commented_point,
  n.commented_at
FROM
  nicoru n
  INNER JOIN
  (
    SELECT
      video_id AS video_id,
      count(1)      AS cnt
    FROM
      (
        SELECT
          n.video_id   AS video_id,
          n.comment_id AS comment_id
        FROM nicoru n
        WHERE NOT EXISTS(
            SELECT *
            FROM comment c
            WHERE c.video_id = n.video_id
                  AND c.id = n.comment_id
        )
      ) incomplete_comment_info
    GROUP BY incomplete_comment_info.video_id
    ORDER BY cnt DESC
    LIMIT 1
  ) incomplete_comment_info_max
    ON n.video_id = incomplete_comment_info_max.video_id
WHERE NOT EXISTS(
    SELECT *
    FROM comment c
    WHERE c.video_id = n.video_id
    AND c.id = n.comment_id)
ORDER BY commented_at DESC;
    """

    def find_by_video_id(self, video_id: str) -> dict:
        nikorare = self.session.query(Nicoru.comment_id, Nicoru.nikorare).filter(Nicoru.video_id == video_id).all()
        return {c: n for c, n in nikorare}

    def find_by_video_id_and_comment_id(self, video_id: str, comment_id: str) -> Optional[Nicoru]:
        return self.session.query(Nicoru).filter(
            Nicoru.video_id == video_id,
            Nicoru.comment_id == comment_id
        ).first()

    def find_incomplete_video_id(self) -> Optional[str]:
        video_id = self.session.execute(self.QUERY_GET_INCOMPLETE_VIDEO_INFO).fetchone()
        return video_id[0] if video_id else None

    def find_incomplete_comment_info(self):
        return self.session.execute(self.QUERY_GET_INCOMPLETE_COMMENT_INFO).fetchall()

    def add_or_update(self, video_id: str, comment_id: str, commented_at: str, commented_point: str) -> Nicoru:
        nicoru = self.find_by_video_id_and_comment_id(video_id, comment_id)
        if nicoru is None:
            return self.__add(video_id, comment_id, commented_at, commented_point)
        nicoru.commented_at = commented_at
        nicoru.commented_point = commented_point
        nicoru.nikorare += 1
        return nicoru

    def __add(self, video_id: str, comment_id: str, commented_at: str, commented_point: str) -> Nicoru:
        nicoru = Nicoru()
        nicoru.video_id = video_id
        nicoru.comment_id = comment_id
        nicoru.commented_at = commented_at
        nicoru.commented_point = commented_point
        nicoru.nikorare = 1
        self.session.add(nicoru)
        return nicoru
