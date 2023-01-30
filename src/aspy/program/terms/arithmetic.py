from typing import Optional, Union, Set, Dict, TYPE_CHECKING
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass

from sympy import solve # type: ignore
from sympy import Expr as SympyExpr # type: ignore

from aspy.program.expression import Substitution, MatchError
from aspy.program.safety import Safety
from aspy.program.variable_set import VariableSet
from .term import Term, Number

if TYPE_CHECKING:
    from aspy.program.expression import Expr


class ArithOp(Enum):
    PLUS    = 0
    MINUS   = 1
    TIMES   = 2
    DIV     = 3

    def __repr__(self) -> str:
        return f"ArithOp({str(self)})"

    def __str__(self) -> str:
        if self == ArithOp.PLUS:
            return '+'
        elif self == ArithOp.MINUS:
            return '-'
        elif self == ArithOp.TIMES:
            return '*'
        else:
            return '/'


class ArithTerm(Term, ABC):
    def __lshift__(self, other: Term) -> bool:
        return self.evaluate() << other

    @abstractmethod
    def evaluate(self) -> Number:
        pass

    @abstractmethod
    def sympy(self) -> SympyExpr:
        pass

    def safety(self) -> Safety:
        return Safety(VariableSet(), self.vars(), set())

    def match(self, other: "Expr", subst: Optional[Substitution]=None) -> Substitution:
        if subst is None:
            subst = Substitution()

        # simplify arithmetical expression first
        simple_term = self.simplify()

        # since we are dealing with ground atoms, the other expression must be an evaluated number
        if isinstance(other, Number):
            # compute sympy expression from arithmetical term
            expr = simple_term.sympy()

            # get variables in expression
            variables = list(expr.free_symbols)

            if len(variables) > 1:
                raise Exception("Cannot match arithmetical expression with multiple variables.")

            # solve for variables
            candidates = solve(expr - other.val, dict=True)

            # initialize list of valid solutions
            valid_solutions = [] 

            # parse solution set
            for solution in candidates:
                # get only variable and its value
                var, value = next(iter(solution.items()))

                # check if solution is integral (ASP-Core-2 is restricted to interger arithmetic)
                if value.is_integer:
                    valid_solutions.append(Number(int(value)))

            if len(valid_solutions) == 0:
                raise MatchError(self, other)
            elif len(valid_solutions) > 1:
                raise Exception("Cannot match arithmetical expression with multiple solutions.")
            else:
                subst.merge(Substitution({str(variables[0]): valid_solutions[0]}))
                return subst
        else:
            raise MatchError(self, other)


@dataclass
class Minus(ArithTerm):
    operand: Term

    def __repr__(self) -> str:
        return f"Minus({repr(self.operand)})"

    def __str__(self) -> str:
        return f"-{str(self.operand)}"

    def vars(self) -> VariableSet:
        return self.operand.vars()

    def sympy(self) -> SympyExpr:
        return -self.operand.sympy()

    def simplify(self) -> ArithTerm:
        operand = self.operand.simplify()

        # simplified operand is a number
        if isinstance(operand, Number):
            return Number(-operand.val)
        # two negatives cancel each other out
        elif isinstance(operand, Minus):
            return operand.operand
        else:
            return Minus(operand)

    def evaluate(self) -> Number:
        # TODO: '~' or '-'?
        return ~self.operand.evaluate()

    def substitute(self, subst: Dict[str, Term]) -> "Minus":
        return Minus(
            self.operand.substitute(subst)
        )


@dataclass
class Add(ArithTerm):
    loperand: Term
    roperand: Term

    def __repr__(self) -> str:
        return f"Add({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}+{str(self.roperand)}"

    def vars(self) -> VariableSet:
        return self.loperand.vars().union(self.roperand.vars())

    def sympy(self) -> SympyExpr:
        return self.loperand.sympy() + self.roperand.sympy()

    def simplify(self) -> ArithTerm:
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

    def evaluate(self) -> Number:
        return Number(self.loperands.evaluate() + self.roperands.evaluate())

    def substitute(self, subst: Dict[str, Term]) -> "Add":
        return Add(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst),
        )


