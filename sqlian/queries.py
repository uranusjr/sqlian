from . import clauses
from .base import Named, Sql


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
        default_param_args = []
        cls_param = {klass: key for key, klass in self.param_classes}
        param_cls = {key: klass for key, klass in self.param_classes}

        for arg in args:
            no_match = True
            if not hasattr(arg, '__sql__'):
                default_param_args.append(arg)
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
            param_clauses[key] = param_cls[key](arg)

        if default_param_args:
            key, klass = self.default_param
            param_clauses[key] = klass(*default_param_args)
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
        ('values', clauses.Values),
    ]


class Update(Query):
    param_classes = [
        ('update', clauses.Update),
        ('set_', clauses.Set),
        ('where', clauses.Where),
    ]


class Delete(Query):
    param_classes = [
        ('delete', clauses.DeleteFrom),
        ('where', clauses.Where),
    ]
    default_param = ('delete', clauses.DeleteFrom)
