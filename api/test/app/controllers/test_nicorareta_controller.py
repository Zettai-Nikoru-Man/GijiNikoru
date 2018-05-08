import json

from src.app.controllers.nicorareta_controller import NicoraretaController
from src.app.models.comment import CommentDAO
from src.app.models.nicoru import NicoruDAO
from src.app.models.video import VideoDAO
from test.app.db_test_helper import db_test_session
from test.app.models.data import TestData


class TestNicoraretaController:
    class Test_get:
        def test(self):
            with db_test_session() as session:
                # setup
                dao = NicoruDAO(session)
                dao.nicoru(TestData.VIDEO_ID_1, TestData.COMMENT_ID_1)
                c_dao = CommentDAO(session)
                c_dao.add(
                    id=TestData.COMMENT_ID_1,
                    video_id=TestData.VIDEO_ID_1,
                    text=TestData.Comment.TEXT_1,
                    posted_at=TestData.Comment.POSTED_AT_1,
                    posted_by=TestData.Comment.POSTED_BY_1,
                    point=TestData.Comment.POINT_1,
                    was_deleted=TestData.Comment.WAS_DELETED_1,
                    original_nicorare=TestData.Comment.ORIGINAL_NICORARE_1,
                )
                v_dao = VideoDAO(session)
                v_dao.add(
                    id=TestData.VIDEO_ID_1,
                    title=TestData.Video.TITLE_1,
                    thumbnail=TestData.Video.THUMBNAIL_1,
                    posted_at=TestData.Video.POSTED_AT_1,
                    length=TestData.Video.LENGTH_1,
                    watch_url=TestData.Video.WATCH_URL_1,
                    posted_by=TestData.Video.POSTED_BY_1,
                    posted_by_name=TestData.Video.POSTED_BY_NAME_1,
                )
                session.commit()
                obj = NicoraretaController()
                # run
                result = obj.get(TestData.Comment.POSTED_BY_1)
                result_json = json.loads(result)
                # verify
                assert result_json == [
                    [1, TestData.VIDEO_ID_1, TestData.Comment.TEXT_1,
                     TestData.Comment.POSTED_AT_1.strftime("%Y/%m/%d %H:%M:%S"),
                     TestData.Video.TITLE_1, TestData.Video.THUMBNAIL_1, TestData.Video.WATCH_URL_1]
                ]