@dataclass
class Sub(ArithTerm):
    loperand: Term
    roperand: Term

    def __repr__(self) -> str:
        return f"Sub({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}-{str(self.roperand)}"

    def vars(self) -> VariableSet:
        return self.loperand.vars().union(self.roperand.vars())

    def sympy(self) -> SympyExpr:
        return self.loperand.sympy() - self.roperand.sympy()

    def simplify(self) -> Union["Sub", Number]:
        loperand = self.loperand.simplify()
        roperand = self.roperand.simplify()

        # if both operands can be simplified to numbers, subtract them
        if isinstance(loperand, Number) and isinstance(roperand, Number):
            return Number(loperand.val-roperand.val)
        # only left operand is a number
        elif isinstance(loperand, Number):
            # left operand does not add anything
            if loperand.val == 0:
                return Minus(roperand)
        # only right operand is a number
        elif isinstance(roperand, Number):
            # right operand does not add anything
            if roperand.val == 0:
                return loperand
        # else return an instance of a simplified subtraction
        return Sub(loperand, roperand)

    def evaluate(self) -> Number:
        return Number(self.loperand.evaluate() - self.roperand.evaluate())

    def substitute(self, subst: Dict[str, Term]) -> "Sub":
        return Sub(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst),
        )


@dataclass
class Mult(ArithTerm):
    loperand: Term
    roperand: Term

    def __repr__(self) -> str:
        return f"Mult({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}*{str(self.roperand)}"

    def vars(self) -> VariableSet:
        return self.loperand.vars().union(self.roperand.vars())

    def sympy(self) -> SympyExpr:
        return self.loperand.sympy() * self.roperand.sympy()

    def simplify(self) -> ArithTerm:
        loperand = self.loperand.simplify()
        roperand = self.roperand.simplify()

        # if both operands can be simplified to numbers, multiply them
        if isinstance(loperand, Number) and isinstance(roperand, Number):
            return Number(loperand.val*roperand.val)
        # only left operand is a number
        elif isinstance(loperand, Number):
            if loperand.val == 0:
                return Number(0)
            elif loperand.val == 1:
                return roperand
            elif loperand.val == -1:
                return Minus(roperand).simplify()
        # only right operand is a number
        elif isinstance(roperand, Number):
            if roperand.val == 0:
                return Number(0)
            elif roperand.val == 1:
                return loperand
            elif roperand.val == -1:
                return Minus(loperand).simplify()
        # else return an instance of a simplified multiplication
        return Mult(loperand, roperand)

    def evaluate(self) -> Number:
        return Number(self.loperands.evaluate() * self.roperands.evaluate())

    def substitute(self, subst: Dict[str, Term]) -> "Mult":
        return Mult(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst),
        )


@dataclass
class Div(ArithTerm):
    loperand: Term
    roperand: Term

    def __repr__(self) -> str:
        return f"Div({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}/{str(self.roperand)}"

    def vars(self) -> VariableSet:
        return self.loperand.vars().union(self.roperand.vars())
    
    def sympy(self) -> SympyExpr:
        return self.loperand.sympy() // self.roperand.sympy() # integer division!
    
    def simplify(self) -> ArithTerm:
        loperand = self.loperand.simplify()
        roperand = self.roperand.simplify()

        # if both operands can be simplified to numbers, divide them
        if isinstance(loperand, Number) and isinstance(roperand, Number):
            if roperand.val == 0:
                raise ValueError("Division by zero detected in arithmetical term.")
            else:
                return Number(loperand.val/roperand.val)
        # only left operand is a number
        elif isinstance(loperand, Number):
            if loperand.val == 0:
                return Number(0)
        # only right operand is a number
        elif isinstance(roperand, Number):
            # invalid operation
            if roperand.val == 0:
                # TODO: custom error?
                raise ValueError("Division by zero detected in arithmetical term.")
            elif roperand.val == 1:
                return loperand
            elif roperand.val == -1:
                return Minus(loperand).simplify()
        # else return an instance of a simplified division
        return Div(loperand, roperand)

    def evaluate(self) -> Number:
        return Number(self.loperands.evaluate() // self.roperands.evaluate())

    def substitute(self, subst: Dict[str, Term]) -> "Div":
        return Div(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst),
        )