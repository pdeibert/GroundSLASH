from abc import ABC
from dataclasses import dataclass

from aspy.program.expression import Expr


@dataclass
class Literal(Expr, ABC):
    """Abstract base class for all literals.

    Literals are either aggregates, predicate literals or built-in literals.
    Predicate literals can additionally be indicated with Negation-as-Failure (NaF).
    """
    naf: bool = False