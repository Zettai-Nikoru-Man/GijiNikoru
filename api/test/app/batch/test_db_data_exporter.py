import pytest

from src.app.batch.db_data_exporter import DBDataExporter
from src.app.config.hard_constants import HardConstants
from src.app.models.comment import CommentDAO
from src.app.models.job_log import JobLogDAO, JobLogType, JobLogStatus
from src.app.models.nicoru import NicoruDAO
from test.app.db_test_helper import db_test_session
from test.app.models.data import TestData


class TestDBDataExporter:
    class Test_execute:
        def test_success(self):
            with db_test_session() as session:
                # setup
                NicoruDAO(session).nicoru(TestData.VIDEO_ID_1, TestData.COMMENT_ID_1)
                CommentDAO(session).add(
                    id=TestData.COMMENT_ID_1,
                    video_id=TestData.VIDEO_ID_1,
                    text=TestData.Comment.TEXT_1,
                    posted_at=TestData.Comment.POSTED_AT_1,
                    posted_by=TestData.Comment.POSTED_BY_1,
                    point=TestData.Comment.POINT_1,
                    was_deleted=TestData.Comment.WAS_DELETED_1,
                    official_nicoru=TestData.Comment.OFFICIAL_NICORU_1,
                )
                session.commit()
                # run
                DBDataExporter.execute()
                # verify
                with open(HardConstants.App.REPORT_CSV, 'r') as f:
                    assert f.readlines() == [
                        '"動画ID","コメ番","コメント","擬似ニコる","公式ニコる"\n',
                        '"{vid}","{cid}","{c}","1","{o_n}"\n'.format(
                            vid=TestData.VIDEO_ID_1,
                            cid=TestData.COMMENT_ID_1,
                            c=TestData.Comment.TEXT_1,
                            o_n=TestData.Comment.OFFICIAL_NICORU_1),
                    ]
                assert JobLogDAO(session).find_by_type(JobLogType.DB_DATA_EXPORT).status == JobLogStatus.DONE

        def test_failure(self):
            with db_test_session() as session:
                # setup
                DBDataExporter.compress_exported_data = lambda: 1 / 0

                # run
                with pytest.raises(Exception):
                    DBDataExporter.execute()

                # verify
                assert JobLogDAO(session).find_by_type(JobLogType.DB_DATA_EXPORT).status == JobLogStatus.ABORTED

    class Test_row_is_valid:
        def test_valid(self):
            assert DBDataExporter.row_is_valid((TestData.VIDEO_ID_1, TestData.COMMENT_ID_1, 0, 0, 0))

        def test_invalid_vid(self):
            assert not DBDataExporter.row_is_valid((TestData.VIDEO_ID_1, '', 0, 0, 0))

        def test_invalid_cid(self):
            assert not DBDataExporter.row_is_valid(('', TestData.COMMENT_ID_1, 0, 0, 0))
