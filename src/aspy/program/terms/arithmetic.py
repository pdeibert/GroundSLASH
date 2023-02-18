from typing import Set, Union,Optional, Union, Tuple, TYPE_CHECKING
from abc import ABC, abstractmethod
from copy import deepcopy
from functools import cached_property

import aspy
from aspy.program.substitution import Substitution
from aspy.program.symbol_table import SpecialChar
from aspy.program.safety_characterization import SafetyTriplet

from .term import Term, Number, Variable

if TYPE_CHECKING:
    from aspy.program.expression import Expr
    from aspy.program.statements import Statement
    from aspy.program.query import Query
    from aspy.program.variable_table import VariableTable


# TODO: restrictions when substituting ground terms? (or only handle during match?)

class ArithVariable(Variable):
    ground: bool = False

    """Variable replacing an arithmetic term"""
    def __init__(self, id: int, orig_term: "ArithTerm") -> None:
        # check if id is valid
        if aspy.debug() and id < 0:
            raise ValueError(f"Invalid value for {type(self)}: {id}")

        self.val = f"{SpecialChar.TAU}{id}"
        self.id = id
        self.orig_term = orig_term

    def precedes(self, other: Term) -> bool:
        raise Exception("Total order is not defined for arithmetical (auxiliary) variables.")

    def __str__(self) -> str:
        return self.val

    def __eq__(self, other: "Expr") -> str:
        return isinstance(other, ArithVariable) and other.val == self.val and self.orig_term == other.orig_term

    def __hash__(self) -> int:
        return hash(("arith var", self.val, self.orig_term))

    def replace_arith(self, var_table: "VariableTable") -> "ArithVariable":
        return deepcopy(self)


class ArithTerm(Term, ABC):
    """Abstract base class for all arithmetic terms."""
    def precedes(self, other: Term) -> bool:
        if not self.ground:
            raise Exception("Total order is not defined for non-ground arithmetic terms.")

        return Number(self.eval()).precedes(other)

    @ abstractmethod
    def simplify(self) -> "ArithTerm":
        pass

    @abstractmethod
    def eval(self) -> int:
        pass
    
    def match(self, other: "Expr") -> Optional["Substitution"]:
        """Tries to match the expression with another one."""
        if not (self.ground and other.ground):
            raise ValueError("Cannot match non-groun arithmetic terms directly.")

        if isinstance(other, ArithTerm):
            # returns a 'Number' instance since 'other' is ground
            other = other.simplify()

        if not self.simplify() == other:
            return None
        
        return Substitution()

    def replace_arith(self, var_table: "VariableTable") -> Union["ArithTerm", ArithVariable]:
        # replace ground arithmetic term with its value
        if self.ground:
            return self.simplify()

        # replace non-ground arithmetic term with a new special variable
        return var_table.create(SpecialChar.TAU, orig_term=self)


class Minus(ArithTerm):
    """Represents a negation of an arithmetic term."""
    def __init__(self, operand: Union[ArithTerm, Number, "Variable"]) -> None:
        self.operand = operand

    def __eq__(self, other: "Expr") -> bool:
        return isinstance(other, Minus) and self.operand == other.operand

    def __hash__(self) -> int:
        return hash( ("minus", self.operand) )

    def __str__(self) -> str:
        return f"-{f'({str(self.operand)})' if isinstance(self.operand, (Add, Sub, Mult, Div)) else str(self.operand)}"

    @cached_property
    def ground(self) -> bool:
        return self.operand.ground

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return self.operand.vars(global_only)

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> SafetyTriplet:
        return SafetyTriplet(unsafe=self.operand.vars())

    def eval(self) -> int:
        if not self.ground:
            raise Exception("Cannot evaluate non-ground arithmetic term.")

        return -self.operand.eval()

    def substitute(self, subst: "Substitution") -> "Minus":
        return Minus(self.operand.substitute(subst))

    def simplify(self) -> "ArithTerm":
        # simplify operand
        operand = self.operand.simplify()

        # simplified operand is a number
        if isinstance(operand, Number):
            return Number(-operand.val)
        # two negatives cancel each other out
        elif isinstance(operand, Minus):
            return operand.operand
        else:
            return Minus(operand)


