from conrad import query

class TestCondition(object):

    def test_attrs(self):
        for module_attr in ['gt', 'lt', 'gte', 'lte']:
            errmsg = 'condition does not have attr {}'.format(module_attr)
            assert hasattr(query, module_attr), errmsg
        assert hasattr(query.Condition, 'statement')

class TestGreaterThan(object):

    def test_class(self):
        print query.lt
        print query.Condition
        assert issubclass(query.lt, query.Condition)

    def test_sqlgen(self):
        gt = query.gt(5)
        assert gt.statement == '{name} > {placeholder}'
        assert 5 == gt.variable

class TestLessThan(object):

    def test_sqlgen(self):
        lt = query.lt(5)
        assert lt.statement == '{name} < {placeholder}'
        assert 5 == lt.variable

class TestGreaterThanOrEqualTo(object):

    def test_sqlgen(self):
        gte = query.gte(5)
        assert gte.statement == '{name} >= {placeholder}'
        assert 5 == gte.variable

class TestLessThanOrEqualTo(object):

    def test_sqlgen(self):
        lte = query.lte(5)
        assert lte.statement == '{name} <= {placeholder}'
        assert 5 == lte.variable


class TestConditionFilterIntegration(object):

    def test_filtering(self):
        q = query.Select('test_table').filter(name=query.lte(25))
        assert q.variables == [25], 'q.variables is {}, should be [25]'.format(q.variables)
        assert 'name <= ?' in q.statement

    def test_filter_chaining(self):
        q = query.Select('test_table').filter(name=query.gt('foobar')).filter(age=query.lte(33))
        assert 33 in q.variables, q.variables
        assert 'foobar' in q.variables
        assert 'name > ?' in q.statement
        assert 'age <= ?' in q.statement
