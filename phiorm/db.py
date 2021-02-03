import psycopg2

from phiorm import settings
from phiorm import exceptions

import philog



# TODO(rapha): abstract connection closing for every driver...
class ConnectionManager:
    '''
    class to manage all connections regardless of db/driver
    '''
    _connections = {}
    @classmethod
    def get(cls, name='connection'):
        if name not in cls._connections:
            if settings.DATABASE['DBDRIVER'] == 'psycopg2':
                cls._connections[name] = psycopg2.connect(
                    database=settings.DATABASE['DATABASE'],
                    user=settings.DATABASE['DB_USER'],
                    password=settings.DATABASE['DB_PASSWORD'],
                    host=settings.DATABASE['DB_HOST'],
                    port=settings.DATABASE['DB_PORT'],
                )
                philog.info(
                    f"Created connection '{name}' to "
                    f"{settings.DATABASE['DATABASE']}://"
                    f"{settings.DATABASE['DB_USER']}"
                    f"@{settings.DATABASE['DB_HOST']}:"
                    f"{settings.DATABASE['DB_PORT']}"
                )
        elif cls._connections[name].closed:
            raise exceptions.ORMException(
                'Connection is closed.'
            )
        return cls._connections[name]

    @classmethod
    def close(cls, name='connection'):
        try:
            cls._connections[name].close()
        except KeyError:
            raise exceptions.ORMException(
                "tried closing connection that doesn't exist"
            )

    @classmethod
    def close_all(cls):
        for conn in cls._connections:
            cls._connections[conn].close()
