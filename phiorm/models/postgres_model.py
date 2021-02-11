from phiorm.models.query.psqlQ import psqlQ
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
    def filter(cls, q: 'psqlQ|None'=None, pk=None, **kwargs):
        # TODO still garbage fix it!
        if q is not None and kwargs:
            raise exceptions.ORMError("filter can't have 'q' and 'kwargs'")
        cls._validate_kwargs_in_fields(greedy=True, **kwargs)

        query = "SELECT * FROM {table} {where};"

        if kwargs:
            kwQ = psqlQ(**kwargs)
            if q:
                q = q & kwQ
            else:
                q = kwQ
            query = query.format(
                table=cls.table_name,
                where=f" WHERE {q.evaluate()}"
            )
        else:
            query = query.format(table=cls.table_name, where="")

        # TODO support setting table indexes explicitly and 
        # adapting the cache acording to the indexes

        # TODO add/convert PK to a collumn in  the query here...
        conn = cls.get_connection()
        data = None
        try:
            with conn:
                with conn.cursor() as cursor:
                    if kwargs or q:
                        cursor.execute(query, q.kwargs())
                    else:
                        cursor.execute(query)
                    data = cursor.fetchall()
        except psycopg2.ProgrammingError as e:
            raise exceptions.ORMError(f'postgresql Programming Error: {e}')
        return cls.deserialize(data, many=True)

    def delete(self):
        raise NotImplementedError
