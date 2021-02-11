from phiorm.models.query.psqlQ import psqlQ
import pytest


@pytest.fixture
def qname():
    return psqlQ(name='Rudeus')


@pytest.fixture
def qwives():
    return psqlQ(wives=3)


@pytest.fixture
def qdad():
    return psqlQ(dad=None)


@pytest.fixture
def qcomposed():
    return psqlQ(dad=None, name='Rudeus', wife1='Silphy', wife2='Roxy', wife3='Eris', harem_size=3)


def test_query_init(qname):
    assert qname.evaluate() == 'name=%(name)s'


def test_query_none(qdad):
    assert qdad.evaluate() == "dad IS %(dad)s"


def test_query_and(qname, qwives):
    assert (qname&qwives).evaluate() == "name=%(name)s AND wives=%(wives)s"


def test_query_or(qname, qdad):
    assert (qname|qdad).evaluate() == "name=%(name)s OR dad IS %(dad)s"


def test_query_inverse(qname, qdad):
    assert (~qname).evaluate() == "name!=%(name)s"
    assert (~qdad).evaluate() == "dad IS NOT %(dad)s"


def test_complex_query(qname, qdad, qwives):
    q = ~qname|qwives|(qwives&~qdad)
    assert q.evaluate() == "name!=%(name)s OR wives=%(wives)s OR wives=%(wives)s AND dad IS NOT %(dad)s"


def test_query_kwargs(qname, qdad, qwives):
    q = qname&qdad&qwives
    assert q.kwargs() == {'name': 'Rudeus', 'dad': None, 'wives': 3}


def test_simple_invert(qname, qdad):
    assert (qname&qdad).evaluate() == (~(qname&qdad)).evaluate()


def test_invert_inverted(qname):
    assert (~(~qname)).evaluate() == qname.evaluate()


def test_non_commital_invert(qdad):
    (~qdad).evaluate()
    assert qdad.evaluate() == 'dad IS %(dad)s'


def test_composed_query_kwargs(qcomposed: psqlQ):
    kwargs = qcomposed.kwargs()
    expected_kwargs = dict(
        dad=None,
        name='Rudeus',
        wife1='Silphy', wife2='Roxy', wife3='Eris',
        harem_size=3
    )
    assert kwargs == expected_kwargs


def test_composed_query_evaluate(qcomposed):
    query = qcomposed.evaluate()
    expected_query = (
        "dad IS %(dad)s AND name=%(name)s AND "
        "wife1=%(wife1)s AND wife2=%(wife2)s AND wife3=%(wife3)s AND "
        "harem_size=%(harem_size)s"
    )
    assert query == expected_query

