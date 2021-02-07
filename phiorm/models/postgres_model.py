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
    @classmethod
    def filter(cls, pk=None, **kwargs):
        cls.__validate_kwargs_in_fields(greedy=True, **kwargs)
        for key in kwargs:
            if cls.fields[key].primary_key:
                pk = kwargs[key]
        if pk in cls._cache:
            return cls._cache[pk]
        else:
            # TODO support setting table indexes explicitly and 
            # adapting the cache acording to the indexes
            pass
            # obj = cls(**kwargs)
            # cls._cache[pk] = obj
            # return obj
        
        # conn = cls.get_connection()

    def delete(self):
        raise NotImplementedError
