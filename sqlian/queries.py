from . import clauses as c
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

    param_aliases = ()

    def __init__(self, *args):
        super(Query, self).__init__()
        self.param_clauses = self._map_clause_to_params(args)

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

    def _map_clause_to_params(self, clauses):
        param_clauses = {}
        cls_param = {klass: key for key, klass in self.param_classes}
        for clause in clauses:
            no_match = True
            for klass in type(clause).mro():
                try:
                    key = cls_param[klass]
                except KeyError:
                    continue
                if key in param_clauses:
                    raise DuplicateClauseError(clause.sql_name, self.sql_name)
                param_clauses[key] = clause
                no_match = False
                break
            if no_match:
                raise InvalidClauseError(clause.sql_name, self.sql_name)
        return param_clauses


class Select(Query):
    param_classes = [
        ('select', c.Select),
        ('from_', c.From),
        ('where', c.Where),
        ('group_by', c.GroupBy),
        ('order_by', c.OrderBy),
        ('limit', c.Limit),
        ('offset', c.Offset),
    ]
    default_param_class = c.Select
    param_aliases = {
        'group': 'group_by',
        'groupby': 'group_by',
        'order': 'order_by',
        'orderby': 'order_by',
    }


class Insert(Query):
    param_classes = [
        ('insert', c.InsertInto),
        ('columns', c.Columns),
        ('values', c.Values),
    ]
    default_param_class = c.InsertInto


class Update(Query):
    param_classes = [
        ('update', c.Update),
        ('set', c.Set),
        ('where', c.Where),
    ]
    default_param_class = c.Update
    param_aliases = {'set_': 'set'}


class Delete(Query):
    param_classes = [
        ('delete', c.DeleteFrom),
        ('where', c.Where),
    ]
    default_param_class = c.DeleteFrom
