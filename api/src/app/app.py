from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api

from src.app.controllers.nicoru_controller import NicoruController
from src.app.models import configured_db
from src.app.util.gn_logger import GNLogger

logger = GNLogger.get_logger(__name__)

# app
application = Flask(__name__)

# db
application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@db/nicoru'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
configured_db.init_app(application)
migrate = Migrate(application, configured_db)

# api
api = Api(application)
api.add_resource(NicoruController, '/nicoru/<string:video_id>')
