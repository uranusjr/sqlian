# Inject everything from standard SQL.
from sqlian.standard.clauses import *   # noqa

from sqlian import Sql, UnsupportedParameterError
from sqlian.standard.clauses import __all__, Clause


__all__ = __all__ + ['Locking', 'Returning']


ALLOWED_LOCKING_STRENGTHS = {
    'UPDATE',
    'NO KEY UPDATE',
    'SHARE',
    'KEY SHARE',
}

ALLOWED_LOCKING_OPTIONS = {
    '',
    'NOWAIT',
    'SKIP LOCKED',
}


class Locking(Clause):

    sql_name = 'FOR'

    def __init__(self, strength, ref, option):
        strength_upper = strength.upper()
        option_upper = option.upper()
        super(Locking, self).__init__(strength_upper, ref, option_upper)
        if strength_upper not in ALLOWED_LOCKING_STRENGTHS:
            raise UnsupportedParameterError(strength, 'locking type')
        if option_upper not in ALLOWED_LOCKING_OPTIONS:
            raise UnsupportedParameterError(option, 'locking option')
        self.strength = strength_upper
        self.ref = ref
        self.option = option_upper

    def __sql__(self, engine):
        parts = [Sql('FOR'), Sql(self.strength)]
        if self.ref:
            parts.append(Sql('OF'))
            parts.append(engine.as_value(self.ref))
        if self.option:
            parts.append(Sql(self.option))
        return Sql(' ').join(parts)


class Returning(Clause):
    sql_name = 'RETURNING'
