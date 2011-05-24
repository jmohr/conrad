from nose.tools import raises

from conrad.query import *


class MockTable(object):
    table = 'tblname'
    table_escaped = 'tblesc'

    def __str__(self):
        return self.table_escaped


class TestQuery(object):

    def setup(self):
        self.table = MockTable()

    def test_select(self):
        q = Select(self.table)
        assert q.statement.startswith('SELECT * FROM')
        assert self.table.table_escaped in q.statement, q.statement

    def test_insert(self):
        q = Insert(self.table)
        assert q.statement.startswith('INSERT INTO')
        assert self.table.table_escaped in q.statement, q.statement

    def test_update(self):
        q = Update(self.table)
        assert q.statement.startswith('UPDATE')
        assert self.table.table_escaped in q.statement, q.statement

    def test_delete(self):
        q = Delete(self.table)
        assert q.statement.startswith('DELETE FROM')
        assert self.table.table_escaped in q.statement, q.statement

    def test_filtering(self):
        q = Select(self.table).filter(name='foobar')
        assert 'WHERE name = ?' in q.statement
        assert 'foobar' in q.variables

    def test_filter_chaining(self):
        q = Select(self.table).filter(name='foobar').filter(name='badabing')
        assert 'foobar' not in q.variables
        assert 'badabing' in q.variables

    def test_limit(self):
        q = Select(self.table).limit(5)
        assert 'LIMIT 5' in q.statement
        q = Select(self.table).limit(lower=5, upper=10)
        assert 'LIMIT 5 5' in q.statement

    @raises(TypeError)
    def test_bad_limit(self):
        Select(self.table).limit(lower=5)

    @raises(ValueError)
    def test_invalid_limit(self):
        Select(self.table).limit(lower=10, upper=5)

    def test_order_by(self):
        q = Select(self.table).order_by('name')
        assert 'ORDER BY name ASC' in q.statement
        q.order_by('email', 'DESC')
        assert 'ORDER BY email DESC' in q.statement
        assert 'ORDER BY name ASC' not in q.statement

    @raises(ValueError)
    def test_bad_order_by(self):
        q = Select(self.table).order_by('ffffuuuuuuu', '; DROP TABLE artist;')

    def test_update_set(self):
        q = Update(self.table, name='ffff', age=30, active=True)
        assert 'ffff' in q.variables
        assert 30 in q.variables
        assert True in q.variables
        assert 'name' in q.statement
        assert 'age' in q.statement
        assert 'active' in q.statement

    def test_update_filter(self):
        q = Update(self.table).filter(id=1).set(name='NO YUO')
        assert 'WHERE id = ?' in q.statement
        assert q.variables[1] == 1
        assert 'name = ?' in q.statement
        assert q.variables[0] == 'NO YUO'

    @raises(AttributeError)
    def test_insert_filter(self):
        q = Insert(self.table).filter(id=1)

    def test_delete_filter(self):
        q = Delete(self.table).filter(id=1)
        assert 'WHERE id = ?' in q.statement
        assert 1 in q.variables


