import json

from flask_restful import Resource

from src.app.helpers.db_helper import db_session
from src.app.models.nicoru import NicoruDAO


class NicoraretaController(Resource):
    """provide nicorareta data"""

    def get(self, user_id: str):
        """get nicoru data which targets are comments posted by given user.

        :param user_id: niconico user id
        :return: Nicorareta JSON
        """
        with db_session() as session:
            dao = NicoruDAO(session)
            return json.dumps(dao.get_nicorareta(user_id))
