from typing import Tuple, Set, Optional, Union, Iterator, TYPE_CHECKING
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property

from aspy.program.expression import Expr

if TYPE_CHECKING:
    from aspy.program.terms import Variable
    from aspy.program.safety_characterization import SafetyTriplet
    from aspy.program.substitution import Substitution
    from aspy.program.statements import Statement
    from aspy.program.query import Query


@dataclass
class Literal(Expr, ABC):
    """Abstract base class for all literals.

    Literals are either aggregates, predicate literals or built-in literals.
    Predicate literals can additionally be indicated with Negation-as-Failure (NaF).
    """
    naf: bool = False

    @abstractmethod
    def pos(self) -> Set["Literal"]:
        pass

    @abstractmethod
    def neg(self) -> Set["Literal"]:
        pass


class LiteralTuple:
    """Represents a collection of literals."""
    def __init__(self, literals: Optional[Tuple[Literal, ...]]=None) -> None:
        self.literals = literals if not literals is None else tuple()

    def __str__(self) -> str:
        return f"{{{','.join(str(literal) for literal in self.literals)}}}"

    def __len__(self) -> int:
        return len(self.literals)

    def __eq__(self, other: "LiteralTuple") -> bool:
        if len(self) != len(other):
            return False

        for l1, l2 in zip(self, other):
            if l1 != l2:
                return False

        return True

    def __hash__(self) -> int:
        return hash(self.literals)

    def __iter__(self) -> Iterator[Literal]:
        return iter(self.literals)

    def __add__(self, other: "LiteralTuple") -> "LiteralTuple":
        return LiteralTuple(self.literals + other.literals)

    @cached_property
    def ground(self) -> bool:
        return all(literal.ground for literal in self.literals)

    def pos(self) -> Set["Literal"]:
        return set().union(*tuple(literal.pos() for literal in self.literals))

    def neg(self) -> Set["Literal"]:
        return set().union(*tuple(literal.neg() for literal in self.literals))

    def vars(self, global_only=False) -> Tuple[Set["Variable"], ...]:
        return tuple(term.vars(global_only) for term in self.terms)

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> Tuple["SafetyTriplet", ...]:
        return tuple(term.safety() for term in self.terms)

    def substitute(self, subst: "Substitution") -> "LiteralTuple":
        # substitute literals recursively
        literals = (literal.substitute(subst) for literal in self)

        return LiteralTuple(literals)