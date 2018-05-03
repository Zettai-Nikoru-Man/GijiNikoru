from datetime import datetime
from typing import Optional

from src.app.models.dao_base import DAOBase
from src.app.models.shared import db


class Video(db.Model):
    """動画の正規情報"""
    id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(300))
    thumbnail = db.Column(db.String(200))
    posted_at = db.Column(db.DateTime)
    length = db.Column(db.String(10))
    watch_url = db.Column(db.String(300))
    posted_by = db.Column(db.String(30))
    posted_by_name = db.Column(db.String(200))
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return '<Video {}>'.format(self.id)


class VideoDAO(DAOBase):
    MODEL = Video

    def add(self,
            id: str,
            title: str,
            thumbnail: str,
            posted_at: datetime,
            length: str,
            watch_url: str,
            posted_by: str,
            posted_by_name: str):
        video = Video()
        video.id = id
        video.title = title
        video.thumbnail = thumbnail
        video.posted_at = posted_at
        video.length = length
        video.watch_url = watch_url
        video.posted_by = posted_by
        video.posted_by_name = posted_by_name
        video.updated_at = datetime.now()
        self.session.add(video)
        return video

    def find(self, id: str) -> Optional[Video]:
        return self.session.query(Video).filter(Video.id == id).first()
