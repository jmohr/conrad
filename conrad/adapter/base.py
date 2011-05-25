import logging
import pyodbc
from abc import ABCMeta, abstractmethod, abstractproperty

from conrad.utils import plural

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

    placeholder = '?'

    def __init__(self, *args, **kwargs):
        logger.debug('Initializing Base DB adapter')
        if not (args or kwargs):
            logger.debug('No args or kwargs defined')
            self.connection = None
            self.cursor = None
        else:
            logger.debug('Calling connect with args: {} and kwargs: {}'.format(
                    args, kwargs))
            self.connect(*args, **kwargs)

    @property
    def connected(self):
        """
        Returns True if the adapter is connected. This is pretty basic,
        though, and should not be trusted too much.
        """
        return self.connection is not None

    @abstractmethod
    def connect(self, *args, **kwargs):
        """
        Override this in your subclasses. This should set self.connection
        and self.cursor to be DBAPI2.0 compliant objects, as named.
        """
        return

    def execute(self, sql, *args):
        """
        This executes the given SQL string, passing in the remaining args.
        If the statement is a SELECT, return the results. If it is an
        INSERT, return the pk of created item. If it is an UPDATE or
        a DELETE, return None.
        """
        logger.info('Executing SQL query "{}" with args "{}"'.format(
                sql, args))
        self.cursor.execute(sql, *args)
        self.connection.commit()
        if sql.startswith('SELECT'):
            logger.debug('Query starts with SELECT, returning list.')
            return Base.to_dicts(self.cursor.fetchall())
        elif sql.startswith('INSERT'):
            logger.debug('Query starts with INSERT, returning last_id')
            logger.debug('last_inserted_statement is: {}'.format(
                    self.last_inserted_statement))
            self.cursor.execute(self.last_inserted_statement)
            pk = self.cursor.fetchone()[0]
            logger.debug('Found PK "{}" for new row'.format(pk))
            return pk
        else:
            logger.debug('Query is not a SELECT or INSERT, returning None')
            return None

    @classmethod
    def to_dicts(cls, rows):
        """
        Takes DBAPI2.0 Row objects, and turns them into a list of dicts
        consisting of column:value pairs.
        """
        return [dict(zip([r[0] for r in row.cursor_description], row)) for row in rows]

    @property
    def last_inserted_statement(self):
        """
        Override this in your subclass if your target database uses some
        other statement to retreive the ID of the last inserted item.
        """
        return 'SELECT last_insert_rowid() AS last_insert_rowid'

    @property
    def tables(self):
        """
        Returns a dict with an entry for each table in the connected
        database. The dict has the following schema:

            table_name:{
                name: the name of the table,
                catalog: the catalog which contains the table,
                schema: the schema which contains the table,
                type: usually TABLE or VIEW,
                remarks: DB dependent
            }
        """
        logger.debug('Returning table listing for {}'.format(self.connection))
        tables = {}
        for row in self.cursor.tables():
            # The following hacks are due to the fact that pyodbc returns
            # None if the DB doesn't have a catalog or schema, but it
            # doesn't accept None when calling cursor.columns() or
            # cursor.tables(). So, change None to empty string.
            if row.table_schem:
                name = '{}.{}'.format(row.table_schem, row.table_name)
                schema = row.table_schem
            else:
                name = row.table_name
                schema = ''
            if row.table_cat:
                catalog = row.table_cat
            else:
                catalog = ''
            tables[name] = {
                'name': row.table_name,
                'catalog': catalog,
                'schema': schema,
                'type': row.table_type,
                'remarks': row.remarks
            }
        logger.debug('Raw tables: {}'.format(tables))
        return tables

    def describe(self, table, catalog='', schema=''):
        """
        Returns a description of the requested table. Description is a
        dict, where the keys are the column names:

            col_name:{
                catalog: catalog containing this table,
                schema: ditto,
                table: name of the table,
                name: the name of the column,
                type: the data type (i.e. VARCHAR, INT),
                size: the size of the type,
                nullable: 1 if null ok,
                remarks: db dependent
            }
        """
        logger.debug('Describing table: {}'.format(table))
        columns = {}
        try:
            for row in self.cursor.columns(table, catalog, schema):
                if row.table_schem:
                    table_schema = row.table_schem
                else:
                    table_schema = ''
                if row.table_cat:
                    table_catalog = row.table_cat
                else:
                    table_catalog = ''
                columns[row.column_name] = {
                    'name': row.column_name,
                    'catalog': table_catalog,
                    'schema': table_schema,
                    'table': row.table_name,
                    'type': row.type_name,
                    'size': row.column_size,
                    'nullable': row.nullable,
                    'remarks': row.remarks,
                    }
        except pyodbc.Error, e:
            logger.error('Error describing table {}: {}'.format(table, e))
        logger.debug('Raw columns: {}'.format(columns))
        return columns

    def escape(self, string):
        """
        Escape the supplied string, in a format supported by this DB.
        """
        logger.debug('Escaping string: {}'.format(string))
        return string

    def pk(self, table):
        """
        Returns the name of the primary key field in the given table. If
        multiple PKs are present, returns the first.
        """
        logger.debug('Fetching primary keys for table {}'.format(table))
        self.cursor.primaryKeys(table)
        all_pks = self.cursor.fetchall()
        logger.debug('Found all PKs: {}'.format(all_pks))
        logger.debug('Using PK: {}'.format(all_pks[0][3]))
        return all_pks[0][3]

    def fks(self, table):
        """
        Returns a dict of the foreign keys present in a table:

            to_table:{
                to: (table, colname),
                from: (table, colname)
            }

        For convenience, this also sets a key plural(to_table) to ease
        lookup of pluralized relations in the models.
        """
        logger.debug('Fetching foreign keys for table {}'.format(table))
        self.cursor.foreignKeys(table)
        fk_list = {}
        for fk in self.cursor.fetchall():
            logger.debug('Scanning and appending raw fk: {}'.format(fk))
            fk_list[fk[6]] = {'to':(fk[6], fk[7]), 'from':(fk[2], fk[3])}
            fk_list[plural(fk[6])] = fk_list[fk[6]]
        logger.info('Final FK list: {}'.format(fk_list))
        return fk_list
