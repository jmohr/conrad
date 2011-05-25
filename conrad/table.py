import logging

from conrad.query import Select
from conrad.resource import Resource


logger = logging.getLogger(__name__)


class Table(object):
    """
    Represents one table in the database. The Table object exposes methods
    such as filter(), get(), and create() to the user. This is where you will
    handle most of the work of finding and making new resources in the DB.

    Take this example:

        db = Database('MyDSN')
        artists = db['artist']
        print artists.all()
        [{'id':1, 'name':...}]
        johnny = artists.create(name="Johnny Cash")
        print johnny
        {'id':7, 'name':'Johnny Cash'}
        some_artists = artists.filter(id=gte(4))
        print some_artists
        [{'id':4,...}]

    A table will often return Queries, which are made up of many
    lazy-loaded Resources. Some methods -- such as get() -- return a single
    Resource. Think of a Table as a way of finding and managing Resources.
    """

    def __init__(self, database, table, catalog='', schema=''):
        logger.debug('Defining table {} with catalog {} and schema {}'.format(
                table, catalog, schema))
        self.table = table
        self.catalog = catalog
        self.schema = schema
        if schema:
            self.escaped_table = database.adapter.escape(
                    '.'.join((schema,table)))
        else:
            self.escaped_table = database.adapter.escape(table)
        self.database = database
        #self.rescan()
        self._columns = None

    @property
    def columns(self):
        if self._columns is None:
            self.rescan()
        return self._columns

    def rescan(self):
        """
        Rescans the tables column listing. These values are used for
        validation checking.
        """
        self._columns = self.database.adapter.describe(
                self.table, self.catalog, self.schema).keys()

    def filter(self, **kwargs):
        """
        Filter the contents of the table, and return the results.
        """
        q = Select(self).filter(**kwargs)
        return q

    def get(self, pk):
        """
        Gets a specific entry in the table by primary key.
        """
        return Select(self).filter(**{self.pk_field:pk})[0]

    def new(self, **kwargs):
        """
        Create a new resource with the values set to **kwargs, but don't
        save the resource.
        """
        return Resource(self, kwargs)

    def create(self, **kwargs):
        """
        Same as new(), but this will save the resource.
        """
        return self.new(**kwargs).save()

    def all(self):
        """
        Returns all resources in the table.
        """
        return Select(self)

    @property
    def pk_field(self):
        """
        The name of the Primary Key column.
        """
        return self.database.adapter.pk(self.table)

    def __call__(self, **kwargs):
        """
        Convenience method to make a new resource for this table. Simply
        calls the new() method.
        """
        return self.new(**kwargs)

    def __str__(self):
        return self.escaped_table

    def __repr__(self):
        return 'Table({})'.format(repr(self.table))
