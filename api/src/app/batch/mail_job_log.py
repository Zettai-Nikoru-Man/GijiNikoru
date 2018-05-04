from typing import List, Tuple, Optional

from flask import Flask
from flask_mail import Message, Mail

from src.app.config.constants import Constants
from src.app.helpers.db_helper import db_session
from src.app.models.job_log import JobLogDAO, JobLog, JobLogType
from src.app.util.gn_logger import GNLogger

app = Flask(__name__)
app.config.update(dict(
    DEBUG=False,
    MAIL_SERVER=Constants.Mail.SMTP_SERVER,
    MAIL_PORT=587,
    # MAIL_USE_TLS = True,
    # MAIL_USE_SSL = False,
    MAIL_USERNAME=Constants.Mail.SENDER,
    MAIL_PASSWORD=Constants.Mail.SENDER_PASSWORD,
))
mail = Mail(app)

logger = GNLogger.get_logger(__name__)


class JobLogMailer:
    """Mailer to mail job log status"""

    @classmethod
    def get_job_log(cls) -> Tuple[Optional[JobLog], Optional[JobLog]]:
        """get job log records

        :return: Tuple consists of video and comment job log
        """
        with db_session() as session:
            dao = JobLogDAO(session)
            v = dao.find_by_type(JobLogType.VIDEO)  # 動画ジョブログ取得
            c = dao.find_by_type(JobLogType.COMMENT)  # コメントジョブログ取得
            return v, c

    @classmethod
    def mail(cls, sender: str, recipients: List[str]):
        """send job log mail

        :param sender: sender mail address
        :param recipients: recipients mail addresses
        """
        logger.info('send mail')
        video_job_log, comment_job_log = cls.get_job_log()
        v_status = video_job_log.status if video_job_log else None
        v_updated_at = video_job_log.updated_at if video_job_log else None
        c_status = comment_job_log.status if comment_job_log else None
        c_updated_at = comment_job_log.updated_at if comment_job_log else None

        with app.app_context():
            msg = Message("GijiNikoru: Job log",
                          sender=sender,
                          recipients=recipients,
                          body="\n".join([
                              "Video job log",
                              "  last status: {}".format(v_status),
                              "  last updated at: {}".format(v_updated_at),
                              "Comment job log",
                              "  last status: {}".format(c_status),
                              "  last updated at: {}".format(c_updated_at),
                          ]))
            mail.send(msg)
            logger.info('sent mail')
