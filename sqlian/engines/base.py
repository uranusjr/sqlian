import functools

import six

from sqlian import compat, Clause, Sql
from sqlian.utils import partition


def ensure_sql(f):

    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        result = f(*args, **kwargs)
        return result if isinstance(result, Sql) else Sql(result)

    wrapped.__sql_ensured__ = True
    return wrapped


def ensure_sql_wrapped(func):
    if getattr(func, '__sql_ensured__', False):
        return func
    return ensure_sql(func)


def query_builder(f):
    """Convert decorated callable to a query builder.

    The decorated callable should return a 3-tuple of the query class,
    the args, and kwargs to build to the query. This decorator parses the
    arguments into appropriate clauses, and instantiate an instance of
    query class with those clauses.
    """
    @functools.wraps(f)
    def wrapped(self, *args, **kwargs):
        query_klass, args, kwargs = f(self, *args, **kwargs)
        param_cls = {k: klass for k, klass in query_klass.param_classes}
        native_args, clause_args = map(
            list, partition(lambda arg: isinstance(arg, Clause), args),
        )

        prepend_args = []

        # Convert native arguments into an extra clause.
        if native_args:
            klass = query_klass.default_param_class
            prepend_args.append(
                klass.parse(native_args[0], self) if len(native_args) == 1
                else klass.parse(native_args, self)
            )

        # Convert kwargs into extra clauses.
        for key, arg in kwargs.items():
            if key in query_klass.param_aliases:
                key = query_klass.param_aliases[key]
            prepend_args.append(param_cls[key].parse(arg, self))

        return self.as_sql(query_klass(*(prepend_args + clause_args)))

    return wrapped


class EngineMeta(type):
    def __new__(meta, name, bases, attrdict):
        # Ensure formatter methods return a ``Sql`` instance.
        for key in list(six.iterkeys(attrdict)):
            if key.startswith('format_') or key.startswith('as_'):
                attrdict[key] = ensure_sql_wrapped(attrdict[key])
        return super(EngineMeta, meta).__new__(meta, name, bases, attrdict)


@six.add_metaclass(EngineMeta)
class Engine(object):
    """An engine that does nothing.
    """
    def __init__(self):
        super(Engine, self).__init__()
        # Populate join variants based on possible join types.
        # Example: join.natural_cross('table', on={'x.a': 'table.a'})
        with compat.suppress(AttributeError):
            join_f = type(self).join
            for join_type in self.compositions.ALLOWED_JOIN_TYPES:
                if not join_type:
                    continue
                name = join_type.lower().replace(' ', '_')
                setattr(join_f, name, functools.partial(
                    join_f, self, join_type=join_type,
                ))
