from query import FilterableQuery


class Update(FilterableQuery):
    """Implements an UPDATE query."""

    template = 'UPDATE {table} SET {updates} {conditions}'

    def __init__(self, table=None, **kwargs):
        FilterableQuery.__init__(self, table)
        self.updates = kwargs

    def set(self, **kwargs):
        """Similar to Insert.set(), this will update a column's value."""
        self.updates.update(kwargs)
        return self

    @property
    def statement(self):
        update_list = ['{} = {}'.format(k, self.placeholder) for k in self.updates.keys()]
        return self.template.format(
            table = self.table,
            updates = ', '.join(update_list),
            conditions = self.where_clause
        ).strip()

    @property
    def variables(self):
        return self.updates.values() + self.conditions.values()
