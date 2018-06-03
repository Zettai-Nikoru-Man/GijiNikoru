"""
dc-test /usr/test/app/batch/test_nicoru_csv_importer.py
"""

from typing import List
from unittest import mock

from src.app.batch.nicoru_csv_importer import NicoruCSVImporter
from src.app.models import Nicoru
from src.app.models.nicoru import NicoruDAO
from test.app.db_test_helper import db_test_session


class TestNicoruCSVImporter:
    class Test_execute:
        def test_2_lines(self):
            with db_test_session() as session:
                # setup
                n_dao = NicoruDAO(session)
                n_dao.nicoru('sm9', '1')
                session.commit()

                stub_io = mock.mock_open(read_data='"sm9","1","3"\n"sm9","2","5"')
                with mock.patch("builtins.open", stub_io, create=True) as m:
                    m.return_value.__iter__ = lambda self_: self_
                    m.return_value.__next__ = lambda self_: next(iter(self_.readline, ''))

                    # run
                    NicoruCSVImporter.execute()

                # verify
                stored = session.query(Nicoru).all()  # type: List[Nicoru]
                assert stored[0].video_id == 'sm9'
                assert stored[0].comment_id == '1'
                assert stored[0].nicoru == 4
                assert stored[1].video_id == 'sm9'
                assert stored[1].comment_id == '2'
                assert stored[1].nicoru == 5

        def test_1001_lines(self):
            with db_test_session() as session:
                # setup
                stub_io = mock.mock_open(read_data="\n".join(['"sm{}","1","3"'.format(i) for i in range(1001)]))
                with mock.patch("builtins.open", stub_io, create=True) as m:
                    m.return_value.__iter__ = lambda self_: self_
                    m.return_value.__next__ = lambda self_: next(iter(self_.readline, ''))

                    # run
                    NicoruCSVImporter.execute()

                # verify
                stored = session.query(Nicoru).all()  # type: List[Nicoru]
                assert len(stored) == 1001
