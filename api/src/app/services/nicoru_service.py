import re


class NicoruService:
    @classmethod
    def post_input_is_valid(cls, video_id: str, comment_id: str):
        if not NicoruService.video_id_is_valid(video_id):
            return False
        if not NicoruService.comment_id_is_valid(comment_id):
            return False
        return True

    @classmethod
    def video_id_is_valid(cls, video_id: str):
        return video_id and re.match(r'^[a-zA-Z0-9]{1,20}$', video_id) is not None

    @classmethod
    def comment_id_is_valid(cls, comment_id: str):
        return comment_id and re.match(r'^[0-9]{1,10}$', comment_id) is not None
