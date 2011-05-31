import logging
from abc import ABCMeta, abstractmethod, abstractproperty

from conrad.utils import plural
from conrad.adapter import Base

logger = logging.getLogger(__name__)


class DBAPI2(Base):
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

    def execute(self, sql, *args):
        """
        This executes the given SQL string, passing in the remaining args.
        If the statement is a SELECT, return the results. If it is an
        INSERT, return the pk of created item. If it is an UPDATE or
        a DELETE, return None.
        """
        logger.info('Executing SQL query "{}" with args "{}"'.format(
                sql, args))
        cursor = self.connection.cursor()
        result = []
        try:
            cursor.execute(sql, *args)
            self.connection.commit()
            result = cursor.fetchall()
        except Exception, e:
            logger.debug('Error while executing SQL statement: {}'.format(e))
        finally:
            cursor.close()
        return result

    def find(self, resource, conditions={}, columns=[],
                order_by=None, limit=None):
        table = self.escape(resource)
        if not columns:
            columns = '*'
        else:
            columns = ', '.join([self.escape(c) for c in columns])
        cmd_args = []
        where_clause_elements = []
        for k, v in conditions.items():
            where_clause_elements.append('{} = {}'.format(
                                self.escape(k), self.placeholder))
            cmd_args.append(v)
        if where_clause_elements:
            where_clause = ' WHERE ' + ' AND '.join(where_clause_elements)
        else:
            where_clause = ''
        if order_by:
            order_by_clause = 'ORDER BY {}'.format(self.escape(order_by))
        else:
            order_by_clause = ''
        if limit:
            if isinstance(limit, (int, long)):
                limit_clause = 'LIMIT {}'.format(limit)
            elif isinstance(limit, tuple):
                limit_clause = 'LIMIT {} {}'.format(*limit)
            else:
                raise ValueError('limit must be int or tuple')
        else:
            limit_clause = ''
        sql = 'SELECT {} FROM {} {} {} {}'.format(
                columns, self.escape(table), where_clause,
                order_by_clause, limit_clause).strip()
        res = self.execute(sql, *cmd_args)
        if res:
            logger.debug('Got command result: {}'.format(res))
            return [self.result_dict(r) for r in res]
        else:
            return []

    def create(self, table, arguments={}):
        logger.debug('Creating {} with {}'.format(table, arguments))
        table = self.escape(table)
        if arguments:
            sql_args = []
            columns = []
            for k, v in arguments.items():
                columns.append("'{}'".format(k))
                sql_args.append(v)
            args_clause = '({}) VALUES ({})'.format(
                ', '.join(columns),
                ', '.join([self.placeholder for c in columns]))
        else:
            raise Exception('Must specify arguments for create')
        sql = 'INSERT INTO {} {}'.format(
            table, args_clause)
        logger.debug('raw SQL query: {}'.format(sql))
        self.execute(sql, sql_args)
        lastid = self.get_inserted_id(table)
        res = self.find(table, conditions={self.pk(table):lastid})
        return res


    def update(self, table, arguments={}, conditions={}):
        table = self.escape(table)


    def delete(self, table, conditions={}):
        table = self.escape(table)
        where, args = self._generate_where(conditions)
        sql = 'DELETE FROM {} {}'.format(
                table, where)
        self.execute(sql, args)

    def _generate_where(self, conditions):
        if not conditions:
            return ''
        attrs = []
        args = []
        for k, v in conditions.items():
            attrs.append('{} = {}'.format(self.escape(k), self.placeholder))
            args.append(v)
        sql = 'WHERE ' + ' AND '.join(attrs)
        return sql, args

    def get_inserted_id(self, table):
        sql = 'SELECT last_insert_rowid() as lastid'
        res = self.execute(sql)
        logger.debug('found upserted id: {}'.format(res[0][0]))
        return res[0][0]

    @classmethod
    def result_dict(cls, row):
        """
        Takes DBAPI2.0 Row object, and turns them into a list of dicts
        consisting of column:value pairs.
        """
        logger.debug('Converting {} to dict'.format(row))
        try:
            d = dict(zip([r[0] for r in row.cursor_description], row))
            logger.debug('Converted to dict: {}'.format(d))
            return d
        except AttributeError, e:
            logger.error('Could not convert row to dict: {} ({})'.format(
                row, type(row)))
            return {}

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
        logger.debug('Returning table listing for {}'.format(self))
        tables = {}
        cursor = self.connection.cursor()
        for row in cursor.tables():
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
        cursor.close()
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
        cursor = self.connection.cursor()
        cursor.primaryKeys(table)
        all_pks = cursor.fetchall()
        cursor.close()
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
