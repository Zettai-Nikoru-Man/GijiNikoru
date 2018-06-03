from typing import List, Tuple, Optional

from src.app.models.comment import CommentDAO
from src.app.models.nicoru import Nicoru, NicoruDAO
from src.app.models.video import VideoDAO
from test.app.db_test_helper import db_test_session
from test.app.models.data import TestData


class TestNicoru:
    class Test___repr__:
        def test(self):
            record = Nicoru()
            record.video_id = TestData.VIDEO_ID_1
            record.comment_id = TestData.COMMENT_ID_1
            record.nicoru = 1
            assert str(record) == '<Nicoru {}-{}>'.format(record.video_id, record.comment_id)


class TestNicoruDAO:
    class Test_get_nicoru_for_video:
        def test_not_found(self):
            with db_test_session() as session:
                # setup
                dao = NicoruDAO(session)
                # run
                stored = dao.get_nicoru_for_video(TestData.VIDEO_ID_1)
                # verify
                assert stored == {}

        def test_found(self):
            with db_test_session() as session:
                # setup
                dao = NicoruDAO(session)
                dao.nicoru(video_id=TestData.VIDEO_ID_1,
                           comment_id=TestData.COMMENT_ID_1)
                session.commit()
                # run
                stored = dao.get_nicoru_for_video(TestData.VIDEO_ID_1)
                # verify
                assert stored == {TestData.COMMENT_ID_1: 1}

    class Test_nicoru:
        def test_add(self):
            with db_test_session() as session:
                # setup
                dao = NicoruDAO(session)
                # run
                new = dao.nicoru(video_id=TestData.VIDEO_ID_1,
                                 comment_id=TestData.COMMENT_ID_1)
                session.commit()
                # verify
                assert new.video_id == TestData.VIDEO_ID_1
                assert new.comment_id == TestData.COMMENT_ID_1
                assert new.nicoru == 1
                stored = dao.find_by_video_id_and_comment_id(video_id=TestData.VIDEO_ID_1,
                                                             comment_id=TestData.COMMENT_ID_1)
                assert stored.video_id == TestData.VIDEO_ID_1
                assert stored.comment_id == TestData.COMMENT_ID_1
                assert stored.nicoru == 1

        def test_update(self):
            with db_test_session() as session:
                # setup
                dao = NicoruDAO(session)
                dao.nicoru(video_id=TestData.VIDEO_ID_1,
                           comment_id=TestData.COMMENT_ID_1)
                session.commit()
                # run
                updated = dao.nicoru(video_id=TestData.VIDEO_ID_1,
                                     comment_id=TestData.COMMENT_ID_1)
                # verify
                assert updated.video_id == TestData.VIDEO_ID_1
                assert updated.comment_id == TestData.COMMENT_ID_1
                assert updated.nicoru == 2
                stored = dao.find_by_video_id_and_comment_id(video_id=TestData.VIDEO_ID_1,
                                                             comment_id=TestData.COMMENT_ID_1)
                assert stored.video_id == TestData.VIDEO_ID_1
                assert stored.comment_id == TestData.COMMENT_ID_1
                assert stored.nicoru == 2

    class Test_find_incomplete_comment_records:
        """
        * We will get TR(target record)
        * TR are 0 or one or more nicoru records.
        * TR's video has more incomplete comments than other nicoru records.
        """

        def get(self, nicorus: List[Tuple], videos: List[str], expected: Tuple[Optional[str], Optional[List[str]]]):
            with db_test_session() as session:
                # insert nicorus
                dao = NicoruDAO(session)
                c_dao = CommentDAO(session)
                for vid, cid, is_completed in nicorus:
                    dao.nicoru(video_id=vid, comment_id=cid)
                    if is_completed:
                        c_dao.add(
                            id=cid,
                            video_id=vid,
                            text=TestData.Comment.TEXT_1,
                            posted_at=TestData.Comment.POSTED_AT_1,
                            posted_by=TestData.Comment.POSTED_BY_1,
                            point=TestData.Comment.POINT_1,
                            was_deleted=TestData.Comment.WAS_DELETED_1,
                            official_nicoru=TestData.Comment.OFFICIAL_NICORU_1,
                        )
                session.commit()

                # insert comments
                v_dao = VideoDAO(session)
                for vid in videos:
                    v_dao.add(
                        id=vid,
                        title=TestData.Video.TITLE_1,
                        thumbnail=TestData.Video.THUMBNAIL_1,
                        posted_at=TestData.Video.POSTED_AT_1,
                        length=TestData.Video.LENGTH_1,
                        watch_url=TestData.Video.WATCH_URL_1,
                        posted_by=TestData.Video.POSTED_BY_1,
                        posted_by_name=TestData.Video.POSTED_BY_NAME_1,
                    )

                session.commit()
                assert dao.find_incomplete_comment_records() == expected

        def test_not_found_1(self):
            self.get(nicorus=[
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_1, True),
            ], videos=[
                TestData.VIDEO_ID_1,
            ], expected=(None, None))  # video 1 has nicoru and video data and comment data

        def test_not_found_2(self):
            self.get(nicorus=[
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_1, True),
                (TestData.VIDEO_ID_2, TestData.COMMENT_ID_1, False),
                (TestData.VIDEO_ID_2, TestData.COMMENT_ID_2, False),
                (TestData.VIDEO_ID_3, TestData.COMMENT_ID_1, True),
            ], videos=[
                TestData.VIDEO_ID_1,
            ], expected=(None, None))  # video 2 has nicoru but doesn't have video data

        def test_found_1(self):
            self.get(nicorus=[
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_1, True),
                (TestData.VIDEO_ID_2, TestData.COMMENT_ID_1, False),
                (TestData.VIDEO_ID_2, TestData.COMMENT_ID_2, False),
            ], videos=[
                TestData.VIDEO_ID_1,
                TestData.VIDEO_ID_2,
            ], expected=(TestData.VIDEO_ID_2, [  # video 2 has nicoru and video data and doesn't have comment data
                TestData.COMMENT_ID_1,
                TestData.COMMENT_ID_2,
            ]))

    class Test_find_incomplete_video_id:
        """
        * We will get TR(target record)
        * TR are 0 or one or more video ids.
        * TR's video is incomplete.
        """

        def get(self, nicorus: List[str], completed_video_ids: List[str], expected: Optional[str]):
            with db_test_session() as session:
                # setup
                dao = NicoruDAO(session)
                for vid in nicorus:
                    dao.nicoru(video_id=vid,
                               comment_id=TestData.COMMENT_ID_1)
                session.commit()

                # add videos
                v_dao = VideoDAO(session)
                for vid in completed_video_ids:
                    v_dao.add(
                        id=vid,
                        title=TestData.Video.TITLE_1,
                        thumbnail=TestData.Video.THUMBNAIL_1,
                        posted_at=TestData.Video.POSTED_AT_1,
                        length=TestData.Video.LENGTH_1,
                        watch_url=TestData.Video.WATCH_URL_1,
                        posted_by=TestData.Video.POSTED_BY_1,
                        posted_by_name=TestData.Video.POSTED_BY_NAME_1,
                    )
                session.commit()

                # run
                result = dao.find_incomplete_video_id()
                # verify
                assert result == expected

        def test_not_found_1(self):
            self.get(nicorus=[
                TestData.VIDEO_ID_1,
            ], completed_video_ids=[
                TestData.VIDEO_ID_1,
            ], expected=None)  # all nicoru video is completed

        def test_not_found_2(self):
            self.get(nicorus=[
                TestData.VIDEO_ID_1,
                TestData.VIDEO_ID_2,
            ], completed_video_ids=[
                TestData.VIDEO_ID_1,
                TestData.VIDEO_ID_2,
            ], expected=None)

        def test_found_1(self):
            self.get(nicorus=[
                TestData.VIDEO_ID_1,
            ], completed_video_ids=[
            ], expected=TestData.VIDEO_ID_1)

    class Test_get_nicorareta:
        def test_found(self):
            with db_test_session() as session:
                # setup
                dao = NicoruDAO(session)
                dao.nicoru(TestData.VIDEO_ID_1, TestData.COMMENT_ID_1)  # v1, c1, 1 nicoru
                dao.nicoru(TestData.VIDEO_ID_1, TestData.COMMENT_ID_2)
                session.commit()
                dao.nicoru(TestData.VIDEO_ID_1, TestData.COMMENT_ID_2)  # v1, c2, 2 nicoru
                dao.nicoru(TestData.VIDEO_ID_2, TestData.COMMENT_ID_1)  # v2, c1, 1 nicoru
                c_dao = CommentDAO(session)
                c_dao.add(  # v1, c1
                    id=TestData.COMMENT_ID_1,
                    video_id=TestData.VIDEO_ID_1,
                    text=TestData.Comment.TEXT_1,
                    posted_at=TestData.Comment.POSTED_AT_1,
                    posted_by=TestData.Comment.POSTED_BY_1,
                    point=TestData.Comment.POINT_1,
                    was_deleted=TestData.Comment.WAS_DELETED_1,
                    official_nicoru=TestData.Comment.OFFICIAL_NICORU_1,
                )
                c_dao.add(  # v1, c2
                    id=TestData.COMMENT_ID_2,
                    video_id=TestData.VIDEO_ID_1,
                    text=TestData.Comment.TEXT_2,
                    posted_at=TestData.Comment.POSTED_AT_2,
                    posted_by=TestData.Comment.POSTED_BY_1,
                    point=TestData.Comment.POINT_1,
                    was_deleted=TestData.Comment.WAS_DELETED_1,
                    official_nicoru=TestData.Comment.OFFICIAL_NICORU_1,
                )
                c_dao.add(  # v1, c3
                    id=TestData.COMMENT_ID_3,
                    video_id=TestData.VIDEO_ID_1,
                    text=TestData.Comment.TEXT_2,
                    posted_at=TestData.Comment.POSTED_AT_3,
                    posted_by=TestData.Comment.POSTED_BY_1,
                    point=TestData.Comment.POINT_1,
                    was_deleted=TestData.Comment.WAS_DELETED_1,
                    official_nicoru=TestData.Comment.OFFICIAL_NICORU_1,
                )
                c_dao.add(  # v2, c1
                    id=TestData.COMMENT_ID_1,
                    video_id=TestData.VIDEO_ID_2,
                    text=TestData.Comment.TEXT_1,
                    posted_at=TestData.Comment.POSTED_AT_3,
                    posted_by=TestData.Comment.POSTED_BY_1,
                    point=TestData.Comment.POINT_1,
                    was_deleted=TestData.Comment.WAS_DELETED_1,
                    official_nicoru=TestData.Comment.OFFICIAL_NICORU_1,
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
                v_dao.add(
                    id=TestData.VIDEO_ID_2,
                    title=TestData.Video.TITLE_2,
                    thumbnail=TestData.Video.THUMBNAIL_2,
                    posted_at=TestData.Video.POSTED_AT_1,
                    length=TestData.Video.LENGTH_1,
                    watch_url=TestData.Video.WATCH_URL_2,
                    posted_by=TestData.Video.POSTED_BY_1,
                    posted_by_name=TestData.Video.POSTED_BY_NAME_1,
                )
                session.commit()
                # run
                data = dao.get_nicorareta(TestData.Comment.POSTED_BY_1)
                # verify
                assert data == [
                    (1, TestData.VIDEO_ID_2, TestData.Comment.TEXT_1,
                     TestData.Comment.POSTED_AT_3.strftime("%Y/%m/%d %H:%M:%S"),
                     TestData.Video.TITLE_2, TestData.Video.THUMBNAIL_2, TestData.Video.WATCH_URL_2),  # v2, c1
                    (2, TestData.VIDEO_ID_1, TestData.Comment.TEXT_2,
                     TestData.Comment.POSTED_AT_2.strftime("%Y/%m/%d %H:%M:%S"),
                     TestData.Video.TITLE_1, TestData.Video.THUMBNAIL_1, TestData.Video.WATCH_URL_1),  # v1, c2
                    (1, TestData.VIDEO_ID_1, TestData.Comment.TEXT_1,
                     TestData.Comment.POSTED_AT_1.strftime("%Y/%m/%d %H:%M:%S"),
                     TestData.Video.TITLE_1, TestData.Video.THUMBNAIL_1, TestData.Video.WATCH_URL_1),  # v1, c1
                ]

        def test_not_found(self):
            with db_test_session() as session:
                # setup
                dao = NicoruDAO(session)
                # run
                data = dao.get_nicorareta(TestData.Comment.POSTED_BY_1)
                # verify
                assert data == []
