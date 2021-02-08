import psycopg2

import philog

import phiorm.conf as conf
import phiorm.exceptions as exceptions


# TODO: abstract connection closing for every driver...
class ConnectionManager:
    '''
    class to manage all connections regardless of db/driver
    '''
    _connections = {}
    @classmethod
    def get(cls, name='connection'):
        if name not in cls._connections:
            if conf.Settings.get().DATABASE['DBDRIVER'] == 'psycopg2':
                cls._connections[name] = psycopg2.connect(
                    database=conf.Settings.get().DATABASE['DATABASE'],
                    user=conf.Settings.get().DATABASE['DB_USER'],
                    password=conf.Settings.get().DATABASE['DB_PASSWORD'],
                    host=conf.Settings.get().DATABASE['DB_HOST'],
                    port=conf.Settings.get().DATABASE['DB_PORT'],
                )
                philog.info(
                    f"Created connection '{name}' to '"
                    f"{conf.Settings.get().DATABASE['DATABASE']}://"
                    f"{conf.Settings.get().DATABASE['DB_USER']}"
                    f"@{conf.Settings.get().DATABASE['DB_HOST']}:"
                    f"{conf.Settings.get().DATABASE['DB_PORT']}'"
                )
        elif cls._connections[name].closed:
            raise exceptions.ConnectionError(
                'Connection is closed.'
            )
        return cls._connections[name]

    @classmethod
    def close(cls, name='connection'):
        try:
            cls._connections[name].close()
            philog.info(
                    f"Closed connection '{name}' to '"
                    f"{conf.Settings.get().DATABASE['DATABASE']}://"
                    f"{conf.Settings.get().DATABASE['DB_USER']}"
                    f"@{conf.Settings.get().DATABASE['DB_HOST']}:"
                    f"{conf.Settings.get().DATABASE['DB_PORT']}'"
                )
        except KeyError:
            raise exceptions.ConnectionError(
                "tried closing connection that doesn't exist"
            )

    @classmethod
    def close_all(cls):
        for conn in cls._connections:
            cls._connections[conn].close()
