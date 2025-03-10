from FastAPIBig.orm.base.base_model import ORMSession
from FastAPIBig.orm.base.session_manager import DataBaseSessionManager
from FastAPIBig.conf.settings import get_project_settings

settings = get_project_settings()

db_manager = DataBaseSessionManager(settings.DATABASE_URL)
ORMSession.initialize(db_manager)
