from dataclasses import dataclass

from expression import Expr
from atom import ClassicalAtom


@dataclass
class Query(Expr):
    """Query."""
    atom: ClassicalAtom

    def __repr__(self) -> str:
        return f"Query({repr(self.atom)})"

    def __str__(self) -> str:
        return f"{str(self.atom)} ?"