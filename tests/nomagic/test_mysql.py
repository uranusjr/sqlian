import pytest

from sqlian import (
    sql,
    clauses as c,
    expressions as e,
    functions as f,
    queries as q,
)


pytestmark = pytest.mark.skip('MySQL backend not yet implemented')


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
