from UserDict import DictMixin

from adapter import default
from table import Table


class Database(DictMixin):
    """A Database represents one connection to a database, with all of its
    tables. A Database instance can be treated as a dictionary of tables.
    By default, the __init__ method uses conrad.adapter.default as its
    adapter, which is a generic ODBC connection. You can pass in another
    adapter to connect to another database type.

    An example:

        >>> import conrad
        >>> db = conrad.Database('MyDSN')
        >>> print db.tables
        {'album': album, 'artist': artist}
        >>> print db['album'].all()
        [{'artist_id':1, 'id':1, ...}]
    """

    def __init__(self, dsn='', adapter=default, **kwargs):
        self.adapter = default
        self.dsn = dsn
        if not self.adapter.connected:
            self.adapter.connect(dsn, **kwargs)
        self.rescan()

    def __repr__(self):
        return 'Database(dsn={})'.format(repr(self.dsn))

    def __getitem__(self, key):
        return self.tables[key]

    def keys(self):
        return self.tables.keys()

    def rescan(self):
        """
        Rescans and repopulates the table hash.
        """
        self.tables = {}
        for name, info in self.adapter.tables.items():
            self.tables[name] = Table(self, info['name'], info['catalog'],
                                                info['schema'])

    def close(self):
        return

