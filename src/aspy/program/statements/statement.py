from typing import Optional, Set, TYPE_CHECKING
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property

from aspy.program.expression import Expr
from aspy.program.literals import AggregateLiteral
from aspy.program.safety import Safety

if TYPE_CHECKING:
    from aspy.program.terms import Variable


class Statement(Expr, ABC):
    """Abstract base class for all statements."""
    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass
    
    @property
    @abstractmethod
    def head(self): # TODO: typing:
        pass

    @property
    @abstractmethod
    def body(self): # TODO: typing:
        pass

    @abstractmethod
    def vars(self) -> Set["Variable"]:
        pass

    def global_vars(self) -> Set["Variable"]:
        return self.var_table.variables

    def safety(self, global_vars: Optional[Set["Variable"]]=None) -> Safety:

        if global_vars is None:
            # compute global variables
            global_vars = self.global_vars()

        safeties = tuple([
            literal.safety(global_vars) if isinstance(literal, AggregateLiteral) else literal.safety() for literal in self.body
        ])

        return Safety.closure(safeties)

    @cached_property
    def is_safe(self) -> bool:
        """Checks whether or not the statement is safe."""

        # pre-compute global variables to avoid recomputation
        global_vars = self.global_vars()

        # compute safety characterization of rule
        return (self.safety(global_vars) == Safety(global_vars,set(),set()))

    def is_ground(self) -> bool:
        """Checks whether or not the statement contains any variables."""
        # TODO: cache and dismiss after call to 'substitute'
        return bool(self.global_vars)


@dataclass
class Rule(Statement, ABC):
    """Abstract base class for all rules."""
    pass


class Fact(Rule, ABC):
    """Abstract base class for all facts."""
    pass


# TODO: weight rules? not part of standard (syntactic sugar?)