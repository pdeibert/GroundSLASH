from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Iterator, Optional, Set, Union

from aspy.program.expression import Expr
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.substitution import AssignmentError, Substitution

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.query import Query
    from aspy.program.statements import Statement
    from aspy.program.terms import Variable
    from aspy.program.variable_table import VariableTable


@dataclass
class Literal(Expr, ABC):
    """Abstract base class for all literals.

    Literals are either aggregates, predicate literals or built-in literals.
    Predicate literals can additionally be indicated with Negation-as-Failure (NaF).
    """

    naf: bool = False

    @abstractmethod  # pragma: no cover
    def pos_occ(self) -> Set["Literal"]:
        pass

    @abstractmethod  # pragma: no cover
    def neg_occ(self) -> Set["Literal"]:
        pass

    @abstractmethod  # pragma: no cover
    def match(self, other: "Expr") -> Optional["Substitution"]:
        """Tries to match the expression with another one."""
        pass

    def global_vars(self, statement: Optional["Statement"] = None) -> Set["Variable"]:
        return self.vars()


class LiteralTuple:
    """Represents a collection of literals."""

    def __init__(self, *literals: Literal) -> None:
        self.literals = tuple(literals)

    def __str__(self) -> str:
        return f"{{{','.join(str(literal) for literal in self.literals)}}}"

    def __len__(self) -> int:
        return len(self.literals)

    def __eq__(self, other: "LiteralTuple") -> bool:
        return (
            isinstance(other, LiteralTuple)
            and len(self) == len(other)
            and frozenset(self.literals) == frozenset(other.literals)
        )

    def __hash__(self) -> int:
        return hash(("literal tuple", frozenset(self.literals)))

    def __iter__(self) -> Iterator[Literal]:
        return iter(self.literals)

    def __add__(self, other: "LiteralTuple") -> "LiteralTuple":
        return LiteralTuple(*self.literals, *other.literals)

    def __getitem__(self, index: int) -> "Literal":
        return self.literals[index]

    @cached_property
    def ground(self) -> bool:
        return all(literal.ground for literal in self.literals)

    def pos_occ(self) -> Set["Literal"]:
        return set().union(*tuple(literal.pos_occ() for literal in self.literals))

    def neg_occ(self) -> Set["Literal"]:
        return set().union(*tuple(literal.neg_occ() for literal in self.literals))

    def vars(self) -> Set["Variable"]:
        return set().union(*tuple(literal.vars() for literal in self.literals))

    def global_vars(self, statement: Optional["Statement"] = None) -> Set["Variable"]:
        return set().union(
            *tuple(literal.global_vars(statement) for literal in self.literals)
        )

    def safety(
        self, rule: Optional[Union["Statement", "Query"]] = None
    ) -> "SafetyTriplet":
        return SafetyTriplet.closure(
            *tuple(literal.safety(rule) for literal in self.literals)
        )

    def without(self, *literals: Literal) -> "LiteralTuple":
        return LiteralTuple(
            *(literal for literal in self.literals if literal not in literals)
        )

    def substitute(self, subst: "Substitution") -> "LiteralTuple":
        if self.ground:
            return deepcopy(self)

        # substitute literals recursively
        literals = (literal.substitute(subst) for literal in self)

        return LiteralTuple(*literals)

    def match(self, other: Expr) -> Optional["Substitution"]:
        # raise Exception("Matching for term tuples is not supported yet.")

        if not (isinstance(other, LiteralTuple) and len(self) == len(other)):
            return None

        subst = Substitution()

        for literal1, literal2 in zip(self.literals, other.literals):
            match = literal1.match(literal2)

            if match is None:
                return None

            try:
                subst = subst + match
            except AssignmentError:
                return None

        return subst

    def replace_arith(self, var_table: "VariableTable") -> "LiteralTuple":
        return LiteralTuple(
            *tuple(literal.replace_arith(var_table) for literal in self.literals)
        )
