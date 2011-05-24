import os

from conrad.test import resource, create_test_database
from conrad import Database


class TestDatabase(object):

    def setup(self):
        self.test_db = create_test_database()
        self.dsn = 'DRIVER={{SQLite3}};DATABASE={}'.format(self.test_db)

    def teardown(self):
        os.unlink(self.test_db)

    def test_db_init(self):
        db = Database(self.dsn)
        assert db is not None

    def test_tables(self):
        db = Database(self.dsn)
        assert db.has_key('artist')
        assert db.has_key('album')

    def test_methods(self):
        db = Database(self.dsn)
        for attr in ['tables', 'rescan']:
            assert hasattr(db, attr), 'db does not have attr {}'.format(attr)

    def test_rescan(self):
        db = Database(self.dsn)
        assert not db.has_key('testtable')
        db.adapter.cursor.execute('CREATE TABLE testtable (id integer primary key, name string)')
        db.rescan()
        assert db.has_key('testtable')

