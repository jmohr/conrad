import os

from conrad.test import resource, create_test_database
from conrad import Database
from conrad.table import Table


class TestTable(object):

    def setup(self):
        self.test_db = create_test_database()
        self.dsn = 'DRIVER={{SQLite3}};DATABASE={}'.format(self.test_db)
        self.db = Database(self.dsn)

    def teardown(self):
        self.db.close()
        os.unlink(self.test_db)

    def test_table_creation(self):
        t = Table(self.db, 'artist')
        assert t is not None
        assert hasattr(t, 'filter')

    def test_columns(self):
        t = Table(self.db, 'artist')
        assert 'name' in t.columns
        assert 'id' in t.columns


