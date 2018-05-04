import pytest

from src.app.batch.niconico_api_connector import NiconicoAPIConnector, VideoDataGetError


class TestNiconicoAPIConnector:
    API_CONNECTOR = NiconicoAPIConnector()

    class Test_get_video_info:
        def test(self):
            result = TestNiconicoAPIConnector.API_CONNECTOR.get_video_info('sm9')
            assert int(result.comment_count) > 10000

        def test_not_found(self):
            with pytest.raises(VideoDataGetError):
                TestNiconicoAPIConnector.API_CONNECTOR.get_video_info('abc')

    class Test_get_video_api_info:
        def test(self):
            result = TestNiconicoAPIConnector.API_CONNECTOR.get_video_api_info('sm9')
            assert result.video_id == 'sm9'

    class Test_get_comments:
        def test_non_offical_video(self):
            result = TestNiconicoAPIConnector.API_CONNECTOR.get_comments('sm9')
            assert result.count > 100

        def test_offical_video(self):
            result = TestNiconicoAPIConnector.API_CONNECTOR.get_comments('1524623846')
            assert result.count > 100
