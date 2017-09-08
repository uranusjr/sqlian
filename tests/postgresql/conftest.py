import pytest

from sqlian.postgresql import Engine


@pytest.fixture
def engine():
    return Engine()


@pytest.fixture
def c(engine):
    return engine.clauses


@pytest.fixture
def e(engine):
    return engine.expressions


@pytest.fixture
def f(engine):
    return engine.functions


@pytest.fixture
def m(engine):
    return engine.compositions


@pytest.fixture
def s(engine):
    return engine.statements
