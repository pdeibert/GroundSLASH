from typing import Set, TYPE_CHECKING
from dataclasses import dataclass

from .expression import Expr

if TYPE_CHECKING:
    from .terms import Variable
    from .literals import PredicateLiteral


@dataclass
class Query(Expr):
    """Query."""
    atom: PredicateLiteral

    def __repr__(self) -> str:
        return f"Query({repr(self.atom)})"

    def __str__(self) -> str:
        return f"{str(self.atom)} ?"

    def vars(self) -> Set[Variable]:
        return self.atom.vars()