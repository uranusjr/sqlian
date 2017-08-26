import collections

from . import clauses
from .base import Named, Sql
from .utils import NativeRow, is_values_mapping_sequence


class QueryError(ValueError):
    def __init__(self, clause_name, query_name):
        super(QueryError, self).__init__(self.error_template.format(
            clause=clause_name, query=query_name,
        ))
        self.clause = clause_name
        self.query = query_name


class DuplicateClauseError(QueryError):
    error_template = 'duplicate {clause!r} clauses for query {query!r}'


class InvalidClauseError(QueryError):
    error_template = 'Query {query!r} does not accept clause {clause!r}'


class Query(Named):

    param_aliases = ()

    def __init__(self, *args, **kwargs):
        super(Query, self).__init__()
        self.param_clauses = self._map_clause_to_params(args, kwargs)

    def __repr__(self):
        return '{}({})'.format(
            self.type_name,
            ', '.join(
                repr(self.param_clauses[key])
                for key, _ in self.param_classes
                if key in self.param_clauses
            ),
        )

    def __sql__(self):
        return Sql(' ').join(
            self.param_clauses[key]
            for key, _ in self.param_classes
            if key in self.param_clauses
        )

    def _map_clause_to_params(self, args, kwargs):
        param_clauses = {}
        native_args = []
        cls_param = {klass: key for key, klass in self.param_classes}
        param_cls = {key: klass for key, klass in self.param_classes}

        for arg in args:
            no_match = True
            if not hasattr(arg, '__sql__'):
                native_args.append(arg)
                continue
            for klass in type(arg).mro():
                try:
                    key = cls_param[klass]
                except KeyError:
                    continue
                if key in param_clauses:
                    raise DuplicateClauseError(arg.sql_name, self.sql_name)
                param_clauses[key] = arg
                no_match = False
                break
            if no_match:
                raise InvalidClauseError(arg.sql_name, self.sql_name)

        for key, arg in kwargs.items():
            if key in self.param_aliases:
                key = self.param_aliases[key]
            param_clauses[key] = param_cls[key].parse(arg)

        if native_args:
            key, klass = self.default_param
            if len(native_args) == 1:
                param_clauses[key] = klass.parse(native_args[0])
            else:
                param_clauses[key] = klass.parse(native_args)
        return param_clauses


class Select(Query):
    param_classes = [
        ('select', clauses.Select),
        ('from_', clauses.From),
        ('where', clauses.Where),
        ('group_by', clauses.GroupBy),
        ('order_by', clauses.OrderBy),
        ('limit', clauses.Limit),
        ('offset', clauses.Offset),
    ]


class Insert(Query):

    param_classes = [
        ('insert', clauses.InsertInto),
        ('columns', clauses.Columns),
        ('values', clauses.Values),
    ]
    default_param = ('insert', clauses.InsertInto)

    def __init__(self, *args, **kwargs):
        # Unpack mapping 'values' kwarg into 'columns' and 'values' kwargs.
        # This only happens if the 'columns' kwarg is not already set.
        values_kwarg = kwargs.get('values')
        if 'columns' not in kwargs:
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
        super(Insert, self).__init__(*args, **kwargs)


class Update(Query):
    param_classes = [
        ('update', clauses.Update),
        ('set', clauses.Set),
        ('where', clauses.Where),
    ]
    default_param = ('update', clauses.Update)
    param_aliases = {'set_': 'set'}


class Delete(Query):
    param_classes = [
        ('delete', clauses.DeleteFrom),
        ('where', clauses.Where),
    ]
    default_param = ('delete', clauses.DeleteFrom)
