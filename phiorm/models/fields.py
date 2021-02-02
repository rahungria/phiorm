from phiorm import exceptions
from phiorm import models


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


# TODO Inherit and create fields for more
# specific cases datetime (defaults and when to set),
# TODO Better __repr__ (to see when displaying all fields of a model)
# TODO delegate GET behaviour to field as well (__call__() or get())...
class Field:
    '''
    Base class for a model field.

    Contains all base functionality for validation.

    Extendable by extending the "__call__" method.
    '''
    def __init__(
        self, _type: type, primary_key=False,
        default=None, is_null=False, validators=tuple(),
    ):
        self.type = _type
        self.primary_key = primary_key
        self.default = default
        self.is_null = is_null
        for _validator in validators:
            if type(_validator) is not Validator:
                raise TypeError(
                    'each Validator must be an instance of Validator '
                    'object, defined in orm.fields.Validator, '
                    f'found: {type(_validator)}'
                )
        self.validators = []
        self.validators.extend(validators)
        self.value = None

    def get(self):
        return self.value

    def serialize(self):
        return self.value

    def validate(self, value):
        for validator in self.validators:
            validator(value)

    def __call__(self, value=None):
        '''
        The field is called every time it is set.

        Handles validation, exception raising and argument adjustments.

        Every context dependant validation should be implemented by
        inheritance/extension of this method,
        instead of using the validators system
        '''
        # null/default validation
        if value is None:
            if self.default:
                self.value = self.default
                return self.value
            elif self.is_null:
                self.value = None
                return self.value
            else:
                raise exceptions.ValidationError(
                    "This field not nullable"
                )

        # type validation
        if type(value) is not self.type:
            print(f'{self.type} is not {type(value)}')
            raise exceptions.ValidationError(
                f'Invalid type: expected {self.type}, '
                f'received {type(value)}'
            )

        # explicit validators
        for _validator in self.validators:
            _validator(value)

        self.value = value
        return self.value

    def __str__(self):
        return (
            f'{self.__class__.__name__}'
            f'({self.value if self.value else self.default})'
        )

    def __repr__(self):
        return self.__str__()


class IntField(Field):

    def __init__(self, default=None, is_null=False, validators=tuple()):
        super().__init__(
            _type=int,
            default=default, is_null=is_null, validators=validators
        )


class StrField(Field):

    def __init__(
        self, max_length=255,
        default=None, is_null=False, validators=list()
    ):
        super().__init__(
            _type=str,
            default=default, is_null=is_null, validators=validators
        )
        self.max_length = max_length
        self.validators.append(
            Validator(
                validator_fn=lambda val: len(val) <= self.max_length,
                msg=f"Exceeded max length: expected <= {self.max_length}"
            )
        )


# TODO depends on functional retrieve functionality
# TODO cascades depend of more robust messaging/event system
class ForeignKeyField(Field):

    def __init__(
        self, ref_model, is_null=False, validators=tuple()
    ):
        super().__init__(
            _type=ref_model, default=None,
            is_null=is_null, validators=validators
        )
        if not issubclass(ref_model, models.Model):
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
        ref = super().serialize()
        return ref.pk()
