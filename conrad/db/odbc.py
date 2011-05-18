import pyodbc

from adapter import Adapter


class ODBC(Adapter):
    """A generic ODBC connection. Subclass this and override escape() and
    lastrowid_field() for different database types."""

    def connect(self, dsn, autocommit=True):
        """Takes a DSN string, and connects to the DB."""
        self.dsn = dsn
        self.connection = pyodbc.connect(self.dsn)
        self.connection.autocommit = autocommit
        self.cursor = self.connection.cursor()

    @classmethod
    def escape(cls, string):
        """For the ODBC class, escape with backticks."""
        return '`{}`'.format(string).lower()

