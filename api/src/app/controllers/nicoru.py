from flask import request
from flask_restful import Resource

from src.app.helpers.db_helper import db_session
from src.app.models.nicoru import NicoruDAO


class Nicoru(Resource):
    def get(self, video_id: str):
        """get nicoru of video by comment ids.

        :param video_id: video id
        :return: Nicoru JSON
            e.g. if comment #100 has 1 nicoru, #101 has 2 nicoru:
                {"100": 1, "101": 2}
        """
        with db_session() as session:
            dao = NicoruDAO(session)
            return dao.find_by_video_id(video_id)

    def put(self, video_id: str):
        """ニコる要求を受信し、DB を更新します。

        当該コメントが既にニコられている場合、ニコられ数に 1 を加えます。
        そうでなければ、当該コメントのニコられ数を 1 にします。

        :param video_id: 動画 ID
        :return:
        """
        data = request.json
        with db_session() as session:
            dao = NicoruDAO(session)
            dao.add_or_update(
                video_id,
                data.get('cid'),
                data.get('ca'),
                data.get('cp')
            )
            return {
                'status': 'ok',
            }
