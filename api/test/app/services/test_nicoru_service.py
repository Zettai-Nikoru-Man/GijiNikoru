import pytest

from src.app.services.nicoru_service import NicoruService
from test.app.models.data import TestData


class TestNicoruService:
    class Test_post_input_is_valid:
        def test_valid_vid_valid_cid(self):
            assert NicoruService.post_input_is_valid(TestData.VIDEO_ID_1, TestData.COMMENT_ID_1)

        def test_valid_vid_invalid_cid(self):
            assert not NicoruService.post_input_is_valid(TestData.VIDEO_ID_1, '')

        def test_invalid_vid_valid_cid(self):
            assert not NicoruService.post_input_is_valid('', TestData.COMMENT_ID_1)

        def test_invalid_vid_invalid_cid(self):
            assert not NicoruService.post_input_is_valid('', '')

    class Test_video_id_is_valid:
        def test_valid_1(self):
            assert NicoruService.video_id_is_valid(TestData.VIDEO_ID_1)

        def test_length(self):
            v1 = 'sm11451481089351281'
            v2 = 'sm114514810893512810'
            v3 = 'sm1145148108935128101'
            assert len(v1) == 19
            assert NicoruService.video_id_is_valid(v1)
            assert len(v2) == 20
            assert NicoruService.video_id_is_valid(v2)
            assert len(v3) == 21
            assert not NicoruService.video_id_is_valid(v3)

        def test_char_variation(self):
            assert NicoruService.video_id_is_valid('sm114514')
            assert NicoruService.video_id_is_valid('sm')
            assert not NicoruService.video_id_is_valid('sm 114514')
            assert not NicoruService.video_id_is_valid(' 114514')
            assert not NicoruService.video_id_is_valid('')
            assert not NicoruService.video_id_is_valid(None)

    class Test_comment_id_is_valid:
        def test_valid_1(self):
            assert NicoruService.comment_id_is_valid(TestData.COMMENT_ID_1)

        def test_length(self):
            c1 = '114514810'
            c2 = '1145148108'
            c3 = '11451481089'
            assert len(c1) == 9
            assert NicoruService.comment_id_is_valid(c1)
            assert len(c2) == 10
            assert NicoruService.comment_id_is_valid(c2)
            assert len(c3) == 11
            assert not NicoruService.comment_id_is_valid(c3)

        def test_char_variation(self):
            assert NicoruService.comment_id_is_valid('114514')
            assert NicoruService.comment_id_is_valid('1')
            assert not NicoruService.comment_id_is_valid('1 14514')
            assert not NicoruService.comment_id_is_valid(' 114514')
            assert not NicoruService.comment_id_is_valid('a')
            assert not NicoruService.comment_id_is_valid('')
            assert not NicoruService.comment_id_is_valid(None)
