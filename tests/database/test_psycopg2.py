import pytest

from sqlian import connect, star
from sqlian.postgresql import Psycopg2Database


psycopg2 = pytest.importorskip('psycopg2')


@pytest.fixture(scope='module')
def database_name(request):
    try:
        conn = psycopg2.connect(database='postgres')
    except psycopg2.OperationalError:
        return None
    conn.autocommit = True  # Required for CREATE DATABASE.

    database_name = 'test_sqlian_psycopg2'
    with conn.cursor() as cursor:
        cursor.execute('CREATE DATABASE "{}"'.format(database_name))

    def finalize():
        with conn.cursor() as cursor:
            cursor.execute('DROP DATABASE "{}"'.format(database_name))
        conn.close()

    request.addfinalizer(finalize)
    return database_name


@pytest.fixture
def db(request, database_name):
    if not database_name:
        pytest.skip('database unavailable')
        return None

    db = Psycopg2Database(database=database_name)

    with db.cursor() as cursor:
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
    with pytest.raises(db.ProgrammingError) as ctx:
        len(rows)
    assert str(ctx.value) == 'no results to fetch'
    names = [r.name for r in db.select('name', from_='person')]
    assert names == ['Mosky', 'Keith']


@pytest.mark.parametrize('scheme', ['postgresql', 'psycopg2+postgresql'])
def test_connect(database_name, scheme):
    db = connect('{scheme}:///{db}?client_encoding=utf8'.format(
        scheme=scheme, db=database_name,
    ))
    assert db.is_open()

    with db.cursor() as cursor:
        cursor.execute('''CREATE TABLE "person" ("name" TEXT)''')
        cursor.execute('''INSERT INTO "person" VALUES ('Mosky')''')

    record, = db.select(star, from_='person')
    assert record.name == 'Mosky'


@pytest.mark.parametrize('scheme', ['postgresql', 'psycopg2+postgresql'])
def test_connect_failure(database_name, scheme):
    with pytest.raises(psycopg2.ProgrammingError):
        connect('{scheme}:///{db}?invalid_option=1'.format(
            scheme=scheme, db=database_name,
        ))
