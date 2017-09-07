import collections
import functools
import numbers

import six

from sqlian import compat, NativeRow, Sql, UnescapableError
from sqlian.utils import is_values_mapping_sequence, partition

from .clauses import Clause


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


class QuerySql(Sql):
    """SQL variant that "knows" from what query itself is built from.
    """
    @classmethod
    def from_query(cls, query, engine):
        sql = cls(query.__sql__(engine))
        sql._source_query = query
        return sql

    @property
    def source_query(self):
        return self._source_query


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

        query = query_klass(*(prepend_args + clause_args))
        return QuerySql.from_query(query, self)

    wrapped.__query_builder__ = True
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
class BaseEngine(object):
    """An engine that does nothing.
    """
    def __init__(self):
        super(BaseEngine, self).__init__()
        # Replace the join method with a proxy callable, and set
        # sub-callables on it.
        with compat.suppress(AttributeError):
            self.join = Join(
                self, type(self).join,
                (t for t in self.compositions.ALLOWED_JOIN_TYPES if t),
            )


def iter_all_members(*modules):
    return (
        (name, getattr(module, name))
        for module in modules
        for name in module.__all__
    )


class Engine(BaseEngine):
    """Engine that emits ANSI-compliant SQL.
    """
    from . import (
        clauses, compositions, constants, expressions, functions, queries,
    )

    # Perform "from X import *" for these modules.
    locals().update({k: v for k, v in iter_all_members(
        compositions, constants, expressions, functools,
    )})

    identifier_quote = '"'
    string_quote = "'"

    # Formatter methods: Override to format things of a certain type to SQL.

    def format_constant(self, value):
        return {self.star: '*'}[value]

    def format_null(self):
        return 'NULL'

    def format_boolean(self, value):
        return {True: 'TRUE', False: 'FALSE'}[value]

    def format_number(self, value):
        return str(value)

    def escape_string(self, value):
        # SQL standard: replace quotes with pairs of them.
        return value.replace(self.string_quote, self.string_quote * 2)

    def format_string(self, value):
        return "{0}{1}{0}".format(self.string_quote, self.escape_string(value))

    def escape_identifier(self, name):
        # SQL standard: replace quotes with pairs of them.
        return name.replace(self.identifier_quote, self.identifier_quote * 2)

    def format_identifier(self, name):
        return '{0}{1}{0}'.format(
            self.identifier_quote,
            self.escape_identifier(name),
        )

    # "Smart" methods: Call these to format a given object to SQL.

    def as_value(self, value):
        if hasattr(value, '__sql__'):
            return value.__sql__(self)
        if value is None:
            return self.format_null()
        if isinstance(value, self.Constant):
            return self.format_constant(value)
        if isinstance(value, bool):
            return self.format_boolean(value)
        if isinstance(value, numbers.Number):
            return self.format_number(value)
        if isinstance(value, six.binary_type):
            return self.format_string(value.decode('utf-8'))
        if isinstance(value, six.text_type):
            return self.format_string(value)
        raise UnescapableError(value)

    def as_identifier(self, name):
        if hasattr(name, '__sql__'):
            return name.__sql__(self)
        if name is None:
            return self.format_null()
        if isinstance(name, self.Constant):
            return self.format_constant(name)
        if isinstance(name, six.binary_type):
            return self.format_identifier(name.decode('utf-8'))
        if isinstance(name, six.text_type):
            return self.format_identifier(name)
        raise UnescapableError(name)

    # Shorthand methods.

    @query_builder
    def select(self, *args, **kwargs):
        if not args and 'select' not in kwargs:
            kwargs['select'] = self.star
        return self.queries.Select, args, kwargs

    @query_builder
    def insert(self, *args, **kwargs):
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
        return self.queries.Insert, args, kwargs

    @query_builder
    def update(self, *args, **kwargs):
        return self.queries.Update, args, kwargs

    @query_builder
    def delete(self, *args, **kwargs):
        return self.queries.Delete, args, kwargs

    def join(self, join_item, on=None, using=None, join_type=''):
        if on is not None and using is not None:
            raise TypeError(
                'cannot specify both "on" and "using" for join clause',
            )

        if on is not None:
            on_using = self.clauses.On.parse(on, self)
        elif using is not None:
            on_using = self.clauses.Using.parse(using, self)
        else:
            on_using = None

        return functools.partial(
            self.Join,
            join_type=join_type,
            join_item=self.Identifier.parse(join_item, self),
            on_using=on_using,
        )
