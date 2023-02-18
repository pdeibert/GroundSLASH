from typing import Any, Set, Optional, Tuple, TYPE_CHECKING
from abc import ABC, abstractmethod
from copy import deepcopy

from aspy.program.variable_table import VariableTable
from aspy.program.symbol_table import SymbolTable
from aspy.program.expression import Expr

if TYPE_CHECKING:
    from aspy.program.terms import Variable
    from aspy.program.safety_characterization import SafetyTriplet


class Statement(Expr, ABC):
    """Abstract base class for all statements."""
    def __init__(self, var_table: Optional["VariableTable"]=None, *args, **kwargs) -> None:
        self.__var_table = var_table

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

    @property
    @abstractmethod
    def ground(self) -> bool:
        pass

    @property
    def var_table(self) -> "VariableTable":
        if self.__var_table is None:
            self.__init_var_table()

        return self.__var_table

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return self.var_table.vars(global_only)

    def safety(self, rule: Optional["Statement"]=None, global_vars: Optional[Set["Variable"]]=None) -> "SafetyTriplet":
        raise Exception()

    def __init_var_table(self) -> None:

        # initialize variable table
        self.__var_table = VariableTable(self.head.vars().union(self.body.vars()))
        self.__var_table.update(self.body.vars())

        # mark global variables
        self.__var_table.update({var: True for var in self.head.vars(global_only=True).union(self.body.vars(global_only=True))})


class Rule(Statement, ABC):
    """Abstract base class for all rules."""
    @abstractmethod
    def rewrite(self, sym_table: SymbolTable) -> Tuple["Rule"]:
        pass


class Fact(Rule, ABC):
    """Abstract base class for all facts."""
    def rewrite(self) -> Tuple["Fact"]:
        return (deepcopy(self), )