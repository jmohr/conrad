import sqlite3
import tempfile
from nose.tools import raises

import conrad, conrad.db
from conrad import test
from conrad.query import Query, QueryError

import logging
logger = logging.getLogger(__name__)


class MockAdapter(conrad.db.Adapter):
    placeholder = '?'
    lastrowid_function = 'LAST_ROW_ID()'
    def connect(self, *args, **kwargs):
        return
    @classmethod
    def escape(cls, string):
        return string


class TestQuery(object):

    table_name = 'test_data'

    def setup(self):
        """Create a test database with a few records in it."""
        self.database_file = tempfile.NamedTemporaryFile()
        self.database_path = self.database_file.name
        logger.debug('Creating test DB at path: %s' % self.database_path)
        self.cxn = sqlite3.connect(self.database_path)
        self.csr = self.cxn.cursor()
        # Here we pull in one query per line, and execute each one in order.
        # This is because the SQLite cursor can only take one statement
        # at a time.
        create_schema = test.resource_file('test_schema.sql').readlines()
        for line in create_schema:
            self.csr.execute(line)

    def teardown(self):
        """Delete the database and close connections."""
        self.csr.close()
        self.cxn.close()
        logger.debug('Unlinking test database: %s' % self.database_path)
        del self.database_file

    def test_init(self):
        """Test initializing the Query object, just to make sure
        no aggregious exceptions are thrown."""
        q = Query(self.table_name, adapter=MockAdapter)
        assert q is not None

    def test_query_types(self):
        for qtype in ('SELECT', 'INSERT', 'UPDATE', 'DELETE'):
            q = Query(self.table_name, qtype, adapter=MockAdapter)
            assert qtype in q.sql

    def test_default_adapter(self):
        q = Query(self.table_name)
        assert issubclass(q.adapter, conrad.db.Adapter)

    def test_select_stmt(self):
        q = Query(self.table_name, adapter=MockAdapter)
        self.csr.execute(q.sql)
        results = self.csr.fetchall()
        assert len(results) == 2

    @raises(sqlite3.OperationalError)
    def test_nonexist_table(self):
        q = Query('bad_table', adapter=MockAdapter)
        self.csr.execute(q.sql)

    @raises(sqlite3.Warning)
    def test_bad_sql(self):
        q = Query('%s; DROP TABLE %s' % (self.table_name, self.table_name), adapter=MockAdapter)
        self.csr.execute(q.sql)
        self.csr.execute('SELECT * FROM %s' % self.table_name)
        assert len(self.csr.fetchall()) == 2

    @raises(QueryError)
    def test_bad_qtype(self):
        q = Query(self.table_name, 'BAD_ACTION')

    def test_insert(self):
        q = Query(self.table_name, 'INSERT')
        q.set(name='New Guy 1')
        q.set(age=31)
        q.set(birthdate='12/12/1980')
        q.set(active=True)
        q.set(address='456 Sample Way')
        q.set(email='newguy@example.net')
        assert q.sql.startswith('INSERT INTO')
        assert 'VALUES' in q.sql
        assert 'name' in q.sql
        assert 'address' in q.sql

    def test_update(self):
        q = Query(self.table_name, 'UPDATE').filter(name='Test Guy 1')
        q.update(name='Fart Bama Sotero')
        logger.debug('UPDATE SQL: %s' % q.sql)
        assert q.sql.startswith('UPDATE')
        assert 'name' in q.sql
        assert 'Fart Bama Sotero' in q.arguments

    def test_delete(self):
        q = Query(self.table_name, 'DELETE').filter(name='Test Guy 1')
        assert q.sql.startswith("DELETE FROM")
        self.csr.execute(q.sql, q.arguments)
        q = Query(self.table_name).filter(name='Test Guy 1')
        self.csr.execute(q.sql, q.arguments)
        res = self.csr.fetchall()
        assert not res

    def test_chaining(self):
        q = Query(self.table_name).filter(name='Test Guy 2').filter(age=30)
        assert 'name' in q.sql
        assert 'age' in q.sql

