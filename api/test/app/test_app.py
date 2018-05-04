from src.app import app


class TestApp:
    def test(self):
        assert app.api is not None