class Add(ArithTerm):
    """Represents an addition of arithmetic terms."""
    def __init__(self, loperand: Union[ArithTerm, Number, "Variable"], roperand: Union[ArithTerm, Number, "Variable"]) -> None:
        self.loperand = loperand
        self.roperand = roperand

    def __eq__(self, other: "Expr") -> bool:
        return isinstance(other, Add) and self.loperand == other.loperand and self.roperand == other.roperand

    def __hash__(self) -> int:
        return hash( ("add", self.loperand, self.roperand) )

    def __str__(self) -> str:
        loperand_str = f"{f'({str(self.loperand)})' if isinstance(self.loperand, (Add, Sub, Mult, Div, Minus)) else str(self.loperand)}"
        roperand_str = f"{f'({str(self.roperand)})' if isinstance(self.roperand, (Add, Sub, Mult, Div, Minus)) else str(self.roperand)}"

        return f"{loperand_str}+{roperand_str}"

    @cached_property
    def ground(self) -> bool:
        return self.loperand.ground and self.roperand.ground

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return self.loperand.vars(global_only).union(self.roperand.vars(global_only))

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> SafetyTriplet:
        return SafetyTriplet(unsafe=self.loperand.vars().union(self.roperand.vars()))

    @property
    def operands(self) -> Tuple[Term, Term]:
        return (self.loperand, self.roperand)

    def eval(self) -> int:
        if not self.ground:
            raise Exception("Cannot evaluate non-ground arithmetic term.")

        return self.loperand.eval() + self.roperand.eval()

    def substitute(self, subst: "Substitution") -> "Add":
        # substitute operands recursively
        operands = (operand.substitute(subst) for operand in self.operands)

        return Add(*operands)

    def simplify(self) -> ArithTerm:
        # simplify operands
        loperand = self.loperand.simplify()
        roperand = self.roperand.simplify()

        # if both operands can be simplified to numbers, add them
        if isinstance(loperand, Number) and isinstance(roperand, Number):
            return Number(loperand.val+roperand.val)
        # only left operand is a number
        elif isinstance(loperand, Number):
            # left operand does not add anything
            if loperand.val == 0:
                return roperand
        # only right operand is a number
        elif isinstance(roperand, Number):
            # right operand does not add anything
            if roperand.val == 0:
                return loperand

        # else return an instance of a simplified addition
        return Add(loperand, roperand)


class Sub(ArithTerm):
    """Represents a subtraction of arithmetic terms."""
    def __init__(self, loperand: Union[ArithTerm, Number, "Variable"], roperand: Union[ArithTerm, Number, "Variable"]) -> None:
        self.loperand = loperand
        self.roperand = roperand

    def __eq__(self, other: "Expr") -> bool:
        return isinstance(other, Sub) and self.loperand == other.loperand and self.roperand == other.roperand

    def __hash__(self) -> int:
        return hash( ("sub", self.loperand, self.roperand) )

    def __str__(self) -> str:
        loperand_str = f"{f'({str(self.loperand)})' if isinstance(self.loperand, (Add, Sub, Mult, Div, Minus)) else str(self.loperand)}"
        roperand_str = f"{f'({str(self.roperand)})' if isinstance(self.roperand, (Add, Sub, Mult, Div, Minus)) else str(self.roperand)}"

        return f"{loperand_str}-{roperand_str}"

    @cached_property
    def ground(self) -> bool:
        return self.loperand.ground and self.roperand.ground

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return self.loperand.vars(global_only).union(self.roperand.vars(global_only))

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> SafetyTriplet:
        return SafetyTriplet(unsafe=self.loperand.vars().union(self.roperand.vars()))

    @property
    def operands(self) -> Tuple[Term, Term]:
        return (self.loperand, self.roperand)

    def eval(self) -> int:
        if not self.ground:
            raise Exception("Cannot evaluate non-ground arithmetic term.")

        return self.loperand.eval() - self.roperand.eval()

    def substitute(self, subst: "Substitution") -> "Sub":
        # substitute operands recursively
        operands = (operand.substitute(subst) for operand in self.operands)

        return Sub(*operands)

    def simplify(self) -> Union["Sub", Number]:
        # simplify operands
        loperand = self.loperand.simplify()
        roperand = self.roperand.simplify()

        # if both operands can be simplified to numbers, subtract them
        if isinstance(loperand, Number) and isinstance(roperand, Number):
            return Number(loperand.val-roperand.val)
        # only left operand is a number
        elif isinstance(loperand, Number):
            # left operand does not add anything
            if loperand.val == 0:
                # NOTE: return the negative of the right operand
                return Minus(roperand)
        # only right operand is a number
        elif isinstance(roperand, Number):
            # right operand does not add anything
            if roperand.val == 0:
                return loperand

        # else return an instance of a simplified subtraction
        return Sub(loperand, roperand)


