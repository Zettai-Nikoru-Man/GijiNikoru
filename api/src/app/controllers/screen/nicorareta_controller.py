from flask import render_template
from flask_restful import Resource

from src.app.helpers.db_helper import db_session
from src.app.models.nicoru import NicoruDAO


class NicoraretaScreenController(Resource):
    """provide nicorareta page"""

    @staticmethod
    def get(user_id: str):
        """get nicoru data which targets are comments posted by given user."""
        with db_session() as session:
            dao = NicoruDAO(session)
            records = dao.get_nicorareta(user_id)
        return render_template('nicorareta.html', records=records)
