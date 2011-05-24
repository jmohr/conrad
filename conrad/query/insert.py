from query import Query


class Insert(Query):
    """Implements an INSERT query."""

    template = 'INSERT INTO {table} ({columns}) VALUES ({placeholders})'

    def __init__(self, table=None, **kwargs):
        Query.__init__(self, table)
        self.updates = kwargs

    def set(self, **kwargs):
        """Set a column to a specified value, as supplied by the
        keyword arguments. This is chainable."""
        self.updates.update(kwargs)
        return self

    @property
    def statement(self):
        return self.template.format(
            table = self.table,
            columns = ', '.join(self.updates.keys()),
            placeholders = ', '.join([self.placeholder for v in self.updates])
        ).strip()

    @property
    def variables(self):
        return self.updates.values()
