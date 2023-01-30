from typing import Dict, Optional, Set, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from .terms import Term
    from .variable_set import VariableSet


class AssignmentError(Exception):
    def __init__(self, subst_1: "Substitution", subst_2: "Substitution") -> None:
        super().__init__(f"Substitution {subst_1} is inconsistent with substitution {subst_2}.")


class Substitution(dict):
    def merge(self, other: "Substitution") -> None:
        for var in other.keys():
            if var in self.keys():
                raise AssignmentError(self, other)
            else:
                # integrate assignment
                self[var] = other[var]


class Expr(ABC):
    """Abstract base class for all expressions."""

    @abstractmethod
    def vars(self) -> "VariableSet": # type: ignore
        pass

    @abstractmethod
    def substitute(self, subst: Dict[str, "Term"]) -> "Expr": # type: ignore
        """Substitutes the expression by replacing variables with their assigned terms."""
        pass

    @abstractmethod
    def match(self, other: "Expr", subst: Optional[Substitution]=None) -> Substitution:
        """Tries to match the expression with another one."""
        pass


class MatchError(Exception):
    def __init__(self, candidate: Expr, target: Expr) -> None:
        super().__init__(f"{candidate} cannot be matched to {target}.")