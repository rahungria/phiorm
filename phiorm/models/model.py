import json
from copy import deepcopy
from abc import ABC, abstractmethod

from phiorm import exceptions
from phiorm import settings
from phiorm import db


__all__ = ('Model',)


class Model(ABC):
    '''
    Abstract Model Base containing all the necessary interfaces
    and transparent functionality with Fields

    EVERY IMPLEMENTATION MUST DEFINE:

    save(self): comits all of the model's serialized fields
    (use with the serialize(self) method) to storage,
    varying on implementation.
    obs: post save fields that can only be set after saving to db
    must be set in this function

    filter(cls, **kwargs): classmethod that handles SELECT ... WHERE ...
    like queries

    delete(self): deletes an object...

    HELPER METHODS THAT CAN BE REDEFINED:

    serialize(self): serializes obj to a valid model
    given a specific dbdriver

    deserialize(cls, obj): deserializes a specific dbdriver model
    and returns an object

    pk(cls): for quick pk lookup (O(n) as of right now)

    get_connection(cls): the retrieve the connection to use
    '''
    # TODO custom _cache object->hold memory of some cache inserts on same pk
    # use algorithm to prefer one ever another/allow extending...
    _cache = dict()
    # fields = dict()

    def __init__(self, **kwargs):
        if not type(self).fields:
            raise TypeError(
                'Every child of orm.Model must declare a static dict '
                'called fields, containing every field declaration '
                '(using the orm.fields.Field object)'
            )
        self.__dict__['fields'] = deepcopy(type(self).fields)
        self.__validate_kwargs_in_fields(**kwargs)
        self.__validate_primary_key_exists()

        # TODO add support for multiple pks
        pk_count = 0
        for field in self.fields:
            pk_count += 1 if self.fields[field].primary_key else 0
            value = self.fields[field].set(value=kwargs.get(field))
            self.__dict__[field] = value
            # setattr(self, field, value)
        if pk_count > 1:
            raise exceptions.ORMFatal(
                f'MODEL ONLY SUPPORTS ONE PRIMARY KEY AS OF RIGHT NOW'
            )

    def __str__(self):
        return f'<{type(self).__name__}: {self.pk()}>'

    def __repr__(self):
        _dict = dict()
        for field in self.fields:
            _dict[field] = self.fields[field].serialize()
        return str(_dict)

    def __setattr__(self, name, value):
        if name == 'fields':
            raise exceptions.ORMFatal(
                "A model can't alter it's fields in runtime"
            )
        elif name in self.fields:
            value = self.fields[name].set(value)
        else:
            return super().__setattr__(name, value)

    def __getattr__(self, name: str):
        if name in self.fields:
            return self.fields[name].get()
        else:
            return super().__getattr__(name)

    @classmethod
    def __validate_kwargs_in_fields(cls, greedy=False,**kwargs):
        '''
        helper to determine if args passed to function
        exist in this model's fields

        greedy -- stop at first error

        Raises:
        phiorm.exceptions.FieldError if any argument fails
        '''
        entries = []
        for entry in kwargs:
            if entry not in cls.fields:
                entries.append(entry)
                if greedy:
                    break
        if entries:
            raise exceptions.FieldError(
                f"columns: {tuple(entries)} don't exist in "
                f"'{cls.__name__}'",
                fields=tuple(entries)
            )
        return True

    def __validate_primary_key_exists(self):
        _pk_count = 0
        for field in self.fields:
            if self.fields[field].primary_key:
                _pk_count += 1
        if _pk_count == 0:
            raise exceptions.FieldError(
                f'{type(self).__name__} has no primary keys!',
                fields=tuple()
            )

    def serialize(self, dict_=False):
        '''
        serializes an object (self) into a tuple/dict of its fields

        dict_ -- if True, returns a dict serialization instead of a tuple
        '''
        if dict_:
            return json.dumps(repr(self))
        else:
            _values = []
            for field in self.fields:
                _values.append(self.fields[field].serialize())
            return tuple(_values)

    # TODO auto fields (de)serialization
    # TODO implement proper fk deserialization
    # TODO support data in form of kwargs (default to None... maybe?)
    @classmethod
    def deserialize(cls, data):
        '''
        deserializes a tuple (data) into an object an instance of this
        model's object

        loads into cache 
        '''
        # TODO raise exceptions...
        assert type(data) is tuple
        assert len(cls.fields) == len(data)

        kwargs = {}
        for i, key in enumerate(cls.fields):
            deserialized_data = cls.fields[key].deserialize(data[i])
            kwargs[key] = deserialized_data
        obj = cls(**kwargs)
        cls._cache[obj.pk()] = obj
        return obj

    @classmethod
    def from_dict(cls, _dict):
        return cls(**_dict)

    # TODO add support for multiple pks
    def pk(self):
        '''
        to be used by many other internal methods,
        like foreign keys for example.

        allows defining a combination on fields as pk.

        can be overwritten for performance or preference
        '''
        for field in self.fields:
            if self.fields[field].primary_key:
                return self.fields[field].get()
        raise exceptions.FieldError(
            f'{type(self).__name__} has no primary key!',
            fields=tuple()
        )

    @abstractmethod
    def save(self):
        '''
        Commits this model instance to storage. (Create/Update)

        Each implementation must handle db connection/serialization
        it's own way
        '''
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def filter(cls, pk=None, **kwargs):
        '''
        handles a SELECT ... WHERE ... statement (Read).
        each kwarg must match a collumn

        special case for primary key (pk)

        return an iterable (maybe special object later) containing
        all matches
        '''
        raise NotImplementedError()

    @abstractmethod
    def delete(self):
        '''
        Deletes an entry (Delete)
        '''
        pass

    @classmethod
    def get_connection(cls):
        '''
        helper method to be used by all models of a certain DBM implementation

        usualy not implemented by a User Leaf...
        '''
        return db.ConnectionManager.get(name=settings.DATABASE['DBDRIVER'])
