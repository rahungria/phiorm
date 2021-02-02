import psycopg2

from orm import settings
from orm import exceptions


_connections = {}


def get_connection(name='default_connection'):
    global _connections
    if name not in _connections:
        if settings.DATABASE['DBDRIVER'] == 'psycopg2':
            _connections[name] = psycopg2.connect(
                database=settings.DATABASE['DATABASE'],
                user=settings.DATABASE['DB_USER'],
                password=settings.DATABASE['DB_PASSWORD'],
                host=settings.DATABASE['DB_HOST'],
                port=settings.DATABASE['DB_PORT'],
            )
            print(
                f"Created connection '{name}' to "
                f"{settings.DATABASE['DATABASE']}://"
                f"{settings.DATABASE['DB_USER']}"
                f"@{settings.DATABASE['DB_HOST']}:"
                f"{settings.DATABASE['DB_PORT']}"
            )
    elif _connections[name].closed:
        raise exceptions.ORMException(
            'Connection is closed.'
        )

    return _connections[name]


def close_connections():
    global _connections
    for conn_name in _connections:
        _connections[conn_name].close()
