from abc import ABC, abstractmethod
from copy import deepcopy
from functools import cached_property
from typing import TYPE_CHECKING, Any, Dict, Optional, Set, Tuple

from aspy.program.expression import Expr
from aspy.program.literals import AggrLiteral
from aspy.program.variable_table import VariableTable

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.literals import AggrPlaceholder, ChoicePlaceholder, LiteralTuple
    from aspy.program.safety_characterization import SafetyTriplet
    from aspy.program.terms import Variable

    from .choice import Choice
    from .special import AggrBaseRule, AggrElemRule, ChoiceBaseRule, ChoiceElemRule


class Statement(Expr, ABC):
    """Abstract base class for all statements."""

    def __init__(
        self, var_table: Optional["VariableTable"] = None, *args, **kwargs
    ) -> None:
        self.__var_table = var_table

    @abstractmethod  # pragma: no cover
    def __str__(self) -> str:
        pass

    @property
    @abstractmethod  # pragma: no cover
    def head(self) -> Any:
        pass

    @property
    @abstractmethod  # pragma: no cover
    def body(self) -> Any:
        pass

    @property
    @abstractmethod  # pragma: no cover
    def safe(self) -> bool:
        pass

    @property
    @abstractmethod  # pragma: no cover
    def ground(self) -> bool:
        pass

    @property
    def var_table(self) -> "VariableTable":
        if self.__var_table is None:
            self.__init_var_table()

        return self.__var_table

    def vars(self) -> Set["Variable"]:
        return self.var_table.vars()

    def global_vars(self, statement: Optional["Statement"] = None) -> Set["Variable"]:
        return self.var_table.global_vars()

    def safety(self, rule: Optional["Statement"] = None) -> "SafetyTriplet":
        raise Exception()

    def __init_var_table(self) -> None:

        # initialize variable table
        self.__var_table = VariableTable(self.head.vars().union(self.body.vars()))

        # mark global variables
        self.__var_table.update(
            {
                var: True
                for var in self.head.global_vars(self).union(
                    self.body.global_vars(self)
                )
            }
        )

    @abstractmethod  # pragma: no cover
    def rewrite_aggregates(
        self,
        aggr_counter: int,
        aggr_map: Dict[
            int,
            Tuple[
                "AggrLiteral",
                "AggrPlaceholder",
                "AggrBaseRule",
                Set["AggrElemRule"],
            ],
        ],
    ) -> "Statement":
        pass

    @abstractmethod  # pragma: no cover
    def assemble_aggregates(
        self, assembling_map: Dict["AggrPlaceholder", "AggrLiteral"]
    ) -> "Statement":
        pass

    def rewrite_choices(
        self,
        choice_counter: int,
        choice_map: Dict[
            int,
            Tuple[
                "Choice",
                "ChoicePlaceholder",
                "ChoiceBaseRule",
                Set["ChoiceElemRule"],
            ],
        ],
    ) -> "Statement":
        return deepcopy(self)

    def assemble_choices(
        self,
        assembling_map: Dict["ChoicePlaceholder", "Choice"],
    ) -> "Statement":
        return deepcopy(self)

    def consequents(self) -> "LiteralTuple":
        return self.head

    def antecedents(self) -> "LiteralTuple":
        return self.body


class Rule(Statement, ABC):
    """Abstract base class for all rules."""

    @cached_property
    def contains_aggregates(self) -> bool:
        return any(isinstance(literal, AggrLiteral) for literal in self.body)


class Fact(Rule, ABC):
    """Abstract base class for all facts."""

    contains_aggregates: bool = False

    def rewrite_aggregates(
        self,
        aggr_counter: int,
        aggr_map: Dict[
            int,
            Tuple[
                "AggrLiteral",
                "AggrPlaceholder",
                "AggrBaseRule",
                Set["AggrElemRule"],
            ],
        ],
    ) -> "Fact":
        return deepcopy(self)

    def assemble_aggregates(
        self, assembling_map: Dict["AggrPlaceholder", "AggrLiteral"]
    ) -> "Fact":
        return deepcopy(self)
