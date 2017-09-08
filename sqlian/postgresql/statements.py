# Inject everything from standard SQL.
from sqlian.standard.statements import *    # noqa

from sqlian.standard.statements import (
    __all__,
    Insert as StandardInsert,
    Select as StandardSelect,
)

from .clauses import Locking, Returning


__all__ = __all__


class Insert(StandardInsert):
    param_classes = StandardInsert.param_classes + [
        ('returning', Returning),
    ]


class Select(StandardSelect):
    param_classes = StandardSelect.param_classes + [
        ('locking', Locking),
    ]
