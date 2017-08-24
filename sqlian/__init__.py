from . import clauses, compositions, expressions, functions, queries
from .base import Named, Sql, UnescapedError, sql
from .expressions import Ref
from .utils import sql_format_identifier, sql_format_string_literal


__all__ = [
    # Metadata.
    'VERSION', '__version__',

    # Base components.
    'Sql', 'sql',
    'Named', 'UnescapedError',

    # Expressions.
    'Ref',

    # Utilities.
    'sql_format_identifier', 'sql_format_string_literal',

    # Submodules.
    'clauses', 'compositions', 'expressions', 'functions', 'queries',

    # Convinience functions.
    'select', 'insert', 'update', 'delete',
]


VERSION = (0, 1, 0, 'dev')

__version__ = '.'.join(str(p) for p in VERSION)


# Convinience functions.

def select(*args, **kwargs):
    return sql(queries.Select(*args, **kwargs))


def insert(*args, **kwargs):
    return sql(queries.Insert(*args, **kwargs))


def update(*args, **kwargs):
    return sql(queries.Update(*args, **kwargs))


def delete(*args, **kwargs):
    return sql(queries.Delete(*args, **kwargs))
