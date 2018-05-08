from src.app.models.video import Video, VideoDAO
from test.app.db_test_helper import db_test_session
from test.app.models.data import TestData


class TestVideo:
    class Test___repr__:
        def test(self):
            record = Video()
            record.id = TestData.VIDEO_ID_1
            assert str(record) == '<Video {}>'.format(record.id)


class TestVideoDAO:
    class Test_add:
        def test(self):
            with db_test_session() as session:
                # setup
                dao = VideoDAO(session)

                # run
                new = dao.add(
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

                # verify
                assert new.id == TestData.VIDEO_ID_1
                assert new.title == TestData.Video.TITLE_1
                assert new.thumbnail == TestData.Video.THUMBNAIL_1
                assert new.posted_at == TestData.Video.POSTED_AT_1
                assert new.length == TestData.Video.LENGTH_1
                assert new.watch_url == TestData.Video.WATCH_URL_1
                assert new.posted_by == TestData.Video.POSTED_BY_1
                assert new.posted_by_name == TestData.Video.POSTED_BY_NAME_1
                stored = dao.find(TestData.VIDEO_ID_1)
                assert stored.id == TestData.VIDEO_ID_1
                assert stored.title == TestData.Video.TITLE_1
                assert stored.thumbnail == TestData.Video.THUMBNAIL_1
                assert stored.posted_at == TestData.Video.POSTED_AT_1
                assert stored.length == TestData.Video.LENGTH_1
                assert stored.watch_url == TestData.Video.WATCH_URL_1
                assert stored.posted_by == TestData.Video.POSTED_BY_1
                assert stored.posted_by_name == TestData.Video.POSTED_BY_NAME_1
