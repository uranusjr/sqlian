from sqlian import Sql

from . import clauses as c


__all__ = [
    'StatementError', 'DuplicateClauseError', 'InvalidClauseError',
    'Statement', 'Select', 'Insert', 'Update', 'Delete',
]


class StatementError(ValueError):
    def __init__(self, clause_name, statement_name):
        super(StatementError, self).__init__(self.error_template.format(
            clause=clause_name, statement=statement_name,
        ))
        self.clause_name = clause_name
        self.statement_name = statement_name


class DuplicateClauseError(StatementError):
    error_template = 'duplicate {clause} clauses for statement {statement}'


class InvalidClauseError(StatementError):
    error_template = 'Statement {statement} does not accept clause {clause}'


class Statement(object):

    param_aliases = ()

    def __init__(self, *args):
        super(Statement, self).__init__()
        self.param_clauses = self._map_clause_to_params(args)

    def __repr__(self):
        return '{}({})'.format(
            type(self).__name__,
            ', '.join(
                repr(self.param_clauses[key])
                for key, _ in self.param_classes
                if key in self.param_clauses
            ),
        )

    def __sql__(self, engine):
        return Sql(' ').join(
            engine.as_value(self.param_clauses[key])
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


class Select(Statement):
    sql_name = 'SELECT'
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


class Insert(Statement):
    sql_name = 'INSERT'
    param_classes = [
        ('into', c.InsertInto),
        ('columns', c.Columns),
        ('values', c.Values),
    ]
    default_param_class = c.InsertInto


class Update(Statement):
    sql_name = 'UPDATE'
    param_classes = [
        ('update', c.Update),
        ('set', c.Set),
        ('where', c.Where),
    ]
    default_param_class = c.Update
    param_aliases = {'set_': 'set'}


class Delete(Statement):
    sql_name = 'DELETE'
    param_classes = [
        ('from_', c.DeleteFrom),
        ('where', c.Where),
    ]
    default_param_class = c.DeleteFrom
