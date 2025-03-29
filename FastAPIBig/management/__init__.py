from FastAPIBig.orm.base.base_model import ORMSession
from FastAPIBig.orm.base.session_manager import DataBaseSessionManager
from FastAPIBig.conf.settings import get_project_settings, get_declarative_base

settings = get_project_settings()
Base = get_declarative_base()
db_manager = DataBaseSessionManager(settings.DATABASE_URL)
ORMSession.initialize(db_manager)
