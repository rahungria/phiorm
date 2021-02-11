from phiorm import exceptions
import psycopg2
from . import model


__all__ = ('PostgresModel',)


class PostgresModel(model.Model):
    '''
    Models that refer to a postgres DB
    '''
    def save(self):
        raise NotImplementedError
        conn = self.get_connection()

    # TODO support multiple pks
    # TODO None/null args
    @classmethod
    def filter(cls, pk=None, **kwargs):
        # TODO still garbage fix it!
        cls._validate_kwargs_in_fields(greedy=True, **kwargs)
        # TODO support setting table indexes explicitly and 
        # adapting the cache acording to the indexes
        where =  f"WHERE {' AND '.join([f'{k}=%({k})s' for k in kwargs])}"
        query = f"SELECT * FROM {cls.table_name} {where};"

        # TODO add/convert PK to a collumn in  the query here...
        conn = cls.get_connection()
        data = None
        try:
            with conn:
                with conn.cursor() as cursor:
                    if kwargs:
                        cursor.execute(
                            query,
                            kwargs
                        )
                    else:
                        cursor.execute(
                            query
                        )
                    data = cursor.fetchall()
        except psycopg2.ProgrammingError as e:
            raise exceptions.ORMError(
                f'postgresql Programming Error: {e}'
            )
        return cls.deserialize(data, many=True)

    def delete(self):
        raise NotImplementedError
