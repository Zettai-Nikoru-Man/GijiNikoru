from flask import request

from src.app.app import application
from src.app.controllers.nicoru_controller import NicoruController
from test.app.db_test_helper import db_test_session


class TestNicoruController:
    class Test_get:
        def test(self):
            with db_test_session() as session:
                # setup
                nicoru = NicoruController()
                # run
                result = nicoru.get('sm9')
                # verify
                assert result == {}

    class Test_put:
        def dummy_get_json(self, force=False, silent=False, cache=True):
            return {'cid': '1'}

        def test(self):
            with db_test_session() as session:
                with application.test_request_context():
                    nicoru = NicoruController()
                    request.get_json = self.dummy_get_json
                    result = nicoru.put('sm9')
                    assert result == {'status': 'ok'}
