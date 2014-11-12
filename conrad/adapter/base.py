import logging
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)


class Base(object):
    """
    This is a base DB adapter, for a database which implements the
    Python DBAPI2.0 spec. Much more testing needs to be done with this,
    as it currently has only been tested with the ODBC subclass. In theory,
    though, you should be able to create your own adapter by subclassing
    this, and defining the connect() method for whatever database you
    are trying to connect to. Just have it set self.cursor and
    self.connection, and you should be good to go. You can override
    any of the other methods if your database is non-standard or
    if the module doesn't fully implement DBAPI2.0.
    """

    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        logger.debug('Initializing Base DB adapter')
        self.connection = None
        if not (args or kwargs):
            logger.debug('No args or kwargs defined')
        else:
            logger.debug('Calling connect with args: {} and kwargs: {}'.format(
                    args, kwargs))
            self.connect(*args, **kwargs)

    @abstractmethod
    def connect(self, *args, **kwargs):
        return

    @abstractmethod
    def find(self, resource, conditions=None):
        return

    @abstractmethod
    def create(self, resource, attributes=None):
        return

    @abstractmethod
    def update(self, resource, attributes=None, conditions=None):
        return

    @abstractmethod
    def delete(self, resource, conditions=None):
        return

    @classmethod
    def result_dict(cls, results):
        return dict(results)
