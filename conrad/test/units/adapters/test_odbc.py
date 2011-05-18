import logging
import pyodbc
import sqlite3
import tempfile

from conrad.db.odbc import ODBC
from conrad import test

logger = logging.getLogger(__name__)


class TestODBC:

    table_name = 'test_data'
    driver = '{SQLite3}'

    def setup(self):
        """Create a test database with a few records in it."""
        self.database_file = tempfile.NamedTemporaryFile()
        self.database_path = self.database_file.name
        logger.debug('Creating test DB at path: %s' % self.database_path)
        cxn = sqlite3.connect(self.database_path)
        csr = cxn.cursor()
        # Here we pull in one query per line, and execute each one in order.
        # This is because the SQLite cursor can only take one statement
        # at a time.
        create_schema = test.resource_file('test_schema.sql').readlines()
        for line in create_schema:
            csr.execute(line)
        csr.close()
        cxn.close()
        self.dsn = "DRIVER={};DATABASE={}".format(
                self.driver, self.database_path)
        logger.info('Test DSN: {}'.format(self.dsn))

    def teardown(self):
        """Delete the database and close connections."""
        logger.debug('Unlinking test database: %s' % self.database_path)
        del self.database_file

    def test_init_empty(self):
        cxn = ODBC()
        assert cxn is not None
        assert cxn.cursor is None
        assert cxn.connection is None

    def test_init_dsn(self):
        cxn = ODBC(self.dsn)
        assert cxn is not None
        assert cxn.cursor is not None
        assert cxn.connection is not None
        assert isinstance(cxn.connection, pyodbc.Connection)
        assert isinstance(cxn.cursor, pyodbc.Cursor)

    def test_connect(self):
        cxn = ODBC()
        cxn.connect(self.dsn)
        assert isinstance(cxn.connection, pyodbc.Connection)
        assert isinstance(cxn.cursor, pyodbc.Cursor)

    def test_tables(self):
        cxn = ODBC(self.dsn)
        tables = cxn.tables()
        assert 'test_data' in tables
        for key in ['catalog', 'schema', 'name', 'type', 'remarks']:
            assert key in tables['test_data']

    def test_describe(self):
        cxn = ODBC(self.dsn)
        table = cxn.describe('test_data')
        for colname in ['name', 'age', 'birthdate', 'active', 'address', 'email']:
            assert colname in table
        for colname, attributes in table.items():
            for key in ['catalog', 'schema', 'table', 'name', 'type', 'size']:
                assert key in attributes

    def test_lastrowid(self):
        cxn = ODBC(self.dsn)
        sql = """
            INSERT INTO test_data
                    (name, age, birthdate,
                     active, address, email)
                 VALUES
                    (?, ?, ?, ?, ?, ?)"""
        arguments = ('Newguy', 2, '2/3/45', True, '123 Street St.', 'new@guy.com')
        res = cxn.execute_raw(sql, *arguments)
        assert res == [], res
        lrid = cxn.lastrowid
        assert lrid is not None
        guy = cxn.execute_raw('SELECT * FROM test_data WHERE name = ?', 'Newguy')[0]
        assert guy['id'] == lrid

    def test_primary_key(self):
        cxn = ODBC(self.dsn)
        assert cxn.primary_key('test_data') == 'id'

    def test_foreign_key(self):
        cxn = ODBC(self.dsn)
        artist_fks = cxn.foreign_keys('artist')
        assert 'id' in artist_fks[0]['parent']
        assert 'artist' in artist_fks[0]['parent']
        assert 'album' in artist_fks[0]['child']
        assert 'artist_id' in artist_fks[0]['child']
