from src.app.config.constants_template import Constants


class TestConstants:
    class TestMail:
        assert Constants.Mail is not None

    class TestApp:
        assert Constants.App is not None

    class TestNiconico:
        assert Constants.Niconico is not None