class Mult(ArithTerm):
    """Represents a multiplication of arithmetic terms."""
    def __init__(self, loperand: Union[ArithTerm, Number, "Variable"], roperand: Union[ArithTerm, Number, "Variable"]) -> None:
        self.loperand = loperand
        self.roperand = roperand

    def __eq__(self, other: "Expr") -> bool:
        return isinstance(other, Mult) and self.loperand == other.loperand and self.roperand == other.roperand

    def __hash__(self) -> int:
        return hash( ("mult", self.loperand, self.roperand) )

    def __str__(self) -> str:
        loperand_str = f"{f'({str(self.loperand)})' if isinstance(self.loperand, (Add, Sub, Mult, Div, Minus)) else str(self.loperand)}"
        roperand_str = f"{f'({str(self.roperand)})' if isinstance(self.roperand, (Add, Sub, Mult, Div, Minus)) else str(self.roperand)}"

        return f"{loperand_str}*{roperand_str}"

    @cached_property
    def ground(self) -> bool:
        return self.loperand.ground and self.roperand.ground

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return self.loperand.vars(global_only).union(self.roperand.vars(global_only))

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> SafetyTriplet:
        return SafetyTriplet(unsafe=self.loperand.vars().union(self.roperand.vars()))

    @property
    def operands(self) -> Tuple[Term, Term]:
        return (self.loperand, self.roperand)

    def eval(self) -> int:
        if not self.ground:
            raise Exception("Cannot evaluate non-ground arithmetic term.")

        return self.loperand.eval() * self.roperand.eval()

    def substitute(self, subst: "Substitution") -> "Mult":
        # substitute operands recursively
        operands = (operand.substitute(subst) for operand in self.operands)

        return Mult(*operands)

    def simplify(self) -> ArithTerm:
        # simplify operands
        loperand = self.loperand.simplify()
        roperand = self.roperand.simplify()

        # if both operands can be simplified to numbers, multiply them
        if isinstance(loperand, Number) and isinstance(roperand, Number):
            return Number(loperand.val*roperand.val)
        # only left operand is a number
        elif isinstance(loperand, Number):
            # multiplication by zero
            if loperand.val == 0:
                # only simplify to zero if other operand is grounded
                if not roperand.vars:
                    return Number(0)
            # identity multiplication
            elif loperand.val == 1:
                return roperand
            # negation
            elif loperand.val == -1:
                # check if left operand is already a 'Minus' instance (cancel out)
                if isinstance(roperand, Minus):
                    return roperand.operand

                return Minus(roperand)
        # only right operand is a number
        elif isinstance(roperand, Number):
            # multiplication by zero
            if roperand.val == 0:
                # only simplify to zero if other operand is grounded
                if not loperand.vars:
                    return Number(0)
            # identity multiplication
            elif roperand.val == 1:
                return loperand
            # negation
            elif roperand.val == -1:
                # check if right operand is already a 'Minus' instance (cancel out)
                if isinstance(loperand, Minus):
                    return loperand.operand

                return Minus(loperand)

        # else return an instance of a simplified multiplication
        return Mult(loperand, roperand)


class Div(ArithTerm):
    """Represents a division of arithmetic terms."""
    def __init__(self, loperand: Union[ArithTerm, Number, "Variable"], roperand: Union[ArithTerm, Number, "Variable"]) -> None:
        self.loperand = loperand
        self.roperand = roperand

    def __eq__(self, other: "Expr") -> bool:
        return isinstance(other, Div) and self.loperand == other.loperand and self.roperand == other.roperand

    def __hash__(self) -> int:
        return hash( ("div", self.loperand, self.roperand) )

    def __str__(self) -> str:
        loperand_str = f"{f'({str(self.loperand)})' if isinstance(self.loperand, (Add, Sub, Mult, Div, Minus)) else str(self.loperand)}"
        roperand_str = f"{f'({str(self.roperand)})' if isinstance(self.roperand, (Add, Sub, Mult, Div, Minus)) else str(self.roperand)}"

        return f"{loperand_str}/{roperand_str}"

    @cached_property
    def ground(self) -> bool:
        return self.loperand.ground and self.roperand.ground

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return self.loperand.vars(global_only).union(self.roperand.vars(global_only))

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> SafetyTriplet:
        return SafetyTriplet(unsafe=self.loperand.vars().union(self.roperand.vars()))

    @property
    def operands(self) -> Tuple[Term, Term]:
        return (self.loperand, self.roperand)

    def eval(self) -> int:
        if not self.ground:
            raise Exception("Cannot evaluate non-ground arithmetic term.")

        # NOTE: ASP-Core-2 requires integer division
        return self.loperand.eval() // self.roperand.eval()

    def substitute(self, subst: "Substitution") -> "Div":
        # substitute operands recursively
        operands = (operand.substitute(subst) for operand in self.operands)

        return Div(*operands)

    def simplify(self) -> ArithTerm:
        # simplify operands
        loperand = self.loperand.simplify()
        roperand = self.roperand.simplify()

        # if both operands can be simplified to numbers, divide them
        if isinstance(loperand, Number) and isinstance(roperand, Number):
            if roperand.val == 0:
                raise ArithmeticError("Division by zero detected while simplifying arithmetical term.")

            # NOTE: integer division
            return Number(loperand.val // roperand.val)
        # only left operand is a number
        elif isinstance(loperand, Number):
            # dividing zero
            if loperand.val == 0:
                # only simplify to zero if other operand is grounded
                if not roperand.vars:
                    return Number(0)
        # only right operand is a number
        elif isinstance(roperand, Number):
            # division by zero
            if roperand.val == 0:
                raise ArithmeticError("Division by zero detected while simplifying arithmetical term.")
            elif roperand.val == 1:
                return loperand
            elif roperand.val == -1:
                # check if right operand is already a 'Minus' instance (cancel out)
                if isinstance(loperand, Minus):
                    return loperand.operand

                return Minus(loperand)

        # else return an instance of a simplified division
        return Div(loperand, roperand)