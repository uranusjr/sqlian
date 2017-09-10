import pytest

from sqlian import connect, star
from sqlian.sqlite import SQLite3Database


@pytest.fixture
def db(request, tmpdir):
    dbpath = tmpdir.join('sqlian-test.sqlite3')
    db = SQLite3Database(database=str(dbpath))

    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE "person" (
            "name" TEXT,
            "occupation" TEXT,
            "main_language" TEXT)
    ''')
    cursor.execute('''
        INSERT INTO "person" ("name", "occupation", "main_language")
        VALUES ('Mosky', 'Pinkoi', 'Python')
    ''')
    cursor.close()

    def finalize():
        db.close()
        dbpath.remove(ignore_errors=True)

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
    assert not rows
    names = [r.name for r in db.select('name', from_='person')]
    assert names == ['Mosky', 'Keith']


@pytest.mark.parametrize('scheme', ['sqlite', 'sqlite3+sqlite'])
def test_connect(tmpdir, scheme):
    dbpath = tmpdir.join('sqlian-connect-test.sqlite3')
    db = connect('{scheme}:///{path}'.format(scheme=scheme, path=dbpath))
    assert db.is_open()

    cursor = db.cursor()
    cursor.execute('''CREATE TABLE "person" ("name" TEXT)''')
    cursor.execute('''INSERT INTO "person" VALUES ('Mosky')''')
    cursor.close()

    record, = db.select(star, from_='person')
    assert record.name == 'Mosky'
