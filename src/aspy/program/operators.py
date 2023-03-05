from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING: # pragma: no cover
    from aspy.program.terms import Term


class RelOp(Enum):
    """Relational operators."""
    EQUAL           =  "="
    UNEQUAL         = "!="
    LESS            =  "<"
    GREATER         =  ">"
    LESS_OR_EQ      = "<="
    GREATER_OR_EQ   = ">="

    def __str__(self) -> str:
        return self._value_

    def __neg__(self) -> "RelOp":
        """Inverts the comparison operator for switched operands."""
        if(self == RelOp.EQUAL or self == RelOp.UNEQUAL):
            return self
        elif(self == RelOp.LESS):
            return RelOp.GREATER
        elif(self == RelOp.GREATER):
            return RelOp.LESS
        elif(self == RelOp.LESS_OR_EQ):
            return RelOp.GREATER_OR_EQ
        else:
            return RelOp.LESS_OR_EQ

    def __invert__(self) -> "RelOp":
        """Returns the opposite operator."""
        if(self == RelOp.EQUAL):
            return RelOp.UNEQUAL
        elif(self == RelOp.UNEQUAL):
            return RelOp.EQUAL
        elif(self == RelOp.LESS):
            return RelOp.GREATER_OR_EQ
        elif(self == RelOp.GREATER):
            return RelOp.LESS_OR_EQ
        elif(self == RelOp.LESS_OR_EQ):
            return RelOp.GREATER
        else:
            return RelOp.LESS

    def eval(self, lterm: "Term", rterm: "Term") -> bool:
        if(self == RelOp.EQUAL):
            return lterm.precedes(rterm) and rterm.precedes(lterm)
        elif(self == RelOp.UNEQUAL):
            return not (lterm.precedes(rterm) and rterm.precedes(lterm))
        elif(self == RelOp.LESS):
            return lterm.precedes(rterm) and not rterm.precedes(lterm)
        elif(self == RelOp.GREATER):
            return not lterm.precedes(rterm) and rterm.precedes(lterm)
        elif(self == RelOp.LESS_OR_EQ):
            return lterm.precedes(rterm)
        else:
            return rterm.precedes(lterm)


class ArithOp(Enum):
    """Arithmetic operators."""
    PLUS    = '+'
    MINUS   = '-'
    TIMES   = '*'
    DIV     = '/'

    def __str__(self) -> str:
        return self._value_


class AggrOp(Enum):
    """Aggregate operators."""
    COUNT   = "#count"
    SUM     =   "#sum"
    MAX     =   "#max"
    MIN     =   "#min"

    def __str__(self) -> str:
        return self._value_