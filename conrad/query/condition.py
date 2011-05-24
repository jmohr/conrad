__all__ = ['gt', 'lt', 'gte', 'lte', 'Condition']


class Condition(object):
    """This is a base class to represent a SQL filtering condition. These
    can be used in a Query.filter clause to implement various equality
    statements. For example, take the following query:

        Select('person').filter(age=30)

    This is great and all, but it will only filter on the exact age. A
    mechanism was needed for implementing other checks. Django handles this
    by doing special checks on the **kwargs that get passed into the
    filter, and the user can append text to the variable name to change
    the comparison. For example, instead of doing "age=30", if you wanted
    to do a greater than comparison, you would do "age__gt=30". This is
    fine, but it doesn't allow the end user to easily create their own
    comparison operators. I found this to be a problem for non-standard
    database servers.

    Conrad implements these comparisons as classes. This allows you to
    subclass the "Condition" class to create your own SQL comparison. A
    Condition has a statement, a variable, and an operator. When the Query
    generates its SQL statement, it will insert the "statement" property
    from any Conditions included in the filters. It will then include the
    value of the "variable" property in the arguments to the adapter. By
    default, the "statement" property is {{name}} {operator} {{placeholder}}
    where operator is just the class' operator property. The name and
    placeholder variables are escaped, and inserted by the Query itself.
    The name is the kwarg that was assigned, and the placeholder is the
    query's placeholder value.

    So, for example, let's use this in a Select:

        Select('person').filter(age=gt(30))

    This filter will return all 'person' rows where `age` > 30. In the
    above description of the "statement", {{name}} is "age" and
    {{placeholder}} is probably "?". In the gt() condition class below,
    the operator is defined as ">". So that's how the Select query can
    generate a SQL query of "SELECT * FROM person WHERE age > 30".
    """

    # Override the operator in subclasses for simple condition modification
    operator = '='

    def __init__(self, variable):
        self.variable = variable

    @property
    def statement(self):
        # Override this property for more extreme conditions
        return '{{name}} {operator} {{placeholder}}'.format(
                operator=self.operator)

    def __repr__(self):
        return self.statement


class GreaterThan(Condition):
    operator = '>'


class LessThan(Condition):
    operator = '<'


class GreaterThanOrEqualTo(Condition):
    operator = '>='


class LessThanOrEqualTo(Condition):
    operator = '<='


gt = GreaterThan
lt = LessThan
gte = GreaterThanOrEqualTo
lte = LessThanOrEqualTo
