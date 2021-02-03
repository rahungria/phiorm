import json
from abc import ABC, abstractmethod
from pathlib import Path

from phiorm import exceptions
from phiorm import settings
from phiorm import db
# from orm import fields as _fields


__all__ = ('Model', 'PostgresModel', 'JSONModel')


class Model(ABC):
    '''
    Abstract Model Base containing all the necessary interfaces
    and transparent functionality with Fields

    EVERY IMPLEMENTATION MUST DEFINE:

    save(self): comits all of the model's serialized fields
    (use with the serialize(self) method)
    to storage, varying on implementation.
    obs: post save fields that can only be set after saving to db
    must be set in this function

    filter(cls, **kwargs): classmethod that handles SELECT ... WHERE ...
    like queries

    delete(self): deletes an object...

    HELPER METHODS THAT CAN BE REDEFINED:

    pk(self): for quick pk lookup (O(n) as of right now)

    get_connection(cls): the retrieve the connection to use
    '''
    _cache = dict()
    fields = dict()

    def __init__(self, **kwargs):
        if not self.fields:
            raise TypeError(
                'Every child of orm.Model must declare a static dict '
                'called fields, containing every field declaration '
                '(using the orm.fields.Field object)'
            )
        self.__kwargs_in_fields(**kwargs)

        for field in self.fields:
            if field not in kwargs:
                if (
                    not self.fields[field].default and
                    not self.fields[field].null
                ):
                    raise exceptions.RequiredFieldError(
                        f"Field: {field} doesn't"
                        "have a default and can't be null"
                    )
            value = self.fields[field](value=kwargs.get(field))
            setattr(self, field, value)

    def __str__(self):
        return f'<{self.__class__.__name__}: {self.pk()}>'

    def __repr__(self):
        _dict = dict()
        for field in self.fields:
            _dict[field] = self.fields[field].serialize()
        return _dict

    def __setattr__(self, name, value):
        if name in self.fields:
            value = self.fields[name](value)
        else:
            raise exceptions.ModelPermissionError(
                'A model only allows settings its fields'
            )

    def __getattr__(self, name: str):
        if name in self.fields:
            return self.fields[name].get()
        else:
            return super().__getattr__(name)

    def __kwargs_in_fields(self, **kwargs):
        '''
        helper to determine if args passed to function
        exist in this model's fields

        raises AttributeError if any argument fails
        '''
        entries = []
        for entry in kwargs:
            if entry not in self.fields:
                entries.append(entry)
        if entries:
            raise AttributeError(
                f"columns: {tuple(entries)} don't exist in "
                f"{self.__class__.__name__}"
            )
        return True

    def serialize(self, dict_=False):
        _values = []
        for field in self.fields:
            _values.append(self.fields[field].serialize())
        return tuple(_values)

    @classmethod
    def from_dict(cls, _dict):
        return cls(**_dict)

    def pk(self):
        '''
        to be used by many other internal methods,
        like foreign keys for example.

        allows defining a combination on fields as pk.

        can be overwritten for performance or preference
        '''
        pks = []
        for field in self.fields:
            if self.fields[field].primary_key:
                pks.append(self.fields[field].get())
        return tuple(pks)

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
    def filter(cls, **kwargs):
        '''
        handles a SELECT ... WHERE ... statement. (Read)

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


class PostgresModel(Model):
    '''
    Models that refer to a postgres DB
    '''
    def save(self):
        conn = self.get_connection()
        raise NotImplementedError
    
    @classmethod
    def filter(cls, **kwargs):
        conn = cls.get_connection()
        raise NotImplementedError


class JSONModel(Model):

    @classmethod
    def _model_path(cls):
        return Path('.') / 'data'

    @classmethod
    def model_file(cls):
        try:
            return (
                f'{cls._model_path().absolute()}/'
                f'{cls.file}'
            )
        except AttributeError:
            raise AttributeError(
                'Models that inherit JSONModel must define a static '
                'field: "file" that contains the name json file '
                'to serialize and store the data. '
                'ex: "file = \'Person.json\'"'
            )

    def save(self):
        if not self._model_path().exists():
            # os.makedirs(self._model_path())
            self._model_path().mkdir()
            with open(self.model_file(), 'w') as f:
                f.write('{}')

        all_lines = None
        with open(self.model_file(), 'r') as f:
            all_lines = f.read()

        _all = json.loads(all_lines or '{}')
        if str(self.pk()) not in _all:
            _all[str(self.pk())] = self.serialize()
        else:
            raise exceptions.RepeatedPKError(
                f'instance with pk: {self.pk()} already exists. '
                'Aborting...'
            )
        with open(self.model_file(), 'w') as f:
            f.write(json.dumps(_all))

    @classmethod
    def filter(cls, **kwargs):
        _all = None
        with open(cls.model_file(), 'r') as f:
            _all = f.read()

        if _all:
            _dict = json.loads(_all)
            filtered = []
            for entry in _dict:
                valid_keys = []
                for key in kwargs:
                    try:
                        value = _dict[entry][key]
                        valid_keys.append(bool(value == kwargs[key]))
                    except KeyError:
                        raise AttributeError(f'column: "{key}" not in model')
                if False not in valid_keys:
                    filtered.append(_dict[entry])
            return tuple(filtered)
        else:
            raise Exception('Database Empty!')
