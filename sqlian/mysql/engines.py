from sqlian.standard.engines import Engine as BaseEngine


class Engine(BaseEngine):

    from . import clauses, statements

    identifier_quote = '`'

    # Shamelessly stolen from `mosql/mysql.py`.
    string_escape_map = {
        # These are escaped in MySQL Connector/C (0.6.2)
        '\0': r'\0',
        '\n': r'\n',
        '\r': r'\r',
        '\\': r'\\',
        '\'': r'\'',
        '\"': r'\"',
        '\x1A': r'\Z',

        # These are escaped in OWASP Enterprise Security API (1.0)
        '\b': r'\b',
        '\t': r'\t',

        # These are not escaped because '\%' and '\_' evaluate repectively to
        # '\%' and '\_' outside of pattern-matching contexts. Programmers
        # should handle their escaping in pattern-matching contexts.
        # '%' : r'\%',
        # '_' : r'\_',
    }

    def escape_string(self, value):
        return ''.join(self.string_escape_map.get(c, c) for c in value)

    def replace(self, *args, **kwargs):
        return self.build_sql(self.statements.Replace, args, kwargs)

    def replace_into(self, *args, **kwargs):
        return self.replace(*args, **kwargs)
