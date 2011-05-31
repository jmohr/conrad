from conrad.adapter import ODBC
from conrad.test.units.adapter import GenericAdapter
from conrad.test import resource, create_test_database


class TestODBCAdapter(GenericAdapter):

    def setup(self):
        self.test_db_path = create_test_database()
        self.adapter = ODBC('DRIVER={{SQLite3}};DATABASE={}'.format(
                self.test_db_path))
