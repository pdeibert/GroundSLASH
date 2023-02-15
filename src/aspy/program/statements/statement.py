from typing import Any
from abc import ABC, abstractmethod

from aspy.program.expression import Expr


class Statement(Expr, ABC):
    """Abstract base class for all statements."""
    @abstractmethod
    def __str__(self) -> str:
        pass

    @property
    @abstractmethod
    def head(self) -> Any:
        pass

    @property
    @abstractmethod
    def body(self) -> Any:
        pass

    @property
    @abstractmethod
    def safe(self) -> bool:
        pass


class Rule(Statement, ABC):
    """Abstract base class for all rules."""
    pass


class Fact(Rule, ABC):
    """Abstract base class for all facts."""
    pass