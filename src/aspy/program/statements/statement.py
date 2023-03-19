from abc import ABC, abstractmethod
from copy import deepcopy
from functools import cached_property
from typing import TYPE_CHECKING, Any, Dict, Optional, Set, Tuple

from aspy.program.expression import Expr
from aspy.program.literals import AggrLiteral
from aspy.program.variable_table import VariableTable

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.literals import (
        AggrPlaceholder,
        ChoicePlaceholder,
        LiteralCollection,
    )
    from aspy.program.safety_characterization import SafetyTriplet
    from aspy.program.terms import Variable

    from .choice import Choice
    from .special import AggrBaseRule, AggrElemRule, ChoiceBaseRule, ChoiceElemRule


class Statement(Expr, ABC):
    """Abstract base class for all statements.

    Declares some default as well as abstract methods for statements.
    All statements should inherit from this class or a subclass thereof.
    """

    def __init__(
        self, var_table: Optional["VariableTable"] = None, *args, **kwargs
    ) -> None:
        """Initializes the statement instance.

        Should always be called.

        Args:
            var_table: Optional `VariableTable` instance corresponding to the statement.
                Defaults to None.
        """
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
        """Variable table of the statement.

        Initializes variable table from scratch if necessary.

        Returns:
            `VariableTable` instance.
        """
        if self.__var_table is None:
            self.__init_var_table()

        return self.__var_table

    def vars(self) -> Set["Variable"]:
        """Returns the variables associated with the statement.

        Returns:
            Set of 'Variable' instances.
        """
        return self.var_table.vars()

    def global_vars(self, statement: Optional["Statement"] = None) -> Set["Variable"]:
        """Returns the global variables associated with the statement.

        Returns:
            Set of 'Variable' instances.
        """
        return self.var_table.global_vars()

    def safety(self, rule: Optional["Statement"] = None) -> "SafetyTriplet":
        """Returns the safety characterization for the statement.

        For details see Bicheler (2015): "Optimizing Non-Ground Answer Set Programs via Rule Decomposition".

        Args:
            statement: Optional `Statement` or `Query` instance the term appears in.
                Irrelevant for statements. Defaults to `None`.

        Returns:
            `SafetyTriplet` instance.
        """  # noqa
        raise Exception()

    def __init_var_table(self) -> None:
        """Initializes the variable table from scratch."""
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
        """TODO"""
        pass

    @abstractmethod  # pragma: no cover
    def assemble_aggregates(
        self, assembling_map: Dict["AggrPlaceholder", "AggrLiteral"]
    ) -> "Statement":
        """TODO"""
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

    def consequents(self) -> "LiteralCollection":
        return self.head

    def antecedents(self) -> "LiteralCollection":
        return self.body


class Rule(Statement, ABC):
    """Abstract base class for all rules.

    Declares some default as well as abstract methods for rules.
    All rules should inherit from this class or a subclass thereof.
    """

    @cached_property
    def contains_aggregates(self) -> bool:
        return any(isinstance(literal, AggrLiteral) for literal in self.body)
