# Inject everything from standard SQL.
from sqlian.standard.queries import *   # noqa

from sqlian.standard.queries import (
    __all__, Query,
    Insert as StandardInsert,
    Select as StandardSelect,
)

from . import clauses as c


__all__ = __all__ + ['Replace']


class Insert(StandardInsert):
    param_classes = StandardInsert.param_classes + [
        ('on_duplicate_key_update', c.OnDuplicateKeyUpdate),
    ]


class Select(StandardSelect):
    param_classes = StandardSelect.param_classes + [
        ('locking', c.Locking),
    ]


class Replace(Query):
    sql_name = 'REPLACE'
    param_classes = [
        ('replace', c.ReplaceInto),
        ('columns', c.Columns),
        ('values', c.Values),
    ]
    default_param_class = c.ReplaceInto
