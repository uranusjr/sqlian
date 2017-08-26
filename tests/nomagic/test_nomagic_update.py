from sqlian import (
    sql,
    clauses as c,
    compositions as m,
    expressions as e,
    functions as f,
    queries as q,
    values as v,
)


def test_update():
    query = q.Update(
        c.Update(e.Ref('person')),
        c.Set(m.Assign(e.Ref('name'), v.Value('Mosky Liu'))),
        c.Where(e.Equal(e.Ref('person_id'), v.Value('mosky'))),
    )
    assert sql(query) == """
        UPDATE "person" SET "name" = 'Mosky Liu' WHERE "person_id" = 'mosky'
    """.strip()
