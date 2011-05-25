import logging
import pyodbc

logger = logging.getLogger(__name__)

from base import Base

class ODBC(Base):
    """
    This is a generic PyODBC based adapter.
    """

    def connect(self, dsn, **kwargs):
        logger.info('Connecting to ODBC connection at {}'.format(dsn))
        self.dsn = dsn
        self.connection = pyodbc.connect(dsn, **kwargs)
        self.cursor = self.connection.cursor()


