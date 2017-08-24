from sqlian import (
    sql,
    clauses as c,
    compositions as m,
    expressions as e,
    functions as f,
    queries as q,
)


def test_select_where_equal():
    query = q.Select(
        c.Select(e.Ref('person_id')),
        c.From(e.Ref('person')),
        c.Where(e.Equal(e.Ref('person_id'), 'mosky')),
    )
    assert sql(query) == """
        SELECT "person_id" FROM "person" WHERE "person_id" = 'mosky'
    """.strip()


def test_select_where_like():
    query = q.Select(
        c.Select(e.star),
        c.From(e.Ref('person')),
        c.Where(e.Like(e.Ref('name'), 'Mosky%')),
        c.Limit(3), c.Offset(1),
    )
    assert sql(query) == """
        SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' LIMIT 3 OFFSET 1
    """.strip()


def test_select_where_in():
    query = q.Select(
        c.Select(e.star),
        c.From(e.Ref('person')),
        c.Where(e.In(e.Ref('person_id'), m.List('andy', 'bob'))),
    )
    assert sql(query) == """
        SELECT * FROM "person" WHERE "person_id" IN ('andy', 'bob')
    """.strip()


def test_select_where_is_null():
    query = q.Select(
        c.Select(e.star),
        c.From(e.Ref('person')),
        c.Where(e.IsNull(e.Ref('name'))),
    )
    assert sql(query) == """
        SELECT * FROM "person" WHERE "name" IS NULL
    """.strip()


def test_select_where_greater_than_like():
    query = q.Select(
        c.Select(e.star),
        c.From(e.Ref('person')),
        c.Where(e.And(
            e.GreaterThan(e.Ref('age'), 20),
            e.Like(e.Ref('name'), 'Mosky%')
        )),
    )
    assert sql(query) == """
        SELECT * FROM "person" WHERE "age" > 20 AND "name" LIKE 'Mosky%'
    """.strip()


def test_select_where_false():
    query = q.Select(
        c.Select(e.star),
        c.From(e.Ref('person')),
        c.Where(False),
    )
    assert sql(query) == 'SELECT * FROM "person" WHERE FALSE'


def test_select_from():
    query = q.Select(
        c.Select(e.star),
        c.From(e.Ref('person')),
    )
    assert sql(query) == 'SELECT * FROM "person"'


def test_select_qualified():
    query = q.Select(
        c.Select(e.Ref('person', 'person_id'), e.Ref('person', 'name')),
        c.From(e.Ref('person')),
    )
    assert sql(query) == (
        'SELECT "person"."person_id", "person"."name" FROM "person"'
    )


def test_select_qualified_as():
    query = q.Select(
        c.Select(
            m.As(e.Ref('person', 'person_id'), e.Ref('id')),
            e.Ref('person', 'name'),
        ),
        c.From(e.Ref('person')),
    )
    assert sql(query) == (
        'SELECT "person"."person_id" AS "id", "person"."name" FROM "person"'
    )


def test_select_order_by():
    query = q.Select(
        c.Select(e.star),
        c.From(e.Ref('person')),
        c.Where(e.Like(e.Ref('name'), 'Mosky%')),
        c.OrderBy(e.Ref('age')),
    )
    assert sql(query) == """
        SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age"
    """.strip()


def test_select_order_by_desc():
    query = q.Select(
        c.Select(e.star),
        c.From(e.Ref('person')),
        c.Where(e.Like(e.Ref('name'), 'Mosky%')),
        c.OrderBy(m.Ordering(e.Ref('age'), 'desc')),
    )
    assert sql(query) == """
        SELECT * FROM "person" WHERE "name" LIKE 'Mosky%' ORDER BY "age" DESC
    """.strip()


def test_select_param():
    query = q.Select(
        c.Select(e.star),
        c.From(e.Ref('table')),
        c.Where(e.And(
            e.Equal(e.Ref('auto_param'), e.Param('auto_param')),
            e.Equal(e.Ref('using_alias'), e.Param('using_alias')),
            e.Equal(e.Ref('custom_param'), e.Param('my_param')),
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
        c.Select(f.Count(e.star)),
        c.From(e.Ref('person')),
        c.GroupBy(e.Ref('age')),
    )
    assert sql(query) == 'SELECT COUNT(*) FROM "person" GROUP BY "age"'


def test_select_join_natural():
    query = q.Select(
        c.Select(e.star),
        c.From(m.Join(e.Ref('person'), 'NATURAL', e.Ref('detail'))),
    )
    assert sql(query) == 'SELECT * FROM "person" NATURAL JOIN "detail"'


def test_select_join_inner_on():
    query = q.Select(
        c.Select(e.star),
        c.From(m.Join(
            e.Ref('person'), 'INNER', e.Ref('detail'),
            c.On(e.Equal(
                e.Ref('person', 'person_id'),
                e.Ref('detail', 'person_id'),
            )),
        )),
    )
    assert sql(query) == (
        'SELECT * FROM "person" '
        'INNER JOIN "detail" ON "person"."person_id" = "detail"."person_id"'
    )


def test_select_join_left_using():
    query = q.Select(
        c.Select(e.star),
        c.From(m.Join(
            e.Ref('person'), 'LEFT', e.Ref('detail'),
            c.Using(m.List(e.Ref('person_id'))),
        )),
    )
    assert sql(query) == """
        SELECT * FROM "person" LEFT JOIN "detail" USING ("person_id")
    """.strip()


def test_select_join_cross():
    query = q.Select(
        c.Select(e.star),
        c.From(m.Join(e.Ref('person'), 'CROSS', e.Ref('detail'))),
    )
    assert sql(query) == 'SELECT * FROM "person" CROSS JOIN "detail"'


def test_select_join_right_using():
    query = q.Select(
        c.Select(e.star),
        c.From(m.Join(
            e.Ref('person'), 'RIGHT', e.Ref('detail'),
            c.Using(m.List(e.Ref('person_id'))),
        )),
    )
    assert sql(query) == """
        SELECT * FROM "person" RIGHT JOIN "detail" USING ("person_id")
    """.strip()
