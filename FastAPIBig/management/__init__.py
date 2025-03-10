from FastAPIBig.orm.base.base_model import ORMSession
from FastAPIBig.orm.base.session_manager import DataBaseSessionManager

db_manager = DataBaseSessionManager(DATABASE_URL_ASYNC, DATABASE_URL_SYNC)
ORMSession.initialize(db_manager)
