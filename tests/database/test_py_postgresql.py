import contextlib

import pytest
import six

from sqlian import star
from sqlian.postgresql import PyPostgreSQLDatabase


dbapi = pytest.importorskip('postgresql.driver.dbapi20')
pytestmark = pytest.mark.skipif(
    six.PY2, reason='py-postgresql does not support Python 2',
)


@pytest.fixture(scope='module')
def database_name(request):
    try:
        conn = dbapi.connect(database='postgres')
    except dbapi.DatabaseError:
        return None
    conn.autocommit = True  # Required for CREATE DATABASE.

    database_name = 'test_sqlian_py_postgresql'
    with contextlib.closing(conn.cursor()) as cursor:
        cursor.execute('CREATE DATABASE "{}"'.format(database_name))

    def finalize():
        with contextlib.closing(conn.cursor()) as cursor:
            cursor.execute('DROP DATABASE "{}"'.format(database_name))
        conn.close()

    request.addfinalizer(finalize)
    return database_name


@pytest.fixture
def db(request, database_name):
    if not database_name:
        pytest.skip('database unavailable')
        return None

    db = PyPostgreSQLDatabase(database=database_name)

    with contextlib.closing(db.cursor()) as cursor:
        cursor.execute('''
            DROP TABLE IF EXISTS "person"
        ''')
        cursor.execute('''
            CREATE TABLE "person" (
                "name" VARCHAR(10),
                "occupation" VARCHAR(10),
                "main_language" VARCHAR(10))
        ''')
        cursor.execute('''
            INSERT INTO "person" ("name", "occupation", "main_language")
            VALUES ('Mosky', 'Pinkoi', 'Python')
        ''')

    def finalize():
        db.close()

    request.addfinalizer(finalize)
    return db


def test_select(db):
    rows = db.select(star, from_='person')
    record, = list(rows)
    assert record[0] == 'Mosky'
    assert record['occupation'] == 'Pinkoi'
    assert record.main_language == 'Python'


def test_insert(db):
    rows = db.insert('person', values={
        'name': 'Keith',
        'occupation': 'iCHEF',
        'main_language': 'Python',
    })
    with pytest.raises(db.InterfaceError) as ctx:
        len(rows)
    assert str(ctx.value).startswith('no portal on stack')
    names = [r.name for r in db.select('name', from_='person')]
    assert names == ['Mosky', 'Keith']
