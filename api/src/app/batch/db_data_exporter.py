import csv
import os
import subprocess

from src.app.config.hard_constants import HardConstants
from src.app.helpers.db_helper import db_session
from src.app.models.job_log import JobLogStatus, JobLogDAO
from src.app.models.job_log import JobLogType
from src.app.models.nicoru import NicoruDAO
from src.app.services.nicoru_service import NicoruService


class DBDataExporter:
    @classmethod
    def execute(cls):
        with db_session() as session:
            dao = JobLogDAO(session)
            try:
                dao.add_or_update(JobLogType.DB_DATA_EXPORT, JobLogStatus.RUNNING)
                session.commit()

                os.makedirs(HardConstants.App.DB_DUMP_DIR, exist_ok=True)
                cls.export_public_data()
                cls.export_data_for_restore()
                cls.compress_exported_data()
            except Exception as e:
                dao.add_or_update(JobLogType.DB_DATA_EXPORT, JobLogStatus.ABORTED)
                session.commit()
                raise e
            else:
                dao.add_or_update(JobLogType.DB_DATA_EXPORT, JobLogStatus.DONE)

    @classmethod
    def export_public_data(cls):
        with db_session() as session:
            dao = NicoruDAO(session)
            records = dao.get_data_for_export()

            with open(HardConstants.App.REPORT_CSV, 'w') as f:
                writer = csv.writer(f, delimiter=",", lineterminator='\n', quotechar='"', quoting=csv.QUOTE_ALL)
                writer.writerow(('動画ID', 'コメ番', 'コメント', '擬似ニコる', '公式ニコる'))
                for record in records:
                    if cls.row_is_valid(record):
                        writer.writerow(record)

    @classmethod
    def export_data_for_restore(cls):
        subprocess.call('{} {}'.format(HardConstants.App.DB_EXPORT_SHELL, HardConstants.App.DB_DUMP_SQL),
                        shell=True)

    @classmethod
    def compress_exported_data(cls):
        subprocess.call('cd {db_dump_dir} && zip -r {db_dump_dir_name}.zip {db_dump_dir_name}'.format(
            db_dump_dir_name=HardConstants.App.DB_DUMP_DIR_NAME,
            db_dump_dir=HardConstants.App.TEMP_DIR), shell=True)

    @classmethod
    def row_is_valid(cls, record):
        vid, cid, _, _, _ = record
        if not NicoruService.video_id_is_valid(vid):
            return False
        if not NicoruService.comment_id_is_valid(cid):
            return False
        return True
