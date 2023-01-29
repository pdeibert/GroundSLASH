from enum import Enum


class CompOp(Enum):
    EQUAL           = 0
    UNEQUAL         = 1
    LESS            = 2
    GREATER         = 3
    LESS_OR_EQ      = 4
    GREATER_OR_EQ   = 5

    def __minus__(self) -> "CompOp":
        """Inverts the comparison operator for switched operands."""
        if(self == CompOp.EQUAL or self == CompOp.UNEQUAL):
            return self
        elif(self == CompOp.LESS):
            return CompOp.GREATER
        elif(self == CompOp.GREATER):
            return CompOp.LESS
        elif(self == CompOp.LESS_OR_EQ):
            return CompOp.GREATER_OR_EQ
        else:
            return CompOp.LESS_OR_EQ

    def __invert__(self) -> "CompOp":
        """Returns the opposite operator."""
        if(self == CompOp.EQUAL):
            return CompOp.UNEQUAL
        elif(self == CompOp.UNEQUAL):
            return CompOp.EQUAL
        elif(self == CompOp.LESS):
            return CompOp.GREATER_OR_EQ
        elif(self == CompOp.GREATER):
            return CompOp.LESS_OR_EQ
        elif(self == CompOp.LESS_OR_EQ):
            return CompOp.GREATER
        else:
            return CompOp.LESS

    def __repr__(self) -> str:
        return f"CompOp({str(self)})"
    
    def __str__(self) -> str:
        if self == CompOp.EQUAL:
            return '='
        elif self == CompOp.UNEQUAL:
            return '!='
        elif self == CompOp.LESS:
            return '<'
        elif self == CompOp.GREATER:
            return '>'
        elif self == CompOp.LESS_OR_EQ:
            return '<='
        else:
            return '>='