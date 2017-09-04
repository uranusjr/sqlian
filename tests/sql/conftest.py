import pytest

from sqlian.standard import Engine


@pytest.fixture
def engine():
    return Engine()
