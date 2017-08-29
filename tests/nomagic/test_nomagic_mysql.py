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


pytestmark = pytest.mark.xfail(reason='MySQL backend not yet implemented')


def test_select_for_update():
    query = q.Select(
        c.Select(f.Count(v.star)),
        c.From(e.Identifier('person')),
        c.Where(e.Equal(e.Identifier('person_id'), v.Value(1))),
        c.ForUpdate(),
    )
    assert sql(query) == (
        'SELECT * FROM "person" WHERE "person_id" = 1 FOR UPDATE'
    )


def test_select_lock_in_share_mode():
    query = q.Select(
        c.Select(f.Count(v.star)),
        c.From(e.Identifier('person')),
        c.Where(e.Equal(e.Identifier('person_id'), v.Value(1))),
        c.LockInShareMode(),
    )
    assert sql(query) == (
        'SELECT * FROM "person" WHERE "person_id" = 1 LOCK IN SHARE MODE'
    )


def test_insert_on_duplicate_key_update():
    query = q.Insert(
        c.InsertInto(e.Identifier('person')),
        c.Values(m.List(v.Value('mosky'), v.Value('Mosky Liu'))),
        c.OnDuplicateKeyUpdate(
            m.Assign(e.Identifier('name'), v.Value('Mosky Liu')),
        ),
    )
    assert sql(query) == (
        'INSERT INTO "person" '
        "VALUES ('mosky', 'Mosky Liu') "
        """ON DUPLICATE KEY UPDATE "name" = 'Mosky Liu'"""
    )


def test_replace():
    query = q.Replace(
        c.ReplaceInto(
            e.Identifier('person'),
            m.List(e.Identifier('person_id'), e.Identifier('name')),
        ),
        c.Values(m.List(v.Value('mosky'), v.Value('Mosky Liu'))),
    )
    assert sql(query) == (
        'REPLACE INTO "person" ("person_id", "name") '
        "VALUES ('mosky', 'Mosky Liu')"
    )
