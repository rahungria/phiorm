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
        cached_obj = None
        for key in kwargs:
        # for index in cls.indexes:
            # pks.append(cls.indexes[index])
        # for pk in pks:
            # if pk in cls._cache:
                # return cls._cache[pk]
            if cls.fields[key].primary_key:
                if kwargs[key] in cls._cache:
                    # TODO WHERE FIELDS ...
                    cached_obj = cls._cache[kwargs[key]]
                    break
        if cached_obj:
            # TODO iterate through args, validate and either return or continue
            pass

        # regular db queries
        query = "SELECT * FROM {table} {where};"
        where =  f"WHERE {' AND '.join([f'{k}=%({k})s' for k in kwargs])}"

        # TODO add/convert PK to a collumn in  the query here...
        conn = cls.get_connection()
        data = None
        try:
            with conn:
                with conn.cursor() as cursor:
                    if kwargs:
                        cursor.execute(
                            query.format(table=cls.table_name, where=where),
                            kwargs
                        )
                    else:
                        cursor.execute(
                            query.format(table=cls.table_name, where="")
                        )
                    data = cursor.fetchall()
        except psycopg2.ProgrammingError as e:
            raise exceptions.ORMError(
                f'postgresql Programming Error: {e}'
            )
        return cls.deserialize(data, many=True)

    def delete(self):
        raise NotImplementedError
