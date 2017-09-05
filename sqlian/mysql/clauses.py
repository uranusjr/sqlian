# Inject everything from standard SQL.
from sqlian.standard.clauses import *   # noqa

from sqlian import Sql, UnsupportedParameterError
from sqlian.standard.clauses import __all__, Clause, IdentifierClause


__all__ = __all__ + [
    'Locking', 'ForUpdate', 'LockInShareMode',
    'OnDuplicateKeyUpdate', 'ReplaceInto',
]


ALLOWED_LOCKING_MODES = {
    'FOR UPDATE',
    'LOCK IN SHARE MODE',
}


class Locking(Clause):

    sql_name = 'LOCKING'

    def __init__(self, mode):
        mode_upper = mode.upper()
        super(Locking, self).__init__(mode_upper)
        if mode_upper not in ALLOWED_LOCKING_MODES:
            raise UnsupportedParameterError(mode, 'locking mode')
        self.mode = mode_upper

    def __sql__(self, engine):
        return Sql(self.mode)


class ForUpdate(Locking):
    def __init__(self):
        super(ForUpdate, self).__init__('FOR UPDATE')


class LockInShareMode(Locking):
    def __init__(self):
        super(LockInShareMode, self).__init__('LOCK IN SHARE MODE')


class OnDuplicateKeyUpdate(Clause):
    sql_name = 'ON DUPLICATE KEY UPDATE'


class ReplaceInto(IdentifierClause):
    sql_name = 'REPLACE INTO'
