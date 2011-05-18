from nose.tools import raises

from conrad.db import load, Adapter


class TestAdapter(object):

    def test_loading(self):
        ODBC = load('ODBC')

    @raises(TypeError)
    def test_abstractosity(self):
        a = Adapter()

    def test_methods(self):
        for method in ['connect', 'execute', 'tables', 'describe']:
            assert hasattr(Adapter, method), "doesn't have method {}".format(method)

    def test_properties(self):
        assert Adapter.placeholder == '?'
        for prop in ['lastrowid']:
            assert hasattr(Adapter, prop), "doesn't have property {}".format(prop)

    def test_escape(self):
        assert Adapter.escape('teststr') == 'teststr'

    def test_row_to_dict(self):
        # TODO: This needs to be tested for real, but pyodbc.Row makes this
        # tricky by not allowing instantiation of Row objects. Fuckers.
        assert hasattr(Adapter, 'row_to_dict')
