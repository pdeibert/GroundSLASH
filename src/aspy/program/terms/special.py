from typing import TYPE_CHECKING

import aspy
from aspy.program.symbol_table import SpecialChar
from aspy.program.terms.term import Term

from .term import Variable

if TYPE_CHECKING:
    from aspy.program.expression import Expr
    from aspy.program.terms import ArithTerm


class ArithVariable(Variable):
    ground: bool = False

    """Variable replacing an arithmetic term"""
    def __init__(self, id: int, orig_term: "ArithTerm") -> None:
        # check if id is valid
        if aspy.debug() and id < 0:
            raise ValueError(f"Invalid value for {type(self)}: {id}")

        self.val = f"{SpecialChar.TAU.value}{id}"
        self.id = id
        self.orig_term = orig_term

    def precedes(self, other: "Term") -> bool:
        raise Exception("Total order is not defined for arithmetical (auxiliary) variables.")

    def __str__(self) -> str:
        return self.val

    def __eq__(self, other: "Expr") -> str:
        return isinstance(other, ArithVariable) and other.val == self.val and self.orig_term == other.orig_term

    def __hash__(self) -> int:
        return hash( ("arith var", self.val, self.orig_term) )