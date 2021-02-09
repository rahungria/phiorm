import pytest
import phiorm.models as models
import phiorm.exceptions as exceptions


def test_create_int_field_kwargs():
    f = models.IntField(default=10, null=False, primary_key=True)
    with pytest.raises(TypeError):
        f2 = models.IntField(drefault=20)
        f2 = models.IntField(validator=models.Validator(lambda a:a,'None'))


def test_create_str_field_kwargs():
    f = models.StrField(default='str', null=False, primary_key=True)
    with pytest.raises(TypeError):
        f2 = models.StrField(drefault='sstr')


def test_int_default():
    f = models.IntField(default=23)
    f.set()
    assert f.get() == 23


def test_str_default():
    f = models.StrField(default='str')
    f.set()
    assert f.get() == 'str'


def test_null():
    f = models.IntField(null=True)
    f.set()
    assert f.get() == None

def test_null_default_precedence():
    i = models.IntField(default=10, null=True)
    i.set()
    assert i.get() == 10
    i2 = models.IntField(default=1, null=False)
    i2.set()
    assert i2.get() == 1


def test_validation():
    i = models.IntField(null=False)
    with pytest.raises(exceptions.ValidationError):
        i.set()
    with pytest.raises(exceptions.ValidationError):
        i.set('str')
    s = models.StrField(default='str', null=False, max_length=9)
    with pytest.raises(exceptions.ValidationError):
        s.set('1234567890')


def test_validators():
    i = models.IntField(
        validators=(models.Validator(
            lambda val: val<25,
            "valor deve ser menor que 25"
        ),)
    )
    with pytest.raises(exceptions.ValidationError):
        i.set(26)
    i.set(24)
    assert i.get() == 24
