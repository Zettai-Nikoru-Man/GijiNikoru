from sqlalchemy.orm import Session


class DAOBase:
    def __init__(self, session: Session):
        self.session = session
