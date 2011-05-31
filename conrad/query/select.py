from query import FilterableQuery


class Select(FilterableQuery):
    """Implements a SELECT query."""

    template = 'SELECT {select} FROM {table} {conditions} {order} {limit}'

    def __init__(self, table=None, fields=()):
        FilterableQuery.__init__(self, table)
        self.select_fields = fields

    def select(self, *fields):
        if '*' in fields:
            self.select_fields = ()
        else:
            self.select_fields = fields
        return self

    def limit(self, upper, lower=None):
        """Limit the results of the query. If only an upper bound is
        specified, lower is assumed to be 0."""
        if upper and not lower:
            self.limit_clause = 'LIMIT {}'.format(upper)
        elif upper and lower:
            if lower >= upper:
                raise ValueError('lower bound must be less than upper bound')
            self.limit_clause = 'LIMIT {} {}'.format(lower, upper-lower)
        return self

    def order_by(self, field, direction='ASC'):
        """Specify result ordering."""
        if direction not in ['ASC', 'DESC']:
            raise ValueError('direction must be ASC or DESC')
        self.order_by_clause = 'ORDER BY {} {}'.format(field, direction)
        return self

    @property
    def statement(self):
        return self.template.format(
            select = ', '.join(self.select_fields) or '*',
            table = self.table,
            conditions = self.where_clause,
            order = self.order_by_clause,
            limit = self.limit_clause,
        ).strip()

    @property
    def variables(self):
        return self.conditions.values()
