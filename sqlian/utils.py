def sql_format_string_literal(value):
    # SQL standard: replace single quotes with pairs of them.
    value = value.replace("'", "''")
    if '\0' in value:   # TODO: Is there a good way to handle this?
        raise ValueError('null character in string')
    return "'{}'".format(value)


def sql_format_identifier(name):
    # TODO: Escape special characters?
    return '"{}"'.format(name)
