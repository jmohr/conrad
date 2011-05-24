import logging
from abc import ABCMeta, abstractproperty

from conrad.query import Condition

logger = logging.getLogger(__name__)


class Query(object):
    """Handles generation of various SQL queries, and acts as a repository
    for the results. This class is abstract, and should be subclassed."""

    __metaclass__ = ABCMeta
    placeholder = '?'

    def __init__(self, table):
        logging.debug('Initializing query for table {}'.format(table))
        self.updates = {}
        self.limit_clause = ''
        self.order_by_clause = ''
        self.table = table
        self._cache = None

    def __repr__(self):
        """Returns the cache's __repr__."""
        return repr(self.cache)

    def __len__(self):
        """Returns the length of the cache."""
        return len(self.cache)

    @abstractproperty
    def statement(self):
        """Override this with the code that will generate the SQL statement."""
        return

    @abstractproperty
    def variables(self):
        """Override this with the code that will return the variables, to
        be passed to the cursor's execute() method along with the
        statement."""
        return

    @abstractproperty
    def template(self):
        """This string contains the SQL query template."""
        return

    def all(self):
        return self

    def __getitem__(self, key):
        """Gets the specified item from the cache. You can specify slices
        to get chunks of data."""
        try:
            return self.cache[key]
        except IndexError, e:
            raise IndexError('The query returned {} results, key [{}] is out of range'.format(
                    len(self.cache), key))

    @property
    def cache(self):
        """Keeps an in-memory cache of the results of the query, as executed
        on self.table.database.adapter."""
        if self._cache is None:
            self._cache = list(self.__iter__())
        return self._cache

    def __iter__(self):
        """Allows you to iterate through results, without incurring overhead
        of putting everything in memory. Yay generators!"""
        for row in self.execute():
            resource = self.table(**row)
            resource.new = False
            yield resource

    def execute(self):
        """Executes this query on self.table.database.adapter, and
        returns the results of said query."""
        return self.table.database.adapter.execute(
                self.statement, *self.variables)


class FilterableQuery(Query):
    """This is a query which allows you to filter your set of results. In
    SQL terms, this is any query where you can do a WHERE clause, such
    as SELECTs or UPDATEs."""

    def __init__(self, *args, **kwargs):
        Query.__init__(self, *args, **kwargs)
        self.conditions = {}

    def filter(self, **kwargs):
        """Supply one or more keyword arguments to use as filters. This
        method can be chained."""
        logger.debug('Filtering on "{}"'.format(kwargs))
        for key, value in kwargs.items():
            if issubclass(type(value), Condition):
                logger.debug('Filter statement is Condition')
                sql = value.statement.format(name=key,
                        placeholder=self.placeholder)
                self.conditions[sql] = value.variable
                logger.debug('Adding filter SQL: {}'.format(sql))
                logger.debug('Adding filter variable: {}'.format(value.variable))
            else:
                logger.debug('Filter is not Condition, using raw value: {}'.format(value))
                logger.debug('Filter value is of type {}'.format(type(value)))
                self.conditions['{} = {}'.format(key, self.placeholder)] = value
        logger.debug("After adding filter, conditions: {}".format(self.conditions))
        return self

    @property
    def where_clause(self):
        """Returns a string representing the WHERE clause of the SQL
        statement."""
        if self.conditions:
            clause = 'WHERE {}'.format(' AND '.join(self.conditions.keys()))
            logger.debug('Returning where_clause: {}'.format(clause))
            return clause
        else:
            logger.debug('No conditions specified, returning blank where_clause')
            return ''
