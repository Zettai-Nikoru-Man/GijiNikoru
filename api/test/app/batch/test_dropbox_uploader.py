"""
dc-test /usr/test/app/batch/test_dropbox_uploader.py
"""
import os
from os import makedirs
from unittest import mock

import pytest
from dropbox import Dropbox
from dropbox.files import UploadSessionCursor, CommitInfo

from src.app.batch.dropbox_uploader import DropboxUploader
from src.app.config.hard_constants import HardConstants
from src.app.models.job_log import JobLogDAO, JobLogType, JobLogStatus
from test.app.db_test_helper import db_test_session


class TestDropboxUploader:
    class Test_execute:
        def test_success(self):
            with db_test_session() as session:
                # run
                with mock.patch.object(DropboxUploader, 'upload'):
                    DropboxUploader.execute()

                # verify
                assert JobLogDAO(session).find_by_type(JobLogType.UPLOAD_TO_STORAGE).status == JobLogStatus.DONE

        def test_failure(self):
            with db_test_session() as session:
                # run
                with mock.patch.object(DropboxUploader, 'upload', side_effect=Exception):
                    with pytest.raises(Exception):
                        DropboxUploader.execute()

                # verify
                assert JobLogDAO(session).find_by_type(JobLogType.UPLOAD_TO_STORAGE).status == JobLogStatus.ABORTED

    class Test_upload:
        @staticmethod
        def make_test_file(path: str, size: int):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write('1' * size)

        def test_short_file(self):
            with db_test_session() as session:
                # setup
                test_zip_path = HardConstants.App.TEST_ASSET_DIR + '/test'
                self.make_test_file(test_zip_path, DropboxUploader.CHUNK_SIZE)
                HardConstants.App.DB_DUMP_ZIP = test_zip_path

                # run
                with mock.patch.object(Dropbox, 'files_upload'), \
                     mock.patch.object(Dropbox, 'files_upload_session_start'), \
                     mock.patch.object(Dropbox, 'files_upload_session_append_v2'), \
                     mock.patch.object(Dropbox, 'files_upload_session_finish', return_value=None), \
                     mock.patch.object(CommitInfo, '__init__', return_value=None), \
                     mock.patch.object(UploadSessionCursor, '__init__', return_value=None):
                    DropboxUploader.upload()

        def test_long_file(self):
            with db_test_session() as session:
                # setup
                test_zip_path = HardConstants.App.TEST_ASSET_DIR + '/test'
                self.make_test_file(test_zip_path, DropboxUploader.CHUNK_SIZE * 2 + 1)
                HardConstants.App.DB_DUMP_ZIP = test_zip_path

                # run
                with mock.patch.object(Dropbox, 'files_upload'), \
                     mock.patch.object(Dropbox, 'files_upload_session_start'), \
                     mock.patch.object(Dropbox, 'files_upload_session_append_v2'), \
                     mock.patch.object(Dropbox, 'files_upload_session_finish', return_value=None), \
                     mock.patch.object(CommitInfo, '__init__', return_value=None), \
                     mock.patch.object(UploadSessionCursor, '__init__', return_value=None):
                    DropboxUploader.upload()
