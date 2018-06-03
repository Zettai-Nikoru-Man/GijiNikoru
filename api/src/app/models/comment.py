from datetime import datetime
from typing import Optional

from sqlalchemy.dialects.mysql import INTEGER

from src.app.models.dao_base import DAOBase
from src.app.models.shared import db


class Comment(db.Model):
    """コメントの正規情報"""
    id = db.Column(db.String(100), primary_key=True)
    video_id = db.Column(db.String(100), primary_key=True)
    text = db.Column(db.String(300))
    posted_at = db.Column(db.DateTime)
    posted_by = db.Column(db.String(100))
    point = db.Column(db.String(10))
    was_deleted = db.Column(db.Boolean)
    official_nicoru = db.Column(INTEGER(unsigned=True))
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return '<Comment {}>'.format(self.id)


class CommentDAO(DAOBase):
    def add(self,
            id: str,
            video_id: str,
            text: str,
            posted_at: datetime,
            posted_by: str,
            point: str,
            was_deleted: bool,
            official_nicoru: int):
        comment = Comment()
        comment.id = id
        comment.video_id = video_id
        comment.text = text
        comment.posted_at = posted_at
        comment.posted_by = posted_by
        comment.point = point
        comment.was_deleted = was_deleted
        comment.official_nicoru = official_nicoru
        comment.updated_at = datetime.now()
        self.session.add(comment)
        return comment

    def find(self, id: str, video_id: str) -> Optional[Comment]:
        return self.session.query(Comment).filter(
            Comment.id == id,
            Comment.video_id == video_id,
        ).first()
