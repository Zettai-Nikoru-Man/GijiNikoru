from src.app.app import application
from src.app.controllers.screen.nicorareta_screen_controller import NicoraretaScreenController
from test.app.db_test_helper import db_test_session
from test.app.models.data import TestData


class TestNicoraretaScreenController:
    class Test_get:
        def test(self):
            with db_test_session() as session:
                with application.test_request_context():
                    obj = NicoraretaScreenController()
                    result = obj.get(TestData.Comment.POSTED_BY_1)
                    assert '<title>ニコられた</title>' in result
