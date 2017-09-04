import functools

import six

from . import compat
from .base import Sql
from .standard import Clause
from .utils import partition


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


class Join(object):
    """Pxory callable for Engine.join() with sub-callables.

    Attributes on this callable object represent join variants.
    """
    def __init__(self, engine, join_f, join_types):
        super(Join, self).__init__()
        self.join_f = join_f

        # Populate join variants based on possible join types.
        # Example: join.natural_cross('table', on={'x.a': 'table.a'})
        for join_type in join_types:
            name = join_type.lower().replace(' ', '_')
            setattr(self, name, functools.partial(
                join_f, engine, join_type=join_type,
            ))

    def __call__(self, *args, **kwargs):
        return self.join_f(*args, **kwargs)


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
        # Replace the join method with a proxy callable, and set
        # sub-callables on it.
        with compat.suppress(AttributeError):
            self.join = Join(
                self, type(self).join,
                (t for t in self.compositions.ALLOWED_JOIN_TYPES if t),
            )
