import collections

import six


def sql_format_string_literal(value):
    # SQL standard: replace single quotes with pairs of them.
    value = value.replace("'", "''")
    if '\0' in value:   # TODO: Is there a good way to handle this?
        raise ValueError('null character in string')
    return "'{}'".format(value)


def sql_format_identifier(name):
    # TODO: Escape special characters?
    return '"{}"'.format(name)


def is_non_string_sequence(s):
    return (
        isinstance(s, collections.Sequence) and
        not isinstance(s, six.string_types)
    )


def is_single_row(iterable):
    return (
        getattr(iterable, '__single_row__', False) or
        any(not is_non_string_sequence(v) for v in iterable)
    )
