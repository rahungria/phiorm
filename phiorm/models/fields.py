from phiorm import exceptions
from . import model


__all__ = ('Validator', 'IntField', 'StrField', 'ForeignKeyField')


class Validator:
    def __init__(self, validator_fn, msg):
        if not callable(validator_fn):
            raise TypeError(
                'validator function must be a callable that that one arg '
                'and returns a bool'
            )
        if type(msg) is not str:
            raise TypeError(
                'msg must be a string: the message to be logged/raised for '
                'extra debugging information'
            )
        self.validator_fn = validator_fn
        self.msg = msg

    def __call__(self, value):
        if not self.validator_fn(value):
            raise exceptions.ValidationError(
                f'Field validation failed for {value}: {self.msg}'
            )


class Field:
    '''
    Base class for a model field

    Contains all base functionality for validation

    Extendable by overriding the "__call__" and "get" methods
    '''
    def __init__(self, _type, **kwargs):
        self._validate__init_kwargs(kwargs)
        self.type = _type
        self.primary_key = kwargs.get('primary_key', False)
        self.default = kwargs.get('default', None)
        self.null = kwargs.get('null', True)
        _validators = kwargs.get('validators', tuple())
        for _validator in _validators:
            if type(_validator) is not Validator:
                raise TypeError(
                    'each Validator must be an instance of Validator '
                    'object, defined in orm.fields.Validator, '
                    f'found: {type(_validator)}'
                )
        self.validators = []
        self.validators.extend(_validators)
        self.value = None

    ACCEPTED_KWARGS = ['default', 'null', 'primary_key', 'validators']

    def _validate__init_kwargs(self, kwargs):
        for arg in kwargs:
            if arg not in self.ACCEPTED_KWARGS:
                raise TypeError(f"Invalid kwarg '{arg}'")

    def serialize(self):
        return self.get()

    def deserialize(self, value):
        return self.set(value)

    def validate(self, value):
        '''
        Does all validation relating to a value

        Extend this method to add behaviour

        does not return any value, but should raise ValidationError
        if case of any failure
        '''
        # default validation
        if value is None:
            if self.default:
                return self.default
            elif self.null:
                return None
            else:
                raise exceptions.ValidationError(
                    f"this {type(self).__name__} field can't be null"
                )
        # type validation
        if type(value) is not self.type:
            raise exceptions.ValidationError(
                f'Invalid type: expected {self.type}, '
                f'received {type(value)}'
            )
        #explicit validators
        for validator in self.validators:
            validator(value)
        return value

    def get(self):
        return self.value

    def set(self, value=None):
        '''
        The field is called every time it is set.

        handles validation, exception raising and argument adjustments.
        '''
        self.value = self.validate(value)

    def __str__(self):
        self_vars = []
        for entry in self.__dict__:
            if self.__dict__[entry]:
                self_vars.append(f"{entry}={self.__dict__[entry]}")
        return f"{type(self).__name__}({', '.join(self_vars)})"

    def __repr__(self):
        return self.__str__()


class IntField(Field):
    def __init__(self, **kwargs):
        super().__init__(_type=int, **kwargs)


class StrField(Field):
    def __init__(self, max_length=255, **kwargs):
        super().__init__(_type=str, **kwargs)
        self.max_length = max_length
        self.validators.append(
            Validator(
                validator_fn=lambda val: len(val) <= self.max_length,
                msg=f"Exceeded max length: expected <= {self.max_length}"
            )
        )


class ForeignKeyField(Field):
    def __init__(self, ref_model, **kwargs):
        super().__init__(_type=ref_model, **kwargs)
        if not issubclass(ref_model, model.Model):
            raise exceptions.ValidationError(
                'Foreign key must reference only classes that '
                'inherit orm.models.Model'
            )
        self.ref_model = ref_model
        self.validators.append(
            Validator(
                lambda val: isinstance(val, self.ref_model),
                "Can't set foreign key to a different model than specified"
            )
        )

    def serialize(self):
        return self.get().pk()

    def deserialize(self, value):
        fk_obj = self.ref_model.filter(pk=value)
        return super().deserialize(fk_obj)
