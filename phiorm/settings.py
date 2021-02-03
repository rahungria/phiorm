import os
import dotenv
import pathlib
from phiorm import exceptions

DEBUG = True
BASE_DIR = pathlib.Path('.')
DOTENV_PATH = BASE_DIR / '.dev.env' if DEBUG else BASE_DIR / '.env'

if not DOTENV_PATH.exists():
    raise exceptions.ORMException('Invalid path for ORM .env file')

dotenv.load_dotenv(dotenv_path=DOTENV_PATH)

try:
    DATABASE = {
        'DBDRIVER': os.environ['DBDRIVER'],
        'DATABASE': os.environ['DATABASE'],
        'DB_USER': os.environ['DB_USER'],
        'DB_PASSWORD': os.environ['DB_PASSWORD'],
        'DB_HOST': os.getenv('DB_HOST') if os.getenv('HOST') else 'localhost',
        'DB_PORT': os.getenv('DB_PORT') if os.getenv('PORT') else '5432',
    }
except KeyError:
    DATABASE = None
    raise exceptions.ORMException(
        '.env must define "DBDRIVER", "DATABASE", "USER", "PASSWORD"'
    )
