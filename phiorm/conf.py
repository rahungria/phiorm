import os
import dotenv
import pathlib

import philog

from phiorm import exceptions


class Settings:
    _instance = None

    def __init__(
        self,
        base_dir: pathlib.Path,
        dotenv_path: pathlib.Path,
        database: dict=None,
        debug: bool=False
    ):
        self.BASE_DIR = base_dir
        self.DOTENV_PATH = dotenv_path
        self.DATABASE = database
        self.DEBUG = debug

    @classmethod
    def get(cls):
        '''
        returns the Settings singleton, builds if needed
        '''
        if not cls._instance:
            cls._instance = cls._build()
        return cls._instance

    @classmethod
    def _build(cls):
        '''
        builds all settings configurations from .env file
        '''
        philog.debug('Building phiorm settings')
        BASE_DIR = pathlib.Path('.')
        DOTENV_PATH = BASE_DIR/'.env'

        if not DOTENV_PATH.exists():
            raise exceptions.ConfigurationError('Invalid path for ORM .env file')
        dotenv.load_dotenv(dotenv_path=DOTENV_PATH)

        try:
            DEBUG = bool(os.getenv('PHIORM_DEBUG', False))
            DATABASE = {
                'DBDRIVER': os.environ['PHIORM_DBDRIVER'],
                'DATABASE': os.environ['PHIORM_DATABASE'],
                'DB_USER': os.environ['PHIORM_DB_USER'],
                'DB_PASSWORD': os.environ['PHIORM_DB_PASSWORD'],
                'DB_HOST': os.getenv('PHIORM_DB_HOST') if os.getenv('PHIORM_DB_HOST') else 'localhost',
                'DB_PORT': os.getenv('PHIORM_DB_PORT') if os.getenv('PHIORM_DB_PORT') else '5432',
            }
        except KeyError:
            DATABASE = None
            raise exceptions.ConfigurationError(
                '.env must define "PHIORM_DBDRIVER", "PHIORM_DATABASE", "PHIORM_DB_USER", "PHIORM_DB_PASSWORD"'
            )
        return cls(
            base_dir=BASE_DIR,
            dotenv_path=DOTENV_PATH,
            database=DATABASE,
            debug=DEBUG
        )
