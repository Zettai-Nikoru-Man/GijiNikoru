from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api

from src.app.controllers.nicorareta_controller import NicoraretaController
from src.app.controllers.nicoru_controller import NicoruController
from src.app.controllers.screen.nicorareta_screen_controller import NicoraretaScreenController
from src.app.models import configured_db
from src.app.util.gn_logger import GNLogger

logger = GNLogger.get_logger(__name__)

# app
application = Flask(__name__)
CORS(application)

# db
application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@db/nicoru?charset=utf8mb4'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
configured_db.init_app(application)
migrate = Migrate(application, configured_db)

# api
api = Api(application)
api.add_resource(NicoruController, '/nicoru/<string:video_id>')
api.add_resource(NicoraretaController, '/nicorareta/<string:user_id>')
application.add_url_rule('/page/nicorareta/<string:user_id>', 'get', NicoraretaScreenController.get)
