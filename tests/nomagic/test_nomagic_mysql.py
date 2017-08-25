import pytest

from sqlian import (
    sql,
    clauses as c,
    compositions as m,
    expressions as e,
    functions as f,
    queries as q,
)


pytestmark = pytest.mark.xfail(reason='MySQL backend not yet implemented')


def test_select_for_update():
    query = q.Select(
        c.Select(f.Count(e.star)),
        c.From(e.Ref('person')),
        c.Where(e.Equal(e.Ref('person_id'), 1)),
        c.ForUpdate(),
    )
    assert sql(query) == (
        'SELECT * FROM "person" WHERE "person_id" = 1 FOR UPDATE'
    )


def test_select_lock_in_share_mode():
    query = q.Select(
        c.Select(f.Count(e.star)),
        c.From(e.Ref('person')),
        c.Where(e.Equal(e.Ref('person_id'), 1)),
        c.LockInShareMode(),
    )
    assert sql(query) == (
        'SELECT * FROM "person" WHERE "person_id" = 1 LOCK IN SHARE MODE'
    )


def test_insert_on_duplicate_key_update():
    query = q.Insert(
        c.InsertInto(e.Ref('person')),
        c.Values(m.List('mosky', 'Mosky Liu')),
        c.OnDuplicateKeyUpdate(m.Assign(e.Ref('name'), 'Mosky Liu')),
    )
    assert sql(query) == (
        'INSERT INTO "person" '
        "VALUES ('mosky', 'Mosky Liu') "
        """ON DUPLICATE KEY UPDATE "name" = 'Mosky Liu'"""
    )


def test_replace():
    query = q.Replace(
        c.ReplaceInto(
            e.Ref('person'),
            m.List(e.Ref('person_id'), e.Ref('name')),
        ),
        c.Values(m.List('mosky', 'Mosky Liu')),
    )
    assert sql(query) == (
        'REPLACE INTO "person" ("person_id", "name") '
        "VALUES ('mosky', 'Mosky Liu')"
    )
