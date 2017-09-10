from .mysql.engines import Engine as MySQLEngine
from .postgresql.engines import Engine as PostgreSQLEngine
from .sqlite.engines import Engine as SQLiteEngine
from .standard.engines import Engine as StantardEngine


__all__ = [
    'StantardEngine', 'standard',
    'MySQLEngine', 'PostgreSQLEngine', 'SQLiteEngine',
    'mysql', 'postgresql', 'sqlite',
]


standard = StantardEngine()

mysql = MySQLEngine()
postgresql = PostgreSQLEngine()
sqlite = SQLiteEngine()
