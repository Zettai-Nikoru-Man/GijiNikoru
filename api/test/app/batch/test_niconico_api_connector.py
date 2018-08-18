"""
dc-test /usr/test/app/batch/test_niconico_api_connector.py
"""
from unittest import mock

import pytest

from src.app.batch.niconico_api_connector import NiconicoAPIConnector, VideoDataGetError, CommentDataGetError
from test.app.models.data import TestData, TestDataUtil, DummySession


class TestNiconicoAPIConnector:
    class Test_get_video_info:
        def test(self):
            with mock.patch('requests.Session', DummySession):
                result = NiconicoAPIConnector().get_video_info(TestData.VIDEO_ID_1)
                assert int(result.comment_count) > 10000

        def test_not_found(self):
            with mock.patch('requests.Session', DummySession):
                with pytest.raises(VideoDataGetError):
                    NiconicoAPIConnector().get_video_info('abc')

    class Test_get_video_api_info:
        def test_success(self):
            with mock.patch('requests.Session', DummySession):
                result = NiconicoAPIConnector().get_video_api_info(TestData.VIDEO_ID_1)
                assert result.video_id == TestData.VIDEO_ID_1

        def test_failure(self):
            with mock.patch('requests.Session', DummySession):
                with pytest.raises(VideoDataGetError):
                    NiconicoAPIConnector().get_video_api_info('abc')

    class Test_get_comments:
        def test_success(self):
            with mock.patch('requests.Session', DummySession):
                result = NiconicoAPIConnector().get_comments(TestData.VIDEO_ID_1)
                assert result.count == 1

        def test_video_data_get_error(self):
            with mock.patch('requests.Session', DummySession):
                with pytest.raises(VideoDataGetError):
                    NiconicoAPIConnector().get_comments('abc')

        def test_comment_data_get_error(self):
            with mock.patch('requests.Session', DummySession):
                with pytest.raises(CommentDataGetError):
                    NiconicoAPIConnector().get_comments('')

    class Test_get_thread_key:
        def test(self):
            with mock.patch('requests.Session', DummySession):
                assert NiconicoAPIConnector()._NiconicoAPIConnector__get_thread_key('none') == ("", "")
