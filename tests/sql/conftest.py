import pytest

from sqlian.engines import StandardEngine


@pytest.fixture
def engine():
    return StandardEngine()
