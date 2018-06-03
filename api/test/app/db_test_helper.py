import contextlib

from src.app.helpers.db_helper import db_session, app
from src.app.models import Comment
from src.app.models import IrregularVideoId
from src.app.models import JobLog
from src.app.models import Nicoru
from src.app.models import Video
from src.app.models import configured_db
from src.app.models.irregular_comment_id import IrregularCommentId
from src.app.util.gn_logger import GNLogger

logger = GNLogger.get_logger(__name__)


@contextlib.contextmanager
def db_test_session():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@db/test_nicoru'
    configured_db.init_app(app)
    try:
        with db_session() as session:
            Nicoru.__table__.create(configured_db.engine, checkfirst=True)
            Video.__table__.create(configured_db.engine, checkfirst=True)
            Comment.__table__.create(configured_db.engine, checkfirst=True)
            JobLog.__table__.create(configured_db.engine, checkfirst=True)
            IrregularVideoId.__table__.create(configured_db.engine, checkfirst=True)
            IrregularCommentId.__table__.create(configured_db.engine, checkfirst=True)
            yield session
    finally:
        with app.app_context():
            Nicoru.__table__.drop(configured_db.engine, checkfirst=True)
            Video.__table__.drop(configured_db.engine, checkfirst=True)
            Comment.__table__.drop(configured_db.engine, checkfirst=True)
            JobLog.__table__.drop(configured_db.engine, checkfirst=True)
            IrregularVideoId.__table__.drop(configured_db.engine, checkfirst=True)
            IrregularCommentId.__table__.drop(configured_db.engine, checkfirst=True)
