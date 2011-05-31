class GenericAdapter(object):

    def test_find(self):
        res = self.adapter.find('artist', {'id':1})
        assert res[0]['name'] == 'James Brown'

    def test_create(self):
        res = self.adapter.create('artist', {'name': 'Mudhoney'})
        print 'got from create: {}'.format(res)
        res = self.adapter.find('artist', {'id': res[0]['id']})
        print '=' * 70
        print res
        print '=' * 70
        assert res[0]['name'] == 'Mudhoney', 'res["name"] is incorrect: {}'.format(res)
