from phiorm.models.query.psqlQ import psqlQ
import pytest


@pytest.fixture
def q_name():
    return psqlQ(name='Rudeus')


@pytest.fixture
def q_wives():
    return psqlQ(wives=3)


@pytest.fixture
def q_dad():
    return psqlQ(dad=None)


def test_query_init(q_name):
    assert q_name.evaluate() == 'name=%(name)s'


def test_query_none(q_dad):
    assert q_dad.evaluate() == "dad IS %(dad)s"


def test_query_and(q_name, q_wives):
    assert (q_name&q_wives).evaluate() == "name=%(name)s AND wives=%(wives)s"


def test_query_or(q_name, q_dad):
    assert (q_name|q_dad).evaluate() == "name=%(name)s OR dad IS %(dad)s"


def test_query_inverse(q_name, q_dad):
    assert (~q_name).evaluate() == "name!=%(name)s"
    assert (~q_dad).evaluate() == "dad IS NOT %(dad)s"


def test_complex_query(q_name, q_dad, q_wives):
    q = ~q_name|q_wives|(q_wives&~q_dad)
    assert q.evaluate() == "name!=%(name)s OR wives=%(wives)s OR wives=%(wives)s AND dad IS NOT %(dad)s"


def test_query_kwargs_preserve(q_name, q_dad, q_wives):
    q = q_name&q_dad&q_wives
    assert q.kwargs() == {'name': 'Rudeus', 'dad': None, 'wives': 3}
