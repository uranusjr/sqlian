import pytest

from sqlian.records import Record, RecordCollection


@pytest.fixture
def keys():
    return ('name', 'occupation', 'main_language')


@pytest.fixture
def values():
    return ('Mosky', 'Pinkoi', 'Python')


@pytest.fixture
def record(keys, values):
    return Record(keys, values)


def test_record(record):
    assert repr(record) == (
        '<Record {"name": "Mosky", "occupation": "Pinkoi", '
        '"main_language": "Python"}>'
    )


def test_record_len(record):
    assert len(record) == 3


def test_record_getitem_key(record):
    assert record['name'] == 'Mosky'
    assert record['occupation'] == 'Pinkoi'
    assert record['main_language'] == 'Python'


def test_record_getitem_key_error(record):
    with pytest.raises(KeyError) as ctx:
        record['color']
    assert str(ctx.value) == "'color'"


def test_record_getitem_index(record):
    assert record[0] == 'Mosky'
    assert record[1] == 'Pinkoi'
    assert record[2] == 'Python'


def test_record_getitem_index_error(record):
    with pytest.raises(IndexError) as ctx:
        record[3]
    assert str(ctx.value) == '3'


def test_record_getattr(record):
    assert record.name == 'Mosky'
    assert record.occupation == 'Pinkoi'
    assert record.main_language == 'Python'


def test_record_getattr_error(record):
    with pytest.raises(AttributeError) as ctx:
        record.color
    assert str(ctx.value) == "'Record' object has no attribute 'color'"


def test_record_equal(record):
    assert record == Record(
        ('name', 'occupation', 'main_language'),
        ('Mosky', 'Pinkoi', 'Python'),
    )
    assert record != Record(    # Ordering matters.
        ('main_language', 'occupation', 'name'),
        ('Python', 'Pinkoi', 'Mosky'),
    )


def test_record_get(record):
    assert record.get('name') == 'Mosky'
    assert record.get('occupation', 'GliaCloud') == 'Pinkoi'
    assert record.get('main_language', 'C') == 'Python'

    assert record.get('age') is None
    assert record.get('color', 'red') == 'red'


def test_record_keys(record):
    assert record.keys() == ('name', 'occupation', 'main_language')


def test_record_values(record):
    assert (record.values()) == ('Mosky', 'Pinkoi', 'Python')


def test_record_items(record):
    assert dict(record.items()) == {
        'name': 'Mosky',
        'occupation': 'Pinkoi',
        'main_language': 'Python',
    }


@pytest.fixture
def collection(keys, record):
    return RecordCollection(iter([
        record,
        Record(keys, ('Keith', 'iCHEF', 'Ruby')),
    ]))


def test_collection_pending(collection):
    assert repr(collection) == '<RecordCollection (pending)>'


def test_collection_half_pending(collection):
    collection[0]
    assert repr(collection) == '<RecordCollection (1+ rows, pending)>'


def test_collection_done(collection):
    for r in collection:
        pass
    assert repr(collection) == '<RecordCollection (2 rows)>'


def test_collection_half_iter(keys, record, collection):
    assert collection[0] == Record(keys, ('Mosky', 'Pinkoi', 'Python'))
    for i, r in enumerate(collection):
        if i == 0:
            assert r == Record(keys, ('Mosky', 'Pinkoi', 'Python'))
        else:
            assert r == Record(keys, ('Keith', 'iCHEF', 'Ruby'))


def test_collection_iter(keys, collection):
    record_list = [r for r in collection]
    assert record_list == [
        Record(keys, ('Mosky', 'Pinkoi', 'Python')),
        Record(keys, ('Keith', 'iCHEF', 'Ruby')),
    ]


def test_collection_getitem(keys, collection):
    assert collection[0] == Record(keys, ('Mosky', 'Pinkoi', 'Python'))
    assert collection[1] == Record(keys, ('Keith', 'iCHEF', 'Ruby'))


def test_collection_indexerror(collection):
    with pytest.raises(IndexError) as ctx:
        collection[2]
    assert str(ctx.value) == 'list index out of range'
