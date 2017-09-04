import collections
import functools
import numbers

import six

from sqlian import NativeRow, UnescapableError
from sqlian.utils import is_values_mapping_sequence

from sqlian.engines import (
    Engine as BaseEngine,
    query_builder,
)


class Engine(BaseEngine):
    """Engine that emits ANSI-compliant SQL.
    """
    from . import clauses, compositions, constants, expressions, queries

    identifier_quote = '"'
    string_quote = "'"

    star = constants.star

    # Formatter methods: Override to format things of a certain type to SQL.

    def format_star(self):
        return '*'

    def format_null(self):
        return 'NULL'

    def format_boolean(self, value):
        return {True: 'TRUE', False: 'FALSE'}[value]

    def format_number(self, value):
        return str(value)

    def format_identifier(self, name):
        # TODO: Escape special characters?
        return '{0}{1}{0}'.format(self.identifier_quote, name)

    def format_string(self, value):
        # SQL standard: replace quotes with pairs of them.
        value = value.replace(self.string_quote, self.string_quote * 2)
        if '\0' in value:   # TODO: Is there a good way to handle this?
            raise ValueError('null character in string')
        return "{0}{1}{0}".format(self.string_quote, value)

    # "Smart" methods: Call these to format a given object to SQL.

    def as_value(self, value):
        if value is None:
            return self.format_null()
        if value is self.star:
            return self.format_star()
        if hasattr(value, '__sql__'):
            return value.__sql__(self)
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
        if name is None:
            return self.format_null()
        if name is self.star:
            return self.format_star()
        if hasattr(name, '__sql__'):
            return name.__sql__(self)
        if isinstance(name, six.binary_type):
            return self.format_identifier(name.decode('utf-8'))
        if isinstance(name, six.text_type):
            return self.format_identifier(name)
        raise UnescapableError(name)

    def as_sql(self, value):
        if hasattr(value, '__sql__'):
            return value.__sql__(self)
        raise UnescapableError(value)

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
            self.compositions.Join,
            join_type=join_type,
            join_item=self.expressions.Identifier.parse(join_item, self),
            on_using=on_using,
        )
