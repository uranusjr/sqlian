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

    def __init__(self, *clauses):
        super(Query, self).__init__()
        self.param_clauses = self._map_clause_to_params(clauses)

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
