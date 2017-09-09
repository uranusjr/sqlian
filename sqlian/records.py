"""The record API and accompanying classes.

Things in this module are strongly inspired by the `Recrods library by Kenneth
Reitz <https://github.com/kennethreitz/records>`__, but with some subtle
differences on how things interact with the database.

.. currentmodule:: sqlian.records
"""

import collections
import json

import six


__all__ = ['Record', 'RecordCollection']


class Record(object):
    """A single row of data from a database.

    You typically don't need to create instances of this class, but interact
    with instances returned by a :class:`sqlian.standard.Database` query.
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
        """How many columns there are in this row.
        """
        return len(self._keys)

    def __eq__(self, other):
        """Test record equality.

        Two records are equal if their keys and values both match.
        Ordering matters.
        """
        try:
            other_keys = other.keys()
            other_vals = other.values()
        except AttributeError:
            return False
        return self.keys() == other_keys and self.values() == other_vals

    def __getitem__(self, key):
        """Access content in the record.

        Records support both numeric (sequence-like) and string (mapping-like)
        indexing.

        Slicing is not supported. Use the :meth:`values` method, which returns
        a slicible object.
        """
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
        """Access content in the record.

        This works like the string indexing of :meth:`__getitem__` to provide
        a simpler syntax under common usage. Always prefer :meth:`__getitem__`
        (the square bracket syntax) if you want to access columns with a
        variable.
        """
        if key in self._key_indexes:
            return self._values[self._key_indexes[key]]
        raise AttributeError(
            "'Record' object has no attribute {!r}".format(key),
        )

    def get(self, key, default=None):
        """Get an item in the record, return `default` on failure.

        This works similarly with the standard mapping interface, but also
        supports numeric indexing.
        """
        try:
            return self[key]
        except (KeyError, IndexError):
            return default

    def keys(self):
        """Returns a sequence containing keys (column names) in this row.

        This works similarly with the standard mapping interface.
        """
        return tuple(self._keys)

    def values(self):
        """Returns a sequence containing values in this row.

        This works similarly with the standard mapping interface.
        """
        return tuple(self._values)

    def items(self):
        """Returns an iterable of 2-tuples containing keys and values.

        This works similarly with the standard mapping interface.
        """
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

    Record collections are backed by record *generators*. Results are fetched
    on demand. This class conforms to the standard sequence interface, and can
    be seamlessly treated as such.
    """
    def __init__(self, record_generator):
        self._row_gen = record_generator
        self._resolved_rows = []
        self._pending = True

    @classmethod
    def from_cursor(cls, cursor):
        """Create a :class:`RecordCollection` from a DB-API 2.0 cursor.

        This method automatically extract useful information for DB-API 2.0
        to generate records. Discrepencies in various interfaces are generally
        taken care of by this method, and you should use it instead of the
        basic constructor when returning records for a database query.
        """
        if isinstance(cursor.description, collections.Sequence):
            keys = tuple(desc[0] for desc in cursor.description)
        else:
            keys = ()
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

            # Resolve a new row if possible.
            elif self._pending:
                try:
                    row = next(self._row_gen)
                except StopIteration:   # TODO: See notes below class.
                    self._pending = False
                    return
                self._resolved_rows.append(row)
                yield row

            else:
                return

            i += 1

    def __getitem__(self, key):
        slicing = isinstance(key, slice)
        stop = key.stop if slicing else key

        # Resolve rows up until the stop marker.
        if self._pending:
            for _ in six.moves.range(stop - len(self._resolved_rows) + 1):
                try:
                    row = next(self._row_gen)
                except StopIteration:   # TODO: See notes below class.
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

    # TODO: Handle non-query errors.
    # DB-API states for `fetchone()`, "an Error (or subclass) exception is
    # raised if the previous call to .execute*() did not produce any result
    # set or no call was issued yet."
    # This means we either (1) Need to "know" a statement doesn't return a
    # result (i.e. is not a query), and don't build a cursor-based collection
    # at all, or (2) Should catch this error here alongside with StopIteration.
    # (1) should be the better approach because we can't really know if the
    # error is caused by an empty execution result, but unfortunately it's
    # also extremely difficult to know upfront whether a statement is a query.
    # For example, INSERT INTO usually is not a query, but can return results
    # with RETURNING; SELECT usually is a query, but doesn't return results if
    # you have an INTO clause). For now we rely on the user to handle this.
