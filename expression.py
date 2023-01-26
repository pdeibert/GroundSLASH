from typing import Dict
from abc import ABC, abstractmethod

#from term import Term


class Expr(ABC):
    """Abstract base class for all expressions."""
    
    @abstractmethod
    def substitute(self, subst: Dict[str, "Term"]) -> "Expr":  # type: ignore
        """substitutes the statement by replacing all variables with assigned terms."""
        pass