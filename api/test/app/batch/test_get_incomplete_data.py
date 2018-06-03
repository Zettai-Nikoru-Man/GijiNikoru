import pytest

from src.app.batch.get_incomplete_data import IncompleteDataGetter


class TestIncompleteDataGetter:
    class Test_get_and_register_data:
        def test_not_implemented(self):
            with pytest.raises(NotImplementedError):
                IncompleteDataGetter.get_and_register_data(None, None)

    class Test_get_incomplete_data_key:
        def test_not_implemented(self):
            with pytest.raises(NotImplementedError):
                IncompleteDataGetter.get_incomplete_data_key(None)
