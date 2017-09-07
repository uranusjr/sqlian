import collections
import json

import six


__all__ = ['Record', 'RecordCollection']


class Record(object):
    """A single row of data from a database.
    """
    def __init__(self, keys, values):
        self._keys = keys
        self._key_indexes = dict(zip(keys, range(len(keys))))
        self._values = values

    def __repr__(self):
        return '<Record {}>'.format(json.dumps(collections.OrderedDict(zip(
            self._keys, self._values,
        ))))

    def __len__(self):
        return len(self._keys)

    def __eq__(self, other):
        # Two records are equal if their keys and values match.
        # Ordering matters!
        try:
            other_keys = other.keys()
            other_vals = other.values()
        except AttributeError:
            return False
        return self.keys() == other_keys and self.values() == other_vals

    def __getitem__(self, key):
        # Numeric indexing.
        if isinstance(key, six.integer_types):
            if key < len(self._keys):
                return self.values()[key]
            raise IndexError(key)

        # Key-value access.
        if key in self._key_indexes:
            return self._values[self._key_indexes[key]]
        raise KeyError(key)

    def __getattr__(self, key):
        if key in self._key_indexes:
            return self._values[self._key_indexes[key]]
        raise AttributeError(
            "'Record' object has no attribute {!r}".format(key),
        )

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        return tuple(self._keys)

    def values(self):
        return tuple(self._values)

    def items(self):
        return zip(self._keys, self._values)


class CursorIterator(object):
    """Helper class to iterate through a cursor.

    This class is meant to be used internally to support cursors that does not
    already provide the iterator interface.
    """
    def __init__(self, cursor):
        self.cursor = cursor

    def __iter__(self):
        return self

    def __next__(self):
        row = self.cursor.fetchone()
        if row is not None:
            return row
        raise StopIteration

    # Python 2 compatibility.
    def next(self):
        return self.__next__()


class RecordCollection(object):
    """A sequence of records.
    """
    def __init__(self, record_generator):
        self._row_gen = record_generator
        self._resolved_rows = []
        self._pending = True

    @classmethod
    def from_cursor(cls, cursor):
        """A shorthand to create a `RecordCollection` from a DB-API 2.0 cursor.
        """
        if cursor.description is None:
            return RecordCollection(iter(()))   # Empty collection.
        keys = tuple(desc[0] for desc in cursor.description)
        try:
            it = iter(cursor)
        except AttributeError:
            it = CursorIterator(cursor)
        return cls(Record(keys, row) for row in it)

    def __repr__(self):
        parts = []
        if self._resolved_rows:
            parts.append('{}{} rows'.format(
                len(self._resolved_rows),
                '+' if self._pending else '',
            ))
        if self._pending:
            parts.append('pending')
        return '<RecordCollection ({})>'.format(', '.join(parts))

    def __iter__(self):
        i = 0
        while True:
            # Exhaust the cached result.
            if i < len(self._resolved_rows):
                yield self._resolved_rows[i]

            # Resolve a new row.
            else:
                try:
                    row = next(self._row_gen)
                except StopIteration:
                    self._pending = False
                    return
                self._resolved_rows.append(row)
                yield row

            i += 1

    def __getitem__(self, key):
        slicing = isinstance(key, slice)
        stop = key.stop if slicing else key

        # Resolve rows up until the stop marker.
        if self._pending:
            for _ in six.moves.range(stop - len(self._resolved_rows) + 1):
                try:
                    row = next(self._row_gen)
                except StopIteration:
                    self._pending = False
                    break
                self._resolved_rows.append(row)

        if slicing:
            return type(self)(iter(self._resolved_rows[key]))
        return self._resolved_rows[key]

    def __len__(self):
        if self._pending:
            for _ in self:  # Resolve everything!
                pass
        return len(self._resolved_rows)

    def __bool__(self):
        return len(self) != 0

    # Python 2 compatibility.
    def __nonzero__(self):
        return self.__bool__()
