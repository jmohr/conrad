import logging
from UserDict import DictMixin

from conrad.query import Select, Insert, Delete, Update

logger = logging.getLogger(__name__)


class Resource(DictMixin):
    """
    This represents one row in a database table. It is essentially a
    dict which holds the key:value mappings for the row. The resource
    handles tracking changes to an object, and saving said changes to the
    backing datastore. Usually, Resources should not be created directly.
    Rather, you should use the methods on a Table to find or create new
    Resources.

    Let's look at resource usage:

        >>> resource = db['artist'].new(name='Some Guy')
        >>> print resource.new
        True
        >>> resource.save()
        >>> print resource.new
        False
        >>> resource.delete()
        >>> db['artist'].get(resource['id'])
        None
    """

    def __init__(self, table, attributes={}):
        self.table = table
        self.attributes = attributes
        self.new = True
        self.dirty = {}

    def __getitem__(self, key):
        """
        This returns the current object's attribute, merged with the
        dirty attributes. Getting a resource's key will always return the
        in-memory version, which may be different from the on-disk version
        if the resource is dirty or new.
        """
        return dict(self.attributes.items() + self.dirty.items())[key]

    def __setitem__(self, key, value):
        """
        Sets an item, but only if the table has the required column. Will
        raise a KeyError if an invalid column is specified.
        """
        if key not in self.table.columns:
            logger.error('Requested column {}.{} does not exist: {}'.format(
                self.table, key, self.table.columns))
            raise KeyError('Table {} does not have a column named {}'.format(
                    self.table, key))
        self.attributes[key] = value
        self.dirty[key] = value

    def keys(self):
        return self.attributes.keys()

    @property
    def save_required(self):
        """
        Returns True if the resource is dirty or new.
        """
        return bool(self.dirty) or self.new

    @property
    def pk(self):
        """
        Returns this object's primary key.
        """
        return self.attributes[self.table.pk_field]

    def save(self):
        """
        Saves the resource. Does an INSERT if the resource is new (e.g.
        one that was just created, but has not been saved yet) and does an
        UPDATE if the object already exists but has been changed.
        """
        if not self.dirty and not self.new:
            return False
        else:
            if self.new:
                # This resource is new, do an INSERT
                self.dirty = {}
                self.new = False
                pk = Insert(self.table).set(**self.attributes).execute()
                self.attributes[self.table.pk_field] = pk
                return self
            else:
                # This resource is not new, do an UPDATE
                q = Update(self.table).filter(**{self.table.pk_field:self.pk})
                q.set(**self.dirty)
                q.execute()
                self.reload()
                self.dirty = {}
                return self

    def delete(self, force=False):
        """
        Deletes this resource from the database. If force=True, it will
        delete no matter what.
        """
        if not force:
            q = Select(self.table).filter(**{self.table.pk_field:self.pk})
            if len(q) != 1:
                raise ResourceError('Invalid number of resources returned: {} {}'.format(
                        q.statement, q.variables))
        d = Delete(self.table).filter(**{self.table.pk_field:self.pk})
        d.execute()

    def reload(self):
        """
        Reloads the resource's attributes from disk. This gets called
        after an update, to make sure the attributes are all in sync. You
        can call this manually if you are changing data outside of conrad.
        """
        q = Select(self.table).filter(**{self.table.pk_field:self.pk})
        obj = q[0]
        self.attributes = obj.attributes
        self.dirty = {}
        self.new = False
        return self
