import re

from conrad.db import database, Adapter
from conrad.query import Query


# This list holds all defined models
cache = []


class EmptyMeta(object): pass


class ModelBase(type):
    """
    Takes care of model/database introspection. Uses the model's class
    name and various user-defined Meta attributes to define the model's
    fields.
    """

    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return super(ModelBase, cls).__new__(cls, name, bases, attrs)
        model = type.__new__(cls, name, bases, attrs)

        if not hasattr(model, 'Meta'):
            model.Meta = EmptyMeta()

        # This is the name of the model, for future access in __repr__ and
        # other informational purposes.
        model.Meta.name = name

        # If the user hasn't specifically set Meta.db in their model, use
        # the default database from conrad/db/__init__.py. If the user does
        # define this, it MUST be a valid conrad.db.Adapter implementation.
        if not hasattr(model.Meta, 'db'):
            model.Meta.db = database
        elif not isinstance(model.Meta.db, conrad.db.Adapter):
            raise ValueError, 'Meta.db must be an instance of conrad.db.Adapter()'

        # The Meta.table variable defines which database table will be
        # used by this model. If the user does not define this, it will
        # be set to the name of the class, with the separation of words
        # defined by StudlyCaps, replaced by underscores. For example,
        # if the class is named MyModel, the default Meta.table will be
        # my_model.
        if not hasattr(model.Meta, 'table'):
            table = re.sub(r'([a-z])([A-Z])', r'\1_\2', name).lower()
            model.Meta.table = table
        # This is just the table name as found above, run through the
        # database adapter's escape method.
        model.Meta.escaped_table = model.Meta.db.escape(model.Meta.table)

        # Here, we introspect the primary key from the database, and
        # if it is not found, default to 'id'. Some databases (I'm looking
        # at you, SQLite) do not support primary key introspection.
        # TODO: This PK lookup may be better done on the Adapter side.
        # TODO: This should also be overrideable by the user in their Meta
        model.Meta.db.cursor.primaryKeys(model.Meta.table)
        model.Meta.pk = model.Meta.db.cursor.fetchone()[0]
        if not model.Meta.pk:
            model.Meta.pk = 'id'

        # Ask the adapter to provide all database fields as a dict
        model.Meta.fields = model.Meta.db.describe(model.Meta.table)

        # Toss this model in the cache, and go on our merry way
        cache.append(model)
        return model


class Model(object):
    """
    Subclass this beast to define your models. Most of the database stuff
    will be introspected by the model at runtime, so you don't have to do
    to much here, usually. By default, the name of your model subclass will
    be mangled and used as the name of the database table. For example,
    if you have a class named Person, Conrad will attempt to use `person` as
    the database table. If the class is named NewEmployees, the table will
    be `new_employees`, and so forth.

    A very basic Model would be:

        class MyModel(conrad.Model):
            pass

    This will attempt to introspect the database for defaults.

    You can override some of the defaults by defining a Meta class within
    your Model class, thusly:

        class MyModel(conrad.Model):
            class Meta(object):
                table = 'another_table'
                db = MyCustomAdatper()
                pk = 'employee_id'

    This will use `another_table` as the table name, instead of `my_model`.
    Also, it will instantiate MyCustomAdapter as the database, instead of
    using the default ODBC adapter, and set the pk field to employee_id
    instead of the default `id`.

    Some other things to note, when the model is defined, it will introspect
    the database to discover the fields, which it will store in Meta.fields
    as a dict. Also, the table name, as escaped by the Adapter, will be
    stored in Meta.escaped_table.
    """

    __metaclass__ = ModelBase

    def __init__(self, **kwargs):
        self._dirty = set()
        self._new_record = True
        self._attrs = {}
        self._attrs[self.Meta.pk] = None
        for key, value in kwargs.items():
            self[key] = value

    def __setitem__(self, name, value):
        if name in self.Meta.fields:
            self._attrs[name] = value
            self._dirty.add(name)

    def __getitem__(self, name):
        if name in self._attrs:
            return self._attrs[name]
        else:
            raise AttributeError

    def __repr__(self):
        return u'{}({}={})'.format(self.Meta.name, self.Meta.pk,
                                   self[self.Meta.pk])

    @property
    def dirty(self):
        """If true, the object is dirty and needs saving."""
        return bool(self._dirty)

    @classmethod
    def all(cls):
        """Returns a queryset containing all rows for this model."""
        return Query(cls).select('*')

    @classmethod
    def find(cls, *args, **kwargs):
        """Returns a queryset filtered on specific criteria. If
        an arg is specified, it is assumed to be the pk, and the Query will
        be constructed accordingly. Alternately, if kwargs are specified,
        then they are assumed to be the desired filter parameters. As with
        the all() method, the result of this method can be chained."""
        if args:
            return Query(cls).filter(**{cls.Meta.pk:args[0]})
        elif kwargs:
            return Query(cls).filter(**kwargs)
        else:
            return cls.all()

    def save(self):
        """If the object is dirty, save it."""
        if self.dirty:
            if self._new_record:
                q = Query(self).set(**self._attrs)
            else:
                q = Query(self).update(**self._attrs)
            q.execute()
            self._dirty = set()
            self._new_record = False
        return self

    def delete(self):
        """Delete this object with extreme prejudice."""
        q = Query(self).filter(**{self.Meta.pk:self._attrs[self.Meta.pk]})
        q.delete()
