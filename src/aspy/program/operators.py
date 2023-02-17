from typing import TYPE_CHECKING
from enum import Enum

from aspy.program.literals import Equal, Unequal, Less, Greater, LessEqual, GreaterEqual, AggregateCount, AggregateSum, AggregateMax, AggregateMin
from aspy.program.terms import Add, Sub, Mult, Div

if TYPE_CHECKING:
    from aspy.program.literals import BuiltinLiteral, Aggregate
    from aspy.program.terms import Term, ArithTerm


class RelOp(Enum):
    """Relational operators."""
    ast: type["BuiltinLiteral"]

    def __new__(cls, value: str, ast: type["BuiltinLiteral"]) -> "RelOp":

        obj = object.__new__(cls)
        obj._value_ = value
        # add additional attribute for easy access to corresponding AST class
        obj.ast = ast

        return obj

    EQUAL           =  "=", Equal
    UNEQUAL         = "!=", Unequal
    LESS            =  "<", Less
    GREATER         =  ">", Greater
    LESS_OR_EQ      = "<=", LessEqual
    GREATER_OR_EQ   = ">=", GreaterEqual

    def __str__(self) -> str:
        return self._value_

    def __minus__(self) -> "RelOp":
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
    ast: type["ArithTerm"]

    def __new__(cls, value: str, ast: type["ArithTerm"]) -> "ArithOp":

        obj = object.__new__(cls)
        obj._value_ = value
        # add additional attribute for easy access to corresponding AST class
        obj.ast = ast

        return obj

    PLUS    = '+', Add
    MINUS   = '-', Sub
    TIMES   = '*', Mult
    DIV     = '/', Div

    def __str__(self) -> str:
        return self._value_


class AggrOp(Enum):
    """Aggregate operators."""
    ast: type["Aggregate"]

    def __new__(cls, value: str, ast: type["Aggregate"]) -> "AggrOp":

        obj = object.__new__(cls)
        obj._value_ = value
        # add additional attribute for easy access to corresponding AST class
        obj.ast = ast

        return obj

    COUNT   = "#count", AggregateCount
    SUM     =   "#sum", AggregateSum
    MAX     =   "#max", AggregateMax
    MIN     =   "#min", AggregateMin

    def __str__(self) -> str:
        return self._value_