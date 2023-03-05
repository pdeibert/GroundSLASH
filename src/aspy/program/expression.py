from typing import Dict, Set, Union, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod # pragma: no cover

if TYPE_CHECKING: # pragma: no cover
    from .statements import Statement
    from .terms import Term, Variable
    from .substitution import Substitution
    from .safety_characterization import SafetyTriplet
    from .query import Query


class Expr(ABC):
    """Abstract base class for all expressions."""
    __slots__ = ("ground")

    @abstractmethod # pragma: no cover
    def vars(self, global_only: bool=False) -> Set["Variable"]: # type: ignore
        pass

    @abstractmethod # pragma: no cover
    def safety(self, rule: Optional[Union["Statement", "Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> "SafetyTriplet":
        pass

    @abstractmethod # pragma: no cover
    def substitute(self, subst: Dict[str, "Term"]) -> "Expr": # type: ignore
        """Substitutes the expression by replacing variables with their assigned terms."""
        pass

    @abstractmethod # pragma: no cover
    def match(self, other: "Expr") -> Optional["Substitution"]:
        """Tries to match the expression with another one."""
        pass