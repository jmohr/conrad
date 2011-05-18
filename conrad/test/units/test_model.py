from nose.tools import raises

from conrad import model, db


class TestModel:

    def test_init(self):
        class MyModel(model.Model):
            pass
        assert MyModel in models.cache

    def test_fields(self):
        class MyModel(model.Model):
            pass
        assert isinstance(MyModel.Meta.fields, dict), '_fields is not a dict'
        for field in ['name', 'age', 'birthdate', 'address', 'active']:
            assert field in MyModel.Meta.fields, '%s not in _fields' % field
            assert isinstance(MyModel.Meta.fields[field], dict), '%s is not Field' % field

    def test_meta(self):
        class MyModel(model.Model):
            pass
        assert hasattr(MyModel, 'Meta')
        for attr in ['pk', 'db', 'table']:
            assert hasattr(MyModel.Meta, attr), 'Meta does not have default %s' % attr
            assert getattr(MyModel.Meta, attr) is not None, 'Meta.%s is None' % attr
        assert MyModel.Meta.pk == 'id'
        assert MyModel.Meta.table == '`mymodel`', 'Meta.table %s is not `mymodel`' % (
                MyModel.Meta.table)
        assert MyModel.Meta.db == db.database

    @raises(ValueError)
    def test_meta_db(self):
        class MyModel(model.Model):
            class Meta:
                db = 'bad'


