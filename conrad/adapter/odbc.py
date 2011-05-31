import logging
import pyodbc

logger = logging.getLogger(__name__)

from dbapi2 import DBAPI2

class ODBC(DBAPI2):
    """
    This is a generic PyODBC based adapter.
    """

    def connect(self, dsn, **kwargs):
        logger.info('Connecting to ODBC connection at {}'.format(dsn))
        self.dsn = dsn
        self.connection = pyodbc.connect(dsn, **kwargs)

