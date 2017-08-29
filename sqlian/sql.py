import collections
import functools

from . import (
    clauses as c,
    compositions as m,
    expressions as e,
    queries as q,
)
from .base import Sql, UnescapableError
from .clauses import Clause
from .utils import NativeRow, is_values_mapping_sequence, partition
from .values import star


def assert_sql(f):
    """Make sure the decorated function returns an SQL object.
    """
    @functools.wraps(f)
    def safe_f(*args, **kwargs):
        v = f(*args, **kwargs)
        assert isinstance(v, Sql)
        return v

    return f


@assert_sql
def sql(obj):
    if hasattr(obj, '__sql__'):
        return obj.__sql__()
    raise UnescapableError(obj)


def _instantiate_query(query_klass, args, kwargs):
    param_cls = {key: klass for key, klass in query_klass.param_classes}
    native_args, clause_args = map(
        list,
        partition(lambda arg: isinstance(arg, Clause), args),
    )

    prepend_args = []

    # Convert native arguments into an extra clause.
    if native_args:
        klass = query_klass.default_param_class
        prepend_args.append(
            klass.parse(native_args[0]) if len(native_args) == 1
            else klass.parse(native_args)
        )

    # Convert kwargs into extra clauses.
    for key, arg in kwargs.items():
        if key in query_klass.param_aliases:
            key = query_klass.param_aliases[key]
        prepend_args.append(param_cls[key].parse(arg))

    return query_klass(*(prepend_args + clause_args))


def select(*args, **kwargs):
    if not args and 'select' not in kwargs:
        kwargs['select'] = star
    return sql(_instantiate_query(q.Select, args, kwargs))


def insert(*args, **kwargs):
    # Unpack mapping 'values' kwarg into 'columns' and 'values' kwargs.
    # This only happens if the 'columns' kwarg is not already set.
    if 'columns' not in kwargs:
        values_kwarg = kwargs.get('values')
        if isinstance(values_kwarg, collections.Mapping):
            kwargs.update({
                'columns': values_kwarg.keys(),
                'values': NativeRow(values_kwarg.values()),
            })
        elif is_values_mapping_sequence(values_kwarg):
            # We need to re-pack the value dicts because the ordering of
            # `dict.values()` is not guarenteed to be consistent, even
            # if the keys are identical.
            columns = values_kwarg[0].keys()
            kwargs.update({
                'columns': columns,
                'values': [[d[k] for k in columns] for d in values_kwarg],
            })
    return sql(_instantiate_query(q.Insert, args, kwargs))


def update(*args, **kwargs):
    return sql(_instantiate_query(q.Update, args, kwargs))


def delete(*args, **kwargs):
    return sql(_instantiate_query(q.Delete, args, kwargs))


def join(join_item, on=None, using=None, join_type=''):
    if on is not None and using is not None:
        raise TypeError('cannot specify both "on" and "using" for join clause')

    if on is not None:
        on_using = c.On.parse(on)
    elif using is not None:
        on_using = c.Using.parse(using)
    else:
        on_using = None

    return functools.partial(
        m.Join,
        join_type=join_type,
        join_item=e.Ref.parse(join_item),
        on_using=on_using,
    )


# Populate join.X variates based on possible join types.
# Example: join.natural_cross('table', on={'x.a': 'table.a'})
for join_type in m.ALLOWED_JOIN_TYPES:
    name = join_type.lower().replace(' ', '_')
    if name:
        setattr(join, name, functools.partial(join, join_type=join_type))
