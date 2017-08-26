from . import clauses, compositions, expressions, functions, queries, values
from .base import Named, Sql, UnescapableError
from .expressions import Ref
from .sql import sql, select, insert, update, delete
from .utils import sql_format_identifier, sql_format_string_literal
from .values import Value, star


__all__ = [
    # Metadata.
    'VERSION', '__version__',

    # Base components.
    'Sql', 'Named', 'UnescapableError',

    # Expose some expressions.
    'Ref', 'Value', 'star',

    # Utilities.
    'sql_format_identifier', 'sql_format_string_literal',

    # Submodules.
    'clauses', 'compositions', 'expressions', 'functions', 'queries', 'values',

    # Convinience functions.
    'sql', 'select', 'insert', 'update', 'delete',
]


VERSION = (0, 1, 0, 'dev')

__version__ = '.'.join(str(p) for p in VERSION)
