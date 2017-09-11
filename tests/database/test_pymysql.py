import warnings

import pytest

from sqlian import star
from sqlian.mysql import PyMySQLDatabase


pymysql = pytest.importorskip('pymysql')


@pytest.fixture(scope='module')
def database_name(request):
    try:
        conn = pymysql.connect()
    except pymysql.OperationalError:
        return None

    database_name = 'test_sqlian_pymysql'
    with conn.cursor() as cursor:
        cursor.execute('CREATE DATABASE `{}`'.format(database_name))

    def finalize():
        with conn.cursor() as cursor:
            cursor.execute('DROP DATABASE `{}`'.format(database_name))
        conn.close()

    request.addfinalizer(finalize)
    return database_name


@pytest.fixture
def db(request, database_name):
    if not database_name:
        pytest.skip('database unavailable')
        return None

    db = PyMySQLDatabase(database=database_name)

    cursor = db.cursor()
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')
        cursor.execute('DROP TABLE IF EXISTS `person`')
    cursor.execute('''
        CREATE TABLE `person` (
            `name` VARCHAR(10),
            `occupation` VARCHAR(10),
            `main_language` VARCHAR(10))
    ''')
    cursor.execute('''
        INSERT INTO `person` (`name`, `occupation`, `main_language`)
        VALUES ('Mosky', 'Pinkoi', 'Python')
    ''')
    cursor.close()

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
    assert len(rows) == 0
    names = [r.name for r in db.select('name', from_='person')]
    assert names == ['Mosky', 'Keith']
