from query import FilterableQuery


class Delete(FilterableQuery):
    """Implements a DELETE query."""

    template = 'DELETE FROM {table} {conditions}'

    @property
    def statement(self):
        return self.template.format(
            table = self.table,
            conditions = self.where_clause
        ).strip()

    @property
    def variables(self):
        return self.conditions.values()