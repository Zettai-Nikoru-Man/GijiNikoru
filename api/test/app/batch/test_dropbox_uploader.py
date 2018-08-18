"""
dc-test /usr/test/app/batch/test_dropbox_uploader.py
"""
from unittest import mock

import pytest
from dropbox import Dropbox
from dropbox.files import UploadSessionCursor, CommitInfo

from src.app.batch.dropbox_uploader import DropboxUploader
from src.app.config.hard_constants import HardConstants
from src.app.models.job_log import JobLogDAO, JobLogType, JobLogStatus
from test.app.db_test_helper import db_test_session
from test.app.models.data import TestDataUtil


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
        def test_short_file(self):
            with db_test_session() as session:
                # setup
                HardConstants.App = HardConstants.Test
                TestDataUtil.make_test_file(HardConstants.App.DB_DUMP_ZIP, DropboxUploader.CHUNK_SIZE)

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
                HardConstants.App = HardConstants.Test
                TestDataUtil.make_test_file(HardConstants.App.DB_DUMP_ZIP, DropboxUploader.CHUNK_SIZE * 2 + 1)

                # run
                with mock.patch.object(Dropbox, 'files_upload'), \
                     mock.patch.object(Dropbox, 'files_upload_session_start'), \
                     mock.patch.object(Dropbox, 'files_upload_session_append_v2'), \
                     mock.patch.object(Dropbox, 'files_upload_session_finish', return_value=None), \
                     mock.patch.object(CommitInfo, '__init__', return_value=None), \
                     mock.patch.object(UploadSessionCursor, '__init__', return_value=None):
                    DropboxUploader.upload()
