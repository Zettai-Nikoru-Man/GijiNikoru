from src.app.helpers.db_helper import db_session
from src.app.models.nicoru import NicoruDAO, Nicoru
from src.app.util.gn_logger import GNLogger

logger = GNLogger.get_logger(__name__)


class TestDBHelper:
    class Test_db_session:
        def test_use_commit_no_error(self):
            # setup
            with db_session() as session:
                session.query(Nicoru).delete()
            # run
            with db_session() as session:
                dao = NicoruDAO(session)
                dao.nicoru('sm9', '1')
            # verify
            with db_session() as session:
                dao = NicoruDAO(session)
                stored = dao.find_by_video_id_and_comment_id('sm9', '1')
                assert stored.video_id == 'sm9'
                assert stored.comment_id == '1'

        def test_use_commit_error(self):
            # setup
            with db_session() as session:
                session.query(Nicoru).delete()
            # run
            try:
                with db_session() as session:
                    dao = NicoruDAO(session)
                    dao.nicoru('sm9', '1')
                    raise Exception
            except:
                pass
            # verify
            with db_session() as session:
                dao = NicoruDAO(session)
                stored = dao.find_by_video_id_and_comment_id('sm9', '1')
                assert stored is None
