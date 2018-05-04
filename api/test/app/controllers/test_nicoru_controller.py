from flask import request

from src.app.app import application
from src.app.controllers.nicoru_controller import NicoruController
from src.app.helpers.db_helper import db_session
from src.app.models import Nicoru


class TestNicoru:
    class Test_get:
        def test(self):
            # setup
            with db_session() as session:
                session.query(Nicoru).delete()
            nicoru = NicoruController()
            # run
            result = nicoru.get('sm9')
            # verify
            assert result == {}

    class Test_put:
        def dummy_get_json(self, force=False, silent=False, cache=True):
            return {'cid': '1'}

        def test(self):
            with application.test_request_context():
                nicoru = NicoruController()
                request.get_json = self.dummy_get_json
                result = nicoru.put('sm9')
                assert result == {'status': 'ok'}
