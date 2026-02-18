from enum import Enum
from functools import cached_property
from typing import Any, Union


class LogicOperand(Enum):
    """
    Enumeration of logical operands used to join filter criteria.
    """

    OR = "OR"
    AND = "AND"

    def __init__(self, symbol: str):
        """
        Initializes the logical operand with its string symbol.

        Args:
            symbol (str): The logical operator string (e.g., 'AND').
        """
        self.__symbol = symbol

    @cached_property
    def symbol(self):
        """
        Returns the string symbol for the operand.
        """
        return self.__symbol

    def __str__(self):
        """
        Returns the string representation of the operand.
        """
        return self.symbol


class FilterOperand(Enum):
    """
    Enumeration of comparison operands for filter criteria.
    """

    EQ = ("=", False)
    IN = ("IN", True)
    LT = ("<", False)
    GT = (">", False)
    LE = ("<=", False)
    GE = (">=", False)
    NE = ("!=", False)

    def __init__(self, symbol: str, requires_list: bool):
        """
        Initializes the filter operand with a symbol and list requirement flag.

        Args:
            symbol (str): The comparison operator symbol (e.g., '=').
            requires_list (bool): Whether the operand expects a list of values.
        """

        self.__symbol = symbol
        self.__requires_list = requires_list

    @cached_property
    def symbol(self):
        """
        Returns the operator symbol.
        """
        return self.__symbol

    @cached_property
    def requires_list(self):
        """
        Returns whether the operand requires a list of values.
        """
        return self.__requires_list

    def __str__(self):
        """
        Returns the string representation of the operand.
        """
        return self.symbol


class FilterCriterion:
    """
    Represents a single filtering rule consisting of a field, operand, and value.
    """

    def __init__(self, field: str, operand: FilterOperand, value: Union[str, int, float]):
        """
        Initializes a filter criterion.

        Args:
            field (str): The data field to filter by.
            operand (FilterOperand): The comparison operator to apply.
            value (Union[str, int, float]): The value to compare against.
        """

        self.__field = field
        self.__operand = operand
        self.__value = value

    @cached_property
    def field(self):
        """
        Returns the field name.
        """
        return self.__field

    @cached_property
    def operand(self):
        """
        Returns the filter operand.
        """
        return self.__operand

    @cached_property
    def value(self):
        """
        Returns the comparison value.
        """
        return self.__value

    def to_sql(self):
        """
        Converts the criterion into a SQL-compatible string.

        Returns:
            str: The formatted SQL snippet for this criterion.
        """

        values = [self.value]
        formatted_values = []

        # Should already be a list.
        if self.operand.requires_list:
            values = self.value

        for value in values:
            if isinstance(value, str):
                value = f"'{value}'"

            formatted_values.append(value)

        value = ", ".join(formatted_values)

        if self.operand.requires_list:
            value = f"({value})"

        return f"{self.field} {self.operand.symbol} {value}"


class KamaFilter:
    """
    An object representing a complete set of filtering criteria and logical operations.
    """

    def __init__(self, query_object: list[Union[FilterCriterion, LogicOperand]]):
        """
        Initializes the filter with a sequence of criteria and operands.

        Args:
            query_object (list): The list of filter components.
        """

        self.__query = query_object

    def get(self, field: str):
        """
        Retrieves the value for a specific field if it exists within the criteria.

        Args:
            field (str): The name of the field to search for.

        Returns:
            Any: The value associated with the field, or None if not found.
        """

        for statement in self.__query:
            if isinstance(statement, FilterCriterion) and statement.field == field:
                return statement.value

        return None

    def to_sql(self):
        """
        Converts the entire filter object into a single SQL string.

        Returns:
            str: The combined SQL query string.
        """

        sql_parts = []

        for statement in self.__query:

            if isinstance(statement, LogicOperand):
                sql_parts.append(statement.symbol)
                continue

            criterion: FilterCriterion = statement
            sql_parts.append(criterion.to_sql())

        return " ".join(sql_parts)


class FilterBuilder:
    """
    Main builder class used to construct KamaFilter objects fluently.
    """

    def __init__(self):
        """
        Initializes an empty filter builder.
        """

        self._criteria: list[Union[FilterCriterion, LogicOperand]] = []
        self.__current_field = None

    def where(self, field: str):
        """
        Starts a new filter query on a specific field.

        Args:
            field (str): The field to apply the first criterion to.

        Returns:
            CriteriaBuilder: A builder to specify the operator and value.
        """
        return CriteriaBuilder(self, field)

    def also(self, field: str):
        """
        Adds an 'AND' operand and starts a new criterion.

        Args:
            field (str): The next field to filter by.

        Returns:
            CriteriaBuilder: A builder to specify the operator and value.
        """

        self._criteria.append(LogicOperand.AND)
        return CriteriaBuilder(self, field)

    def either(self, field: str):
        """
        Adds an 'OR' operand and starts a new criterion.

        Args:
            field (str): The next field to filter by.

        Returns:
            CriteriaBuilder: A builder to specify the operator and value.
        """

        self._criteria.append(LogicOperand.OR)
        return CriteriaBuilder(self, field)

    def build(self):
        """
        Finalizes the building process and returns the constructed KamaFilter.

        Returns:
            KamaFilter: The completed filter object.
        """
        return KamaFilter(self._criteria)


class CriteriaBuilder:
    """
    Helper builder class used to assign operators and values to a specific field.
    """

    def __init__(self, filter_builder: FilterBuilder, field: str):
        """
        Initializes the criteria builder for a specific field.

        Args:
            filter_builder (FilterBuilder): The parent builder.
            field (str): The field being configured.
        """

        if field is None:
            raise ValueError("You must call .where() before an operator.")

        self.__filter_builder = filter_builder
        self.__field = field

    def among(self, values: list):
        """
        Applies an 'IN' operator to the current field.

        Args:
            values (list): The list of acceptable values.

        Returns:
            FilterBuilder: The parent builder for further chaining or building.
        """
        return self.add_criterion(FilterOperand.IN, values)

    def equals(self, value: Any):
        """
        Applies an '=' operator to the current field.

        Args:
            value (Any): The value to match.

        Returns:
            FilterBuilder: The parent builder for further chaining or building.
        """
        return self.add_criterion(FilterOperand.EQ, value)

    def add_criterion(self, operand: FilterOperand, value):
        """
        Internal helper to create a criterion and add it to the parent builder.

        Args:
            operand (FilterOperand): The operator to use.
            value (Any): The value to compare.

        Returns:
            FilterBuilder: The parent builder.
        """

        criterion = FilterCriterion(
            field=self.__field,
            operand=operand,
            value=value
        )

        self.__filter_builder._criteria.append(criterion)  # noqa
        return self.__filter_builder
