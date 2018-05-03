import enum
from datetime import datetime

from src.app.models.dao_base import DAOBase
from src.app.models.shared import db


class JobLogType(enum.Enum):
    VIDEO = 0
    COMMENT = 1


class JobLogStatus(enum.Enum):
    ABORTED = -1
    RUNNING = 0
    DONE = 1


class JobLog(db.Model):
    """ジョブログ"""
    type = db.Column(db.Enum(JobLogType), primary_key=True)
    status = db.Column(db.Enum(JobLogStatus), nullable=True)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return '<JobLog {} {}>'.format(self.type, self.updated_at)


class JobLogDAO(DAOBase):
    def add_or_update(self, type: JobLogType, status: JobLogStatus):
        """add a record with given values if the table has no record of the type yet. otherwise update it.

        :param type: JobLogType
        :param status: JobLogStatus
        :return: added or updated record
        """
        found = self.find_by_type(type)
        if found:
            found.status = status
            found.updated_at = datetime.now()
            return found
        return self.__add(type, status)

    def find_by_type(self, type: JobLogType) -> JobLog:
        """find record by type

        :param type: JobLogType
        :return: A record has the type or None.
        """
        return self.session.query(JobLog).filter(JobLog.type == type).first()

    def __add(self, type: JobLogType, status: JobLogStatus):
        record = JobLog()
        record.type = type
        record.status = status
        record.updated_at = datetime.now()
        self.session.add(record)
        return record
