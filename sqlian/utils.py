def sql_format_string_literal(value):
    # TODO: Escape special characters.
    return "'{}'".format(value)


def sql_format_identifier(name):
    # TODO: Escape special characters?
    return '"{}"'.format(name)
