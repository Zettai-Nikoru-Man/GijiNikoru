import contextlib
import traceback

from flask import Flask
from sqlalchemy.orm import Session

from src.app.models import configured_db
from src.app.util.gn_logger import GNLogger

logger = GNLogger.get_logger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@db/nicoru'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
configured_db.init_app(app)


@contextlib.contextmanager
def db_session():
    with app.app_context():
        session = configured_db.session  # type: Session
        try:
            yield session
            if session:
                session.commit()
        except Exception as e:
            logger.exception(e)
            traceback.print_exc()
            if session:
                session.rollback()
            raise e
        finally:
            if session:
                session.close()
