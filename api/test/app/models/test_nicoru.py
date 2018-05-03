from typing import List, Tuple

from src.app.helpers.db_helper import db_session
from src.app.models import Video
from src.app.models.comment import Comment
from src.app.models.comment import CommentDAO
from src.app.models.nicoru import Nicoru, NicoruDAO
from src.app.models.video import VideoDAO
from test.app.models.data import TestData


class TestNicoru:
    class Test___repr__:
        def test(self):
            record = Nicoru()
            record.video_id = TestData.VIDEO_ID_1
            record.comment_id = TestData.COMMENT_ID_1
            record.commented_at = TestData.COMMENTED_AT_1
            record.commented_point = TestData.COMMENTED_POINT_1
            record.nikorare = 1
            assert str(record) == '<Nicoru {}-{}>'.format(record.video_id, record.comment_id)


class TestNicoruDAO:
    class Test_find_by_video_id:
        def test_not_found(self):
            with db_session() as session:
                # setup
                session.query(Nicoru).delete()
                dao = NicoruDAO(session)

                # run
                stored = dao.find_by_video_id(TestData.VIDEO_ID_1)

                # verify
                assert stored == {}

        def test_found(self):
            with db_session() as session:
                # setup
                session.query(Nicoru).delete()
                dao = NicoruDAO(session)
                dao.add_or_update(video_id=TestData.VIDEO_ID_1,
                                  comment_id=TestData.COMMENT_ID_1,
                                  commented_at=TestData.COMMENTED_AT_1,
                                  commented_point=TestData.COMMENTED_POINT_1)

                # run
                stored = dao.find_by_video_id(TestData.VIDEO_ID_1)

                # verify
                assert stored == {TestData.COMMENT_ID_1: 1}

    class Test_add_or_update:
        def test_add(self):
            with db_session() as session:
                # setup
                session.query(Nicoru).delete()
                dao = NicoruDAO(session)

                # run
                new = dao.add_or_update(video_id=TestData.VIDEO_ID_1,
                                        comment_id=TestData.COMMENT_ID_1,
                                        commented_at=TestData.COMMENTED_AT_1,
                                        commented_point=TestData.COMMENTED_POINT_1)

                # verify
                assert new.video_id == TestData.VIDEO_ID_1
                assert new.comment_id == TestData.COMMENT_ID_1
                assert new.commented_at == TestData.COMMENTED_AT_1
                assert new.commented_point == TestData.COMMENTED_POINT_1
                assert new.nikorare == 1
                stored = dao.find_by_video_id_and_comment_id(video_id=TestData.VIDEO_ID_1,
                                                             comment_id=TestData.COMMENT_ID_1)
                assert stored.video_id == TestData.VIDEO_ID_1
                assert stored.comment_id == TestData.COMMENT_ID_1
                assert stored.commented_at == TestData.COMMENTED_AT_1
                assert stored.commented_point == TestData.COMMENTED_POINT_1
                assert stored.nikorare == 1

        def test_update(self):
            with db_session() as session:
                # setup
                session.query(Nicoru).delete()
                dao = NicoruDAO(session)
                dao.add_or_update(video_id=TestData.VIDEO_ID_1,
                                  comment_id=TestData.COMMENT_ID_1,
                                  commented_at=TestData.COMMENTED_AT_1,
                                  commented_point=TestData.COMMENTED_POINT_1)

                # run
                updated = dao.add_or_update(video_id=TestData.VIDEO_ID_1,
                                            comment_id=TestData.COMMENT_ID_1,
                                            commented_at=TestData.COMMENTED_AT_2,
                                            commented_point=TestData.COMMENTED_POINT_2)

                # verify
                assert updated.video_id == TestData.VIDEO_ID_1
                assert updated.comment_id == TestData.COMMENT_ID_1
                assert updated.commented_at == TestData.COMMENTED_AT_2
                assert updated.commented_point == TestData.COMMENTED_POINT_2
                assert updated.nikorare == 2
                stored = dao.find_by_video_id_and_comment_id(video_id=TestData.VIDEO_ID_1,
                                                             comment_id=TestData.COMMENT_ID_1)
                assert stored.video_id == TestData.VIDEO_ID_1
                assert stored.comment_id == TestData.COMMENT_ID_1
                assert stored.commented_at == TestData.COMMENTED_AT_2
                assert stored.commented_point == TestData.COMMENTED_POINT_2
                assert stored.nikorare == 2

    class Test_find_incomplete_comment_info:
        """
        * We will get TR(target record)
        * TR are 0 or one or more nicoru records.
        * TR's video has more incomplete comments than other nicoru records.
        """

        def get(self, nicorus: List[Tuple], comments: List[Tuple], expected: List[Tuple]):
            with db_session() as session:
                session.query(Nicoru).delete()
                session.query(Comment).delete()
                dao = NicoruDAO(session)
                c_dao = CommentDAO(session)
                for vid, cid in nicorus:
                    dao.add_or_update(video_id=vid,
                                      comment_id=cid,
                                      commented_at=TestData.COMMENTED_AT_1,
                                      commented_point=TestData.COMMENTED_POINT_1)
                for vid, cid in comments:
                    c_dao.add(
                        id=cid,
                        video_id=vid,
                        text=TestData.Comment.TEXT_1,
                        posted_at=TestData.Comment.POSTED_AT_1,
                        posted_by=TestData.Comment.POSTED_BY_1,
                        point=TestData.Comment.POINT_1,
                        was_deleted=TestData.Comment.WAS_DELETED_1,
                        original_nicorare=TestData.Comment.ORIGINAL_NICORARE_1,
                        updated_at=TestData.Comment.UPDATED_AT_1,
                    )
                session.commit()
                result = dao.find_incomplete_comment_info()
                expected_2 = [(vid, cid, TestData.COMMENTED_POINT_1, TestData.COMMENTED_AT_1) for vid, cid in
                              expected]
                assert result == expected_2

        def test_not_found_1(self):
            self.get(nicorus=[
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_1),
            ], comments=[
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_1),
            ], expected=[
            ])

        def test_not_found_2(self):
            self.get(nicorus=[
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_1),
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_2),
            ], comments=[
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_1),
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_2),
            ], expected=[
            ])

        def test_found_1(self):
            self.get(nicorus=[
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_1),
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_2),
            ], comments=[
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_1),
            ], expected=[
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_2)
            ])

        def test_found_2(self):
            self.get(nicorus=[
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_1),
                (TestData.VIDEO_ID_2, TestData.COMMENT_ID_1),
                (TestData.VIDEO_ID_2, TestData.COMMENT_ID_2),
                (TestData.VIDEO_ID_3, TestData.COMMENT_ID_1),
            ], comments=[
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_1),
            ], expected=[
                (TestData.VIDEO_ID_2, TestData.COMMENT_ID_1),  # video 2 has most incomplete nicoru records
                (TestData.VIDEO_ID_2, TestData.COMMENT_ID_2),
            ])

        def test_found_3(self):
            self.get(nicorus=[
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_1),
                (TestData.VIDEO_ID_2, TestData.COMMENT_ID_1),
                (TestData.VIDEO_ID_2, TestData.COMMENT_ID_2),
                (TestData.VIDEO_ID_3, TestData.COMMENT_ID_1),
            ], comments=[
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_1),
                (TestData.VIDEO_ID_2, TestData.COMMENT_ID_1),
            ], expected=[
                (TestData.VIDEO_ID_3, TestData.COMMENT_ID_1),  # video 3 has newest nicoru records
            ])

        def test_found_4(self):
            self.get(nicorus=[
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_1),
                (TestData.VIDEO_ID_2, TestData.COMMENT_ID_1),
                (TestData.VIDEO_ID_2, TestData.COMMENT_ID_2),
                (TestData.VIDEO_ID_3, TestData.COMMENT_ID_1),
            ], comments=[
                (TestData.VIDEO_ID_1, TestData.COMMENT_ID_1),
                (TestData.VIDEO_ID_2, TestData.COMMENT_ID_1),
                (TestData.VIDEO_ID_3, TestData.COMMENT_ID_1),
            ], expected=[
                (TestData.VIDEO_ID_2, TestData.COMMENT_ID_2),
                # video 2 has newest and most incomplete nicoru records
            ])

    class Test_find_incomplete_video_info:
        """
        * We will get TR(target record)
        * TR are 0 or one or more video ids.
        * TR's video is incomplete.
        """

        def get(self, nicorus: List[str], videos: List[str], expected: List[str]):
            with db_session() as session:
                session.query(Nicoru).delete()
                session.query(Video).delete()
                dao = NicoruDAO(session)
                v_dao = VideoDAO(session)
                for vid in nicorus:
                    dao.add_or_update(video_id=vid,
                                      comment_id=TestData.COMMENT_ID_1,
                                      commented_at=TestData.COMMENTED_AT_1,
                                      commented_point=TestData.COMMENTED_POINT_1)
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
                        updated_at=TestData.Video.UPDATED_AT_1,
                    )
                session.commit()
                result = dao.find_incomplete_video_info()
                expected_2 = [(vid,) for vid in expected]
                assert result == expected_2

        def test_not_found_1(self):
            self.get(nicorus=[
                TestData.VIDEO_ID_1,
            ], videos=[
                TestData.VIDEO_ID_1,
            ], expected=[
            ])

        def test_not_found_2(self):
            self.get(nicorus=[
                TestData.VIDEO_ID_1,
                TestData.VIDEO_ID_2,
            ], videos=[
                TestData.VIDEO_ID_1,
                TestData.VIDEO_ID_2,
            ], expected=[
            ])

        def test_found_1(self):
            self.get(nicorus=[
                TestData.VIDEO_ID_1,
            ], videos=[
            ], expected=[
                TestData.VIDEO_ID_1,
            ])

        def test_found_2(self):
            self.get(nicorus=[
                TestData.VIDEO_ID_1,
                TestData.VIDEO_ID_2,
            ], videos=[
                TestData.VIDEO_ID_1,
            ], expected=[
                TestData.VIDEO_ID_2,
            ])

        def test_found_3(self):
            self.get(nicorus=[
                TestData.VIDEO_ID_1,
                TestData.VIDEO_ID_2,
            ], videos=[
            ], expected=[
                TestData.VIDEO_ID_1,
                TestData.VIDEO_ID_2,
            ])
