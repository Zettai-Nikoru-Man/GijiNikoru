import csv

from src.app.config.hard_constants import HardConstants
from src.app.helpers.db_helper import db_session
from src.app.models.nicoru import NicoruDAO
from src.app.util.gn_logger import GNLogger

logger = GNLogger.get_logger(__name__)


class NicoruCSVImporter:
    @classmethod
    def execute(cls):
        with open(HardConstants.App.NICORU_CSV_TO_BE_IMPORTED, 'r') as f:
            with db_session() as session:
                # print(list(f.readlines()))
                lines = csv.reader(f, delimiter=",", lineterminator='\n', quotechar='"')
                lines_to_be_committed = 0
                dao = NicoruDAO(session)


                # do import
                for vid, cid, nicoru in lines:
                    dao.nicoru_from_csv(vid, cid, nicoru)
                    lines_to_be_committed += 1
                    if lines_to_be_committed >= 1000:
                        # commit for each 1000 lines
                        session.commit()
                        lines_to_be_committed = 0

                # commit last lines
                session.commit()
