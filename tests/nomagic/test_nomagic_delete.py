from sqlian import (
    sql,
    clauses as c,
    compositions as m,
    expressions as e,
    functions as f,
    queries as q,
    values as v,
)


def test_delete():
    query = q.Delete(
        c.DeleteFrom(e.Ref('person')),
        c.Where(e.Equal(e.Ref('person_id'), v.Value('mosky'))),
    )
    assert sql(query) == """
        DELETE FROM "person" WHERE "person_id" = 'mosky'
    """.strip()
