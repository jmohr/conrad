import logging
import pyodbc
from abc import ABCMeta, abstractmethod, abstractproperty

logger = logging.getLogger(__name__)


class Adapter(object):
    """An Adapter class provides an interface to a specific type of SQL
    database, for abstraction purposes. To define your own adapter, you
    must create a class that inherits this Adapter class. Your subclass
    must, at a minimum, define a connect() method which establishes a
    connection to the database, and sets the self.connection and
    self.cursor attributes, as defined by the Python DBAPI2.0 spec[1].
    These attributes are used by the default execute() method.

    Alternately, you can forgo all of the connection/cursor stuff, and
    just define your own connect() and execute() methods from scratch,
    if you are going to create an adapter for a module that doesn't
    abide by the DBAPI2.0 spec.

    [1] http://www.python.org/dev/peps/pep-0249/
    """

    __metaclass__ = ABCMeta

    placeholder = '?'

    def __init__(self, *args, **kwargs):
        if args or kwargs:
            self.connect(*args, **kwargs)
        else:
            self.connection = None
            self.cursor = None

    @abstractmethod
    def connect(self, *args, **kwargs):
        """This method must set self.connection to the DBAPI2 connection,
        and self.cursor to a cursor from said connection. You MUST define
        this abstract method in your implementation."""
        return

    def execute(self, query):
        """Execute the supplied Query object."""
        return self.execute_raw(query.sql, *query.arguments)

    def execute_raw(self, sql, *arguments):
        """Execute the sql statement, substituting placeholders with
        the supplied arguments. By default, this method will just call
        execute() on the cursor, using the DBAPI calls. Override it if
        you are creating an adapter for some weird-assed database module
        that doesn't adhere to the DBAPI spec."""
        self.cursor.execute(sql, *arguments)
        try:
            return Adapter.rows_to_dicts(self.cursor.fetchall())
        except pyodbc.ProgrammingError, e:
            logger.debug('Could not fetchall on cursor: {}'.format(e))
            return []

    def tables(self):
        """Returns a formatted dict containing all tables and their
        metadata."""
        tables = {}
        self.cursor.tables()
        for table in self.cursor.fetchall():
            tables[table[2]] = {
                'catalog':table[0],
                'schema':table[1],
                'name':table[2],
                'type':table[3],
                'remarks':table[4],
            }
        return tables

    def describe(self, table):
        """Given a table name, this method returns a formatted dict
        describing each column in the database."""
        columns = {}
        self.cursor.columns(table)
        for column in self.cursor.fetchall():
            columns[column[3]] = {
                'catalog':column[0],
                'schema':column[1],
                'table':column[2],
                'name':column[3],
                'type':column[5],
                'size':column[6],
            }
        return columns

    def primary_key(self, table):
        self.cursor.primaryKeys(table)
        return self.cursor.fetchone()[3]

    def foreign_keys(self, table):
        self.cursor.foreignKeys(table)
        fks = self.cursor.fetchall()
        return [{'parent':(fk[2],fk[3]),
                 'child':(fk[6],fk[7])} for fk in fks]

    @property
    def lastrowid(self):
        """Returns the value of the primary key field of the last
        inserted row. You may override this property if you need to
        do something really fancy to get it, or you can just change
        lastrowid_function in your subclass."""
        sql = 'select last_insert_rowid() as lastrowid'
        return self.execute_raw(sql)[0]['lastrowid']

    @classmethod
    def escape(cls, string):
        """This classmethod gets called when substituting table and
        column names in SQL queries, to escape them for the database. For
        example, in MySQL databases, you can escape names with backticks,
        but some databases barf on this. By default, this method does
        nothing, but override if you want to transform the string."""
        return string

    @staticmethod
    def row_to_dict(row):
        """Takes one DBAPI2.0 compliant Row object, and turns it into
        a dict in the format of {'col1_name':col1_value,...}"""
        logger.debug('Converting row "{}" to dict.'.format(row))
        colnames = [col[0] for col in row.cursor_description]
        return dict(zip(colnames, row))

    @staticmethod
    def rows_to_dicts(rows):
        """Takes a list of rows (as returned by cursor.fetchall) and
        turns it into a list of dicts. See Adapter.row_to_dict() above."""
        return [Adapter.row_to_dict(row) for row in rows]
