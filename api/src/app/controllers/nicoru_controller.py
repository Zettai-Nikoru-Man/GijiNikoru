from flask import request
from flask_restful import Resource

from src.app.helpers.db_helper import db_session
from src.app.models.nicoru import NicoruDAO


class NicoruController(Resource):
    def get(self, video_id: str):
        """get nicoru of video by comment ids.

        :param video_id: video id
        :return: Nicoru JSON
            e.g. if comment #100 has 1 nicoru, #101 has 2 nicoru:
                {"100": 1, "101": 2}
        """
        with db_session() as session:
            dao = NicoruDAO(session)
            return dao.get_nicoru_for_video(video_id)

    def put(self, video_id: str):
        """receive nicoru request, update db

        :param video_id: 動画 ID
        :return: status
        """
        data = request.json
        with db_session() as session:
            dao = NicoruDAO(session)
            dao.nicoru(
                video_id,
                data.get('cid'),
            )
            return {
                'status': 'ok',
            }
