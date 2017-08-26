from . import clauses, compositions, expressions, functions, queries
from .base import Named, Sql, UnescapableError
from .expressions import Ref
from .sql import sql, select, insert, update, delete
from .utils import sql_format_identifier, sql_format_string_literal


__all__ = [
    # Metadata.
    'VERSION', '__version__',

    # Base components.
    'Sql', 'sql',
    'Named', 'UnescapableError',

    # Expressions.
    'Ref',

    # Utilities.
    'sql_format_identifier', 'sql_format_string_literal',

    # Submodules.
    'clauses', 'compositions', 'expressions', 'functions', 'queries',

    # Convinience functions.
    'sql', 'select', 'insert', 'update', 'delete',
]


VERSION = (0, 1, 0, 'dev')

__version__ = '.'.join(str(p) for p in VERSION)
