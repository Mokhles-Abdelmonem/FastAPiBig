""" """

from pathlib import Path

# Base directory for SQLite storage
BASE_DIR = Path(__file__).resolve().parent

# Other default settings
DEBUG = True
SECRET_KEY = "default-secret-key"



# Default to SQLite if the user doesn't configure a database
DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/db.sqlite3"
