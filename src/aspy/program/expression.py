from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Optional, Set, Union

if TYPE_CHECKING:  # pragma: no cover
    from .query import Query
    from .safety_characterization import SafetyTriplet
    from .statements import Statement
    from .terms import Term, Variable


class Expr(ABC):
    """Abstract base class for all expressions."""

    __slots__ = "ground"

    @abstractmethod  # pragma: no cover
    def vars(self) -> Set["Variable"]:  # type: ignore
        pass

    @abstractmethod  # pragma: no cover
    def global_vars(self, statement: Optional["Statement"] = None) -> Set["Variable"]:  # type: ignore # noqa
        pass

    @abstractmethod  # pragma: no cover
    def safety(
        self, rule: Optional[Union["Statement", "Query"]] = None
    ) -> "SafetyTriplet":
        pass

    @abstractmethod  # pragma: no cover
    def substitute(self, subst: Dict[str, "Term"]) -> "Expr":  # type: ignore
        """Substitutes the expression by replacing variables with their assigned terms."""  # noqa
        pass
