from .mysql.engines import Engine as MySQLEngine
from .postgresql.engines import Engine as PostgreSQLEngine
from .standard.engines import Engine as StantardEngine


__all__ = [
    'MySQLEngine', 'PostgreSQLEngine', 'StantardEngine',
    'mysql', 'postgresql', 'standard',
]


mysql = MySQLEngine()
postgresql = PostgreSQLEngine()
standard = StantardEngine()
