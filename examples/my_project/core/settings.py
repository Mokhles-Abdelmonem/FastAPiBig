""" """

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ""

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


MIDDLEWARE = []


DATABASE_URL = "postgresql+asyncpg://SG_USER:SG_PASS@localhost:5432/SG_DB"
