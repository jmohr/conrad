import logging
import re

from conrad import db

logger = logging.getLogger(__name__)


class QueryError(Exception):
    pass


class Query(object):

    """
    The Query class handles generation and execution of SQL commands for
    a specified model. This class is still pretty basic, in that it doesn't
    yet handle advanced (or rather, non-rudimentary) SQL, such as JOINs
    and comparison operators. These features are planned, however.

    When generating a query, you must provide a Model, which is used
    to introspect table and field names, and also to obtain a database
    object which is compliant with the conrad.db.Adapter interface.

    Using a query directly is pretty simple. Four main query types are
    supported, SELECT, UPDATE, INSERT, and DELETE.

    To do a SELECT:

        >>> all = Query(MyModel)
        >>> print all
        [MyModel(1), MyModel(2)]

    And an INSERT:

        >>> q = Query(MyModel).set(name="Fred", age=40)
        >>> q.save()

    UPDATE:

        >>> q = Query(MyModel).update(name="Froederick")
        >>> q.save()

    And DELETE:

        >>> q = Query(MyModel).filter(name="Froederick")
        >>> q.delete()

    You can filter SELECTs, UPDATEs, and DELETEs, too:

        >>> Query(MyModel).filter(name="Freddy Kreuger")

    And LIMIT them:

        >>> Query(MyModel).limit(10)
        >>> Query(MyModel).limit(start=10, end=20)
        >>> Query(MyModel)[:5]

    And even specify an ORDER:

        >>> Query(MyModel).order('name ASC')

    Most of these modfiers are chainable:

        >>> Query(MyModel).filter(name="Fred Flintstone").update(age=48).save()
    """

    QUERY_TEMPLATES = {
        'SELECT': 'SELECT {select} FROM {table} {conditions} {order} {limit}',
        'UPDATE': 'UPDATE {table} SET {updates} {conditions}',
        'INSERT': 'INSERT INTO {table} {inserts}',
        'DELETE': 'DELETE FROM {table} {conditions}',
    }

    def __init__(self, model):
        logger.debug('Initializing Query for model {}'.format(
                model))

        if hasattr(model, 'Meta'):
            self.model = model
        else:
            raise QueryError('Supplied model must have a "Meta" attr')

        self.type = None
        self._conditions = {}
        self._order = ''
        self._limit = ''
        self._select_attributes = '*'
        self._updates = {}
        self._cache = None

    def __repr__(self):
        return repr(self.execute())

    def __getitem__(self, k):
        """This tries to get the result from the _cache, to speed up
        multiple accesses."""
        if self._cache is not None:
            return self._cache[k]
        # If `k` is an int, assume we are accessing a single object
        # from whatever is returned. If it is a slice, do some fancy
        # limiting.
        if isinstance(k, (int, long)):
            self.limit(k)
            lst = self.execute()
            if not lst:
                return None
            return lst[0]
        elif isinstance(k, slice):
            self.limit(k.stop, k.start)
        else:
            raise ValueError('Limit must be int or slice.')
        return self.execute()

    def __len__(self):
        return len(self.execute())

    def __iter__(self):
        return self.iterator()

    @property
    def sql(self):
        """This property does the gruntwork of putting together the SQL
        query. Where needed, it will pull information from the model's
        database adapter, to make this as agnostic as possible."""
        if not self.type:
            self.type = 'SELECT'
        tpl = self.QUERY_TEMPLATES[self.type]
        context = {'table':self.model.Meta.table,
                   'conditions':self._condition_sql()}
        if self.type == 'SELECT':
            context['select'] = self._select_attributes
            context['limit'] = self._limit
            context['order'] = self._order
        elif self.type == 'UPDATE':
            context['updates'] = self._update_sql()
        elif self.type == 'INSERT':
            context['inserts'] = self._insert_sql()
        return tpl.format(**context).strip()

    @property
    def arguments(self):
        """This property simply returns a list of arguments to be supplied
        to cursor.execute, along with the above SQL property. This list
        is in a specific order to go along with the placeholders in the
        SQL query."""
        return self._update_values() + self._condition_values()

    def _condition_sql(self):
        """Returns a formatted SQL chunk representing a WHERE clause, with
        placeholders and junk."""
        if self._conditions:
            return 'WHERE %s' % ' AND '.join(
                '%s=%s' % (self.model.Meta.db.escape(k),
                    self.model.Meta.db.placeholder) for k in self._conditions)
        else:
            return ''

    def _condition_values(self):
        """Returns the values to go along with the above WHERE statement."""
        return self._conditions.values()

    def _update_sql(self):
        """Returns a chunk of SQL used when doing an UPDATE."""
        return ', '.join('%s=%s' % (self.model.Meta.db.escape(k),
                                    self.placeholder) for k in self._updates)

    def _update_values(self):
        """Ditto, with the values for the above."""
        return self._updates.values()

    def _insert_sql(self):
        """This formats the SQL for an INSERT INTO clause. It uses the values
        from the _update_values() method, since they all go into the same
        variable."""
        insert_tpl = '({columns}) VALUES ({placeholders})'
        columns = ', '.join(self._updates.keys())
        placeholders = ', '.join(self.model.Meta.db.placeholder for v in self._updates.keys())
        return insert_tpl.format(columns=columns, placeholders=placeholders)

    def filter(self, **kwargs):
        """This adds one or more conditions to the WHERE clause on statements
        other than INSERT. You can specify more than one kwarg in a filter
        call, and they will just all get appended to the end of the WHERE
        clause. This method is chainable."""
        if self.type == 'INSERT':
            raise QueryError('filter() cannot be used on an INSERT')
        self._conditions.update(kwargs)
        return self

    def limit(self, end=None, begin=None):
        """Places a LIMIT clause on a SELECT. You can specify just an end, or
        both an end and a begin. This method is chainable."""
        if end:
            if not begin:
                # have an ending, but no beginning, assuming 0
                self._limit = 'LIMIT %s' % int(end)
            else:
                # have begining and ending
                if end <= begin:
                    raise ValueError('Limit end must be greater than begin')
                self._limit = 'LIMIT %s, %s' % (begin, end - begin)
        if begin and not end:
            raise AttributeError('Cannot specify limit `begin` without an `end`')
        return self

    def order_by(self, field, direction='ASC'):
        """Places an ORDER BY clause on the statement. This method is
        chainable."""
        self._order = 'ORDER BY %s %s' % (field, direction)
        return self

    def select(self, *attributes):
        """Limits the attributes returned by a SELECT statement. By default,
        the ORM will do a SELECT *, but if attributes are specified here,
        it will do a SELECT attr1, attr2, attrN FROM ..."""
        if self.type != 'SELECT':
            if not self.type:
                self.type = 'SELECT'
            else:
                raise QueryError('Cannot call set() on {}'.format(self.type))
        if not attributes or attributes[0] == '*':
            self._select_attributes = '*'
        else:
            self._select_attributes = ', '.join(self.model.Meta.db.escape(a) for a in attributes)
        return self

    def update(self, **kwargs):
        """Marks attributes for change in an UPDATE statement. This method
        is chainable."""
        if self.type != 'UPDATE':
            if not self.type:
                self.type = 'UPDATE'
            else:
                raise QueryError('Cannot call set() on {}'.format(self.type))
        self._updates.update(kwargs)
        return self

    def set(self, **kwargs):
        """Similar to the update() method, this sets the attributes on an
        INSERT statement. Chainable as all get out."""
        if self.type != 'INSERT':
            if not self.type:
                self.type = 'INSERT'
            else:
                raise QueryError('Cannot call set() on {}'.format(self.type))
        self._updates.update(kwargs)
        return self

    def delete(self, force=False):
        """Deletes the object(s) specified by the filter conditions. If force
        is False, but no filter conditions are set, an exception will be
        raised, to prevent you from accidentally deleting a whole table."""
        if not self._conditions and not force:
            raise QueryError('Attempt to delete() without filter()ing. Specify force=True to override.')
        if self.type == 'DELETE' or self.type is None:
            self.type = 'DELETE'
            self.execute()
        else:
            raise QueryError('Called delete() on predefined query type')

    def execute(self):
        """Returns the cache if it exists. Otherwise, populates the cache with
        the results of the query, as it is currently defined."""
        if self._cache is None:
            self._cache = list(self.iterator())
        return self._cache

    def iterator(self):
        """Yields the next objet in the execution result list."""
        for result in self.model.Meta.db.execute(self):
            obj = self.model(**result)
            obj._new_record = False
            yield obj

