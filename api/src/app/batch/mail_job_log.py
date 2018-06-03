from typing import List

from flask import Flask
from flask_mail import Message, Mail

from src.app.config.constants import Constants
from src.app.config.hard_constants import HardConstants
from src.app.helpers.db_helper import db_session
from src.app.models.job_log import JobLogDAO
from src.app.models.nicoru import NicoruDAO
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
    def execute(cls):
        cls.mail(Constants.Mail.SENDER, Constants.Mail.RECIPIENTS)

    @classmethod
    def mail(cls, sender: str, recipients: List[str]):
        """send job log mail

        :param sender: sender mail address
        :param recipients: recipients mail addresses
        """
        logger.info('send mail')
        with app.app_context():
            msg = Message(subject="GijiNikoru: Job log",
                          sender=sender,
                          recipients=recipients,
                          attachments=None,
                          body=cls.make_mail_body())

            with app.open_resource(HardConstants.App.DB_DUMP_ZIP) as fp:
                msg.attach(HardConstants.App.DB_DUMP_ZIP_NAME, "application/zip", fp.read())
                mail.send(msg)
            logger.info('sent mail')

    @classmethod
    def make_mail_body(cls) -> str:
        with db_session() as session:
            logs = JobLogDAO(session).list()
            logs_text = "\n".join(["{}: {}({})".format(x.type, x.updated_at, x.status) for x in logs])
            video_progress = NicoruDAO(session).get_status_of_video_data_getting()
            video_progress_text = "got: {}, irregular: {}, all(to get): {}, progress: {}".format(
                video_progress[0],
                video_progress[1],
                video_progress[2],
                video_progress[3])
            comment_progress = NicoruDAO(session).get_status_of_comment_data_getting()
            comment_progress_text = "got: {}, irregular: {}, irregular2: {}, all(to get): {}, progress: {}".format(
                comment_progress[0],
                comment_progress[1],
                comment_progress[2],
                comment_progress[3],
                comment_progress[4])
        return "\n".join([
            "[Job Status]",
            logs_text,
            "",
            "[Progress of video data completion]",
            video_progress_text,
            "",
            "[Progress of comment data completion]",
            comment_progress_text
        ])
