import os

from dropbox import dropbox

from src.app.config.constants import Constants
from src.app.config.hard_constants import HardConstants
from src.app.helpers.db_helper import db_session
from src.app.models.job_log import JobLogType, JobLogStatus, JobLogDAO
from src.app.util.gn_logger import GNLogger

logger = GNLogger.get_logger(__name__)


class DropboxUploader:
    CHUNK_SIZE = 4 * 1024 * 1024  # 4MiB

    @classmethod
    def execute(cls):
        with db_session() as session:
            dao = JobLogDAO(session)
            try:
                dao.add_or_update(JobLogType.UPLOAD_TO_STORAGE, JobLogStatus.RUNNING)
                session.commit()
                cls.upload()
            except Exception as e:
                dao.add_or_update(JobLogType.UPLOAD_TO_STORAGE, JobLogStatus.ABORTED)
                session.commit()
                raise e
            else:
                dao.add_or_update(JobLogType.UPLOAD_TO_STORAGE, JobLogStatus.DONE)

    @classmethod
    def upload(cls):
        dbx = dropbox.Dropbox(Constants.Dropbox.ACCESS_TOKEN)
        file_path = HardConstants.App.DB_DUMP_ZIP
        file_size = os.path.getsize(file_path)
        dest_path = HardConstants.App.DB_DUMP_ZIP_PATH_ON_DROPBOX
        chunk_size = cls.CHUNK_SIZE
        logger.info('file size: {}'.format(file_size))

        with open(file_path, 'rb') as f:
            if file_size <= chunk_size:
                dbx.files_upload(f.read(), dest_path, mode=dropbox.files.WriteMode.overwrite)
                return

            session = dbx.files_upload_session_start(f.read(chunk_size))
            cursor = dropbox.files.UploadSessionCursor(session_id=session.session_id, offset=f.tell())
            commit = dropbox.files.CommitInfo(path=dest_path, mode=dropbox.files.WriteMode.overwrite)
            while f.tell() < file_size:
                if (file_size - f.tell()) <= chunk_size:
                    dbx.files_upload_session_finish(f.read(chunk_size), cursor, commit)
                    return
                dbx.files_upload_session_append_v2(f.read(chunk_size), cursor)
                cursor.offset = f.tell()
