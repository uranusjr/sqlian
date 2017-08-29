from sqlian import (
    sql,
    clauses as c,
    compositions as m,
    expressions as e,
    functions as f,
    queries as q,
    values as v,
)


def test_select_where_equal():
    query = q.Select(
        c.Select(e.Identifier('person_id')),
        c.From(e.Identifier('person')),
        c.Where(e.Equal(e.Identifier('person_id'), v.Value('mosky'))),
    )
    assert sql(query) == """
        SELECT "person_id" FROM "person" WHERE "person_id" = 'mosky'
    """.strip()


def test_select_where_like():
    query = q.Select(
        c.Select(v.star),
        c.From(e.Identifier('person')),
        c.Where(e.Like(e.Identifier('name'), v.Value('Mosky%'))),
        c.Limit(v.Value(3)), c.Offset(v.Value(1)),
    )
    assert sql(query) == """
        SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' LIMIT 3 OFFSET 1
    """.strip()


def test_select_where_in():
    query = q.Select(
        c.Select(v.star),
        c.From(e.Identifier('person')),
        c.Where(e.In(
            e.Identifier('person_id'),
            m.List(v.Value('andy'), v.Value('bob')),
        )),
    )
    assert sql(query) == """
        SELECT * FROM "person" WHERE "person_id" IN ('andy', 'bob')
    """.strip()


def test_select_where_is_null():
    query = q.Select(
        c.Select(v.star),
        c.From(e.Identifier('person')),
        c.Where(e.Is(e.Identifier('name'), v.Value(None))),
    )
    assert sql(query) == """
        SELECT * FROM "person" WHERE "name" IS NULL
    """.strip()


def test_select_where_greater_than_like():
    query = q.Select(
        c.Select(v.star),
        c.From(e.Identifier('person')),
        c.Where(e.And(
            e.GreaterThan(e.Identifier('age'), v.Value(20)),
            e.Like(e.Identifier('name'), v.Value('Mosky%'))
        )),
    )
    assert sql(query) == """
        SELECT * FROM "person" WHERE "age" > 20 AND "name" LIKE 'Mosky%'
    """.strip()


def test_select_where_false():
    query = q.Select(
        c.Select(v.star),
        c.From(e.Identifier('person')),
        c.Where(v.Value(False)),
    )
    assert sql(query) == 'SELECT * FROM "person" WHERE FALSE'


def test_select_from():
    query = q.Select(
        c.Select(v.star),
        c.From(e.Identifier('person')),
    )
    assert sql(query) == 'SELECT * FROM "person"'


def test_select_qualified():
    query = q.Select(
        c.Select(
            e.Identifier('person', 'person_id'),
            e.Identifier('person', 'name'),
        ),
        c.From(e.Identifier('person')),
    )
    assert sql(query) == (
        'SELECT "person"."person_id", "person"."name" FROM "person"'
    )


def test_select_qualified_as():
    query = q.Select(
        c.Select(
            m.As(e.Identifier('person', 'person_id'), e.Identifier('id')),
            e.Identifier('person', 'name'),
        ),
        c.From(e.Identifier('person')),
    )
    assert sql(query) == (
        'SELECT "person"."person_id" AS "id", "person"."name" FROM "person"'
    )


def test_select_order_by():
    query = q.Select(
        c.Select(v.star),
        c.From(e.Identifier('person')),
        c.Where(e.Like(e.Identifier('name'), v.Value('Mosky%'))),
        c.OrderBy(e.Identifier('age')),
    )
    assert sql(query) == """
        SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age"
    """.strip()


def test_select_order_by_desc():
    query = q.Select(
        c.Select(v.star),
        c.From(e.Identifier('person')),
        c.Where(e.Like(e.Identifier('name'), v.Value('Mosky%'))),
        c.OrderBy(m.Ordering(e.Identifier('age'), 'desc')),
    )
    assert sql(query) == """
        SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age" DESC
    """.strip()


def test_select_param():
    query = q.Select(
        c.Select(v.star),
        c.From(e.Identifier('table')),
        c.Where(e.And(
            e.Equal(e.Identifier('auto_param'), v.Parameter('auto_param')),
            e.Equal(e.Identifier('using_alias'), v.Parameter('using_alias')),
            e.Equal(e.Identifier('custom_param'), v.Parameter('my_param')),
        )),
    )
    assert sql(query) == (
        'SELECT * FROM "table" '
        'WHERE "auto_param" = %(auto_param)s '
        'AND "using_alias" = %(using_alias)s '
        'AND "custom_param" = %(my_param)s'
    )


def test_select_count():
    query = q.Select(
        c.Select(f.Count(v.star)),
        c.From(e.Identifier('person')),
        c.GroupBy(e.Identifier('age')),
    )
    assert sql(query) == 'SELECT COUNT(*) FROM "person" GROUP BY "age"'


def test_select_join_natural():
    query = q.Select(
        c.Select(v.star),
        c.From(m.Join(
            e.Identifier('person'),
            'NATURAL', e.Identifier('detail'),
        )),
    )
    assert sql(query) == 'SELECT * FROM "person" NATURAL JOIN "detail"'


def test_select_join_inner_on():
    query = q.Select(
        c.Select(v.star),
        c.From(m.Join(
            e.Identifier('person'), 'INNER', e.Identifier('detail'),
            c.On(e.Equal(
                e.Identifier('person', 'person_id'),
                e.Identifier('detail', 'person_id'),
            )),
        )),
    )
    assert sql(query) == (
        'SELECT * FROM "person" '
        'INNER JOIN "detail" ON "person"."person_id" = "detail"."person_id"'
    )


def test_select_join_left_using():
    query = q.Select(
        c.Select(v.star),
        c.From(m.Join(
            e.Identifier('person'), 'LEFT', e.Identifier('detail'),
            c.Using(m.List(e.Identifier('person_id'))),
        )),
    )
    assert sql(query) == """
        SELECT * FROM "person" LEFT JOIN "detail" USING ("person_id")
    """.strip()


def test_select_join_cross():
    query = q.Select(
        c.Select(v.star),
        c.From(m.Join(
            e.Identifier('person'),
            'CROSS', e.Identifier('detail'),
        )),
    )
    assert sql(query) == 'SELECT * FROM "person" CROSS JOIN "detail"'


def test_select_join_right_using():
    query = q.Select(
        c.Select(v.star),
        c.From(m.Join(
            e.Identifier('person'), 'RIGHT', e.Identifier('detail'),
            c.Using(m.List(e.Identifier('person_id'))),
        )),
    )
    assert sql(query) == """
        SELECT * FROM "person" RIGHT JOIN "detail" USING ("person_id")
    """.strip()
