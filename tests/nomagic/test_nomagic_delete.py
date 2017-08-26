from sqlian import (
    sql,
    base as b,
    clauses as c,
    compositions as m,
    expressions as e,
    functions as f,
    queries as q,
)


def test_delete():
    query = q.Delete(
        c.DeleteFrom(e.Ref('person')),
        c.Where(e.Equal(e.Ref('person_id'), b.Value('mosky'))),
    )
    assert sql(query) == """
        DELETE FROM "person" WHERE "person_id" = 'mosky'
    """.strip()
