from conrad import adapter

def test_module_imports():
    for m in ['Base', 'DBAPI2', 'ODBC']:
        assert hasattr(adapter, m), 'conrad.adapter is missing: {}'.format(m)
    #assert isinstance(adapter.default, adapter.Base)
