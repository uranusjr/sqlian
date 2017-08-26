import pytest

from sqlian import (
    sql,
    clauses as c,
    compositions as m,
    expressions as e,
    functions as f,
    queries as q,
    values as v,
)


pytestmark = pytest.mark.xfail(reason='PostgreSQL backend not yet implemented')


def test_select_locking():
    # Proposed locking clause implementation:
    # class Locking(Clause):
    #     def __init__(self, *table_refs, strength, option):
    #         ...
    # Both strength and option are keyword-only (need some backporting...)
    # strength: 'UPDATE', 'NO KEY UPDATE', 'SHARE', or 'KEY SHARE'
    # option: 'NOWAIT' or 'SKIP LOCKED'
    query = q.Select(
        c.Select(f.Count(v.star)),
        c.From(e.Ref('person')),
        c.Where(e.Equal(e.Ref('person_id'), 1)),
        c.Locking('update', e.Ref('person'), nowait=True),
    )
    assert sql(query) == (
        'SELECT * FROM "person" WHERE "person_id" = 1 '
        'FOR UPDATE OF "person" NOWAIT'
    )


def test_insert_returning():
    query = q.Insert(
        c.InsertInto(
            c.Ref('person'),
            m.List(c.Ref('person_id'), c.Ref('name')),
        ),
        c.Values(v.Value('mosky'), v.Value('Mosky Liu')),
        c.Returning(v.star),
    )
    assert sql(query) == (
        'INSERT INTO "person" ("person_id", "name") '
        "VALUES ('mosky', 'Mosky Liu') RETURNING *"
    )
