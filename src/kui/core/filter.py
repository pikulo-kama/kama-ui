from enum import Enum
from functools import cached_property
from typing import Any, Union


class LogicOperand(Enum):

    OR = "OR"
    AND = "AND"

    def __init__(self, symbol: str):
        self.__symbol = symbol

    @cached_property
    def symbol(self):
        return self.__symbol

    def __str__(self):
        return self.symbol


class FilterOperand(Enum):

    EQ = ("=", False)
    IN = ("IN", True)
    LT = ("<", False)
    GT = (">", False)
    LE = ("<=", False)
    GE = (">=", False)
    NE = ("!=", False)

    def __init__(self, symbol: str, requires_list: bool):
        self.__symbol = symbol
        self.__requires_list = requires_list

    @cached_property
    def symbol(self):
        return self.__symbol

    @cached_property
    def requires_list(self):
        return self.__requires_list

    def __str__(self):
        return self.symbol


class FilterCriterion:

    def __init__(self, field: Union[str | "FilterCriterion"], operand: FilterOperand, value: Any):
        self.__field = field
        self.__operand = operand
        self.__value = value

    @cached_property
    def field(self):
        return self.__field

    @cached_property
    def operand(self):
        return self.__operand

    @cached_property
    def value(self):
        if self.__operand.requires_list:
            return ", ".join(self.__value)

        return self.__value


class KamaFilter:

    def __init__(self, query_object: list[Union[FilterCriterion | LogicOperand]]):
        self.__query = query_object

    def sql(self):

        sql_parts = []

        for statement in self.__query:

            if isinstance(statement, LogicOperand):
                sql_parts.append(statement.symbol)
                continue

            criterion: FilterCriterion = statement
            statement_sql = f"{criterion.field} {criterion.operand.symbol}"

            if criterion.operand.requires_list:
                statement_sql += f"({criterion.field.value})"
            else:
                statement_sql += criterion.field.value

            sql_parts.append(statement_sql)

        return " ".join(sql_parts)


class FilterBuilder:

    def __init__(self):
        self._criteria: list[Union[FilterCriterion | LogicOperand]] = []
        self.__current_field = None

    def where(self, field: str):
        return CriteriaBuilder(self, field)

    def also(self, field: str):
        self._criteria.append(LogicOperand.AND)
        return CriteriaBuilder(self, field)

    def either(self, field: str):
        self._criteria.append(LogicOperand.OR)
        return CriteriaBuilder(self, field)

    def build(self):
        return KamaFilter(self._criteria)



class CriteriaBuilder:

    def __init__(self, filter_builder: FilterBuilder, field: str):

        if field is None:
            raise ValueError("You must call .where() before an operator.")

        self.__filter_builder = filter_builder
        self.__field = field

    def among(self, values: list):
        return self._add_criterion(FilterOperand.IN, values)

    def equals(self, value: Any):
        return self._add_criterion(FilterOperand.EQ, value)

    def _add_criterion(self, operand: FilterOperand, value):

        criterion = FilterCriterion(
            field=self.__field,
            operand=operand,
            value=value
        )

        self.__filter_builder._criteria.append(criterion)  # noqa
        return self.__filter_builder
