import time

import schedule

from src.app.batch.db_data_exporter import DBDataExporter
from src.app.batch.dropbox_uploader import DropboxUploader
from src.app.batch.get_incomplete_comment_data import IncompleteCommentDataGetter
from src.app.batch.get_incomplete_video_data import IncompleteVideoDataGetter
from src.app.batch.mail_job_log import JobLogMailer
from src.app.util.gn_logger import GNLogger

logger = GNLogger.get_logger(__name__)


def get_incomplete_video_data():
    try:
        logger.info('job1 start.')
        code = IncompleteVideoDataGetter.execute()
        logger.info('job1 done: {}'.format(code))
    except Exception as e:
        logger.exception(e)


def get_incomplete_comment_data():
    try:
        logger.info('job2 start.')
        code = IncompleteCommentDataGetter.execute()
        logger.info('job2 done: {}'.format(code))
    except Exception as e:
        logger.exception(e)


def export_db_data():
    try:
        DBDataExporter.execute()
    except Exception as e:
        logger.exception(e)


def upload_to_dropbox():
    try:
        DropboxUploader.execute()
    except Exception as e:
        logger.exception(e)


def mail_job_log():
    try:
        JobLogMailer.execute()
        logger.info('job5 done.')
    except Exception as e:
        logger.exception(e)


schedule.every(5).seconds.do(get_incomplete_video_data)
schedule.every(5).seconds.do(get_incomplete_comment_data)
schedule.every().day.at("14:00").do(export_db_data)
schedule.every().day.at("16:00").do(upload_to_dropbox)
schedule.every().day.at("18:00").do(mail_job_log)

while True:
    schedule.run_pending()
    time.sleep(1)
