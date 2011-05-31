from conrad.adapter import Base

class TestBase(object):

    def test_methods(self):
        for method in ['connect', 'find', 'update', 'create',
                'delete', 'result_dict']:
            assert hasattr(Base, method), 'Base is missing method {}'.format(
                                                                      method)

    def test_result_dict(self):
        test_tuple = (('one', 111), ('two', 222), ('three', 333))
        d = Base.result_dict(test_tuple)
        for k, v in test_tuple:
            assert d.has_key(k), 'result is missing key "{}"'.format(k)
            assert d[k] == v, 'result[{}] is not {}'.format(k, v)