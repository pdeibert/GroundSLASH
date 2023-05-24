from typing import TYPE_CHECKING, Any, Dict, Optional, Set, Union

from .expression import Expr
from .literals import LiteralCollection, PredLiteral

if TYPE_CHECKING:  # pragma: no cover
    from ground_slash.program.terms import Term, Variable

    from .safety_characterization import SafetyTriplet
    from .statements import Statement


class Query(Expr):
    """Query."""

    def __init__(self, atom: "PredLiteral") -> None:
        self.atom = atom

    def __str__(self) -> str:
        return f"{str(self.atom)} ?"

    def __eq__(self, other: "Any") -> bool:
        return isinstance(other, Query) and self.atom == other.atom

    def __hash__(self) -> int:
        return hash(("query", self.atom))

    @property
    def head(self) -> LiteralCollection:
        return LiteralCollection(self.atom)

    @property
    def body(self) -> LiteralCollection:
        return LiteralCollection()

    @property
    def ground(self) -> bool:
        return self.atom.ground

    def vars(self) -> Set["Variable"]:
        return self.atom.vars()

    def global_vars(self) -> Set["Variable"]:
        return self.atom.global_vars()

    def safety(
        self, statement: Optional[Union["Statement", "Query"]] = None
    ) -> "SafetyTriplet":
        return self.atom.safety(self)

    def substitute(self, subst: Dict[str, "Term"]) -> "Query":  # type: ignore
        return Query(self.atom.substitute(subst))
