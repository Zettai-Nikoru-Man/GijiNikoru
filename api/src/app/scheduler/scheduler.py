import time

import schedule

from src.app.batch.get_incomplete_comment_data import IncompleteCommentDataGetter
from src.app.batch.get_incomplete_video_data import IncompleteVideoDataGetter
from src.app.batch.mail_job_log import JobLogMailer
from src.app.config.constants import Constants
from src.app.util.gn_logger import GNLogger

logger = GNLogger.get_logger(__name__)


def get_incomplete_video_data():
    try:
        code = IncompleteVideoDataGetter.execute()
        logger.debug('job1 done: {}'.format(code))
    except Exception as e:
        logger.exception(e)


def get_incomplete_comment_data():
    try:
        code = IncompleteCommentDataGetter.execute()
        logger.debug('job2 done: {}'.format(code))
    except Exception as e:
        logger.exception(e)


def mail_job_log():
    try:
        JobLogMailer.mail(Constants.Mail.SENDER, Constants.Mail.RECIPIENTS)
        logger.debug('job3 done.')
    except Exception as e:
        logger.exception(e)


schedule.every(15).seconds.do(get_incomplete_video_data)
schedule.every(15).seconds.do(get_incomplete_comment_data)
schedule.every().day.at("20:00").do(mail_job_log)

while True:
    schedule.run_pending()
    time.sleep(1)
