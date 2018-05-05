from typing import List, Tuple, Optional

from src.app.helpers.db_helper import db_session
from src.app.models import Video
from src.app.models.nicoru import Nicoru, NicoruDAO, NicoruStatus
from src.app.models.video import VideoDAO
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
            with db_session() as session:
                # setup
                session.query(Nicoru).delete()
                session.commit()
                dao = NicoruDAO(session)
                # run
                stored = dao.get_nicoru_for_video(TestData.VIDEO_ID_1)
                # verify
                assert stored == {}

        def test_found(self):
            with db_session() as session:
                # setup
                session.query(Nicoru).delete()
                session.commit()
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
            with db_session() as session:
                # setup
                session.query(Nicoru).delete()
                session.commit()
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
            with db_session() as session:
                # setup
                session.query(Nicoru).delete()
                session.commit()
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
            with db_session() as session:
                session.query(Nicoru).delete()
                session.query(Video).delete()
                session.commit()

                # insert nicorus
                dao = NicoruDAO(session)
                for vid, cid, is_completed in nicorus:
                    added = dao.nicoru(video_id=vid, comment_id=cid)
                    if is_completed:
                        added.status = NicoruStatus.HAS_REGULAR_COMMENT_DATA

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
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_1, False),
                (TestData.VIDEO_ID_2, TestData.COMMENT_ID_1, False),
                (TestData.VIDEO_ID_2, TestData.COMMENT_ID_2, False),
                (TestData.VIDEO_ID_3, TestData.COMMENT_ID_1, False),
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
            with db_session() as session:
                session.query(Nicoru).delete()
                session.query(Video).delete()
                session.commit()

                dao = NicoruDAO(session)
                for vid in nicorus:
                    dao.nicoru(video_id=vid,
                               comment_id=TestData.COMMENT_ID_1)

                session.commit()

                for vid in completed_video_ids:
                    record = dao.find_by_video_id_and_comment_id(vid, TestData.COMMENT_ID_1)
                    record.status = NicoruStatus.HAS_REGULAR_COMMENT_DATA

                session.commit()

                result = dao.find_incomplete_video_id()
                assert result == expected

        def test_not_found_1(self):
            self.get(nicorus=[
                TestData.VIDEO_ID_1,
            ], completed_video_ids=[
                TestData.VIDEO_ID_1,
            ], expected=None)

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

    class Test_update_status_for_comment:
        def test(self):
            with db_session() as session:
                # setup
                session.query(Nicoru).delete()
                session.commit()

                dao = NicoruDAO(session)
                dao.nicoru(TestData.VIDEO_ID_1, TestData.COMMENT_ID_1)
                dao.nicoru(TestData.VIDEO_ID_1, TestData.COMMENT_ID_2)
                dao.nicoru(TestData.VIDEO_ID_1, TestData.COMMENT_ID_3)
                session.commit()

                # run
                dao.update_status_for_comment(TestData.VIDEO_ID_1,
                                  comment_ids=[TestData.COMMENT_ID_1, TestData.COMMENT_ID_2],
                                  completed_comment_ids=[TestData.COMMENT_ID_1])
                session.commit()

                # verify
                stored = session.query(Nicoru).filter(
                    Nicoru.video_id == TestData.VIDEO_ID_1
                ).order_by(Nicoru.video_id, Nicoru.comment_id).all()  # type: List[Nicoru]
                assert stored[0].video_id == TestData.VIDEO_ID_1
                assert stored[0].comment_id == TestData.COMMENT_ID_1
                assert stored[0].nicoru == 1
                assert stored[0].status == NicoruStatus.HAS_REGULAR_COMMENT_DATA
                assert stored[1].video_id == TestData.VIDEO_ID_1
                assert stored[1].comment_id == TestData.COMMENT_ID_2
                assert stored[1].nicoru == 1
                assert stored[1].status == NicoruStatus.HAS_NO_REGULAR_COMMENT_DATA
                assert stored[2].video_id == TestData.VIDEO_ID_1
                assert stored[2].comment_id == TestData.COMMENT_ID_3
                assert stored[2].nicoru == 1
                assert stored[2].status == NicoruStatus.NEW
