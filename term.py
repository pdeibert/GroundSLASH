from typing import Tuple, Dict
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from functools import cached_property

from expression import Expr


class Term(Expr, ABC):
    def __eq__(self, other: "Term") -> bool:
        """Implements the binary '=' operator for terms."""
        return (self << other) and (other << self)

    def __ne__(self, other: "Term") -> bool:
        """Implements the binary '!=' operator for terms."""
        return not (self == other)

    def __lt__(self, other: "Term") -> bool:
        """Implements the binary '<' operator for terms."""
        return (self << other) and not (other << self)

    def __gt__(self, other: "Term") -> bool:
        """Implements the binary '>' operator for terms."""
        return (other << self) and not (self << other)

    def __le__(self, other: "Term") -> bool:
        """Implements the binary '<=' operator for terms."""
        return (self << other)

    def __ge__(self, other: "Term") -> bool:
        """Implements the binary '>=' operator for terms."""
        return (other << self)

    @abstractmethod
    def __lshift__(self, other: "Term") -> bool:
        """Defines the total ordering operator defined for terms in ASP-Core-2."""
        pass


class Infimum(Term):
    """Least element in a total ordering."""
    def __lshift__(self, other: Term) -> bool:
        return True

    def substitute(self, subst: Dict[str, Term]) -> "Infimum":
        return Infimum

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return "#inf"


class Supremum(Term):
    """Greatest element in a total ordering."""
    def __lshift__(self, other: Term) -> bool:
        return False

    def substitute(self, subst: Dict[str, Term]) -> "Supremum":
        return Supremum

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return "#sup"


@dataclass
class Variable(Term):
    val: str

    def __lshift__(self, other: Term) -> bool:
        raise Exception("Total ordering if undefined for variables.")

    def substitute(self, subst: Dict[str, Term]) -> Term:
        if self.val in subst:
            return subst[self.val]
        else:
            raise LookupError(f"Variable {self.val} is not assigned during instantiation.")

    def __repr__(self) -> str:
        return f"Var({self.val})"

    def __str__(self) -> str:
        return self.val


class AnonVariable(Term):
    def __init__(self, id: int) -> None:
        self.val = f"_{id}"

    def __lshift__(self, other: Term) -> bool:
        raise Exception("Total ordering is undefined for anonymous variables.")

    def substitute(self, subst: Dict[str, Term]) -> Term:
        raise Exception("Instantiation of anonymous variables not supported yet.")

    def __repr__(self) -> str:
        return f"Var({self.val})"

    def __str__(self) -> str:
        return "_"


@dataclass
class Number(Term):
    val: int

    def __lshift__(self, other: Term) -> bool:
        if isinstance(other, Infimum):
            return False
        elif isinstance(other, Number):
            return self.val <= other.val
        else:
            return True

    def __add__(self, other) -> "Number":
        return Number(self.val + other.val)

    def __sub__(self, other) -> "Number":
        return Number(self.val - other.val)

    def __mul__(self, other) -> "Number":
        return Number(self.val * other.val)

    def __floordiv__(self, other) -> "Number":
        return Number(self.val // other.val)

    def __neg__(self) -> "Number":
        return Number(self.val * -1)

    def __invert__(self) -> "Number":
        return -self

    def __abs__(self) -> "Number":
        return Number(abs(self.val))

    def substitute(self, subst: Dict[str, Term]) -> "Number":
        return Number(self.val)

    def __repr__(self) -> str:
        return f"Number({str(self.val)})"

    def __str__(self) -> str:
        return str(self.val)


@dataclass
class SymbolicConstant(Term):
    val: str

    def __lshift__(self, other: Term) -> bool:
        if isinstance(other, (Infimum, Number)):
            return False
        elif isinstance(other, SymbolicConstant):
            return self.val <= other.val
        else:
            return True

    def substitute(self, subst: Dict[str, Term]) -> "SymbolicConstant":
        return SymbolicConstant(self.val)

    def __repr__(self) -> str:
        return f"SymConst({self.val})"

    def __str__(self) -> str:
        return self.val


@dataclass
class String(Term):
    val: str

    def __lshift__(self, other: Term) -> bool:
        if isinstance(other, (Infimum, Number, SymbolicConstant)):
            return False
        elif isinstance(other, String):
            return self.val <= other.val
        else:
            return True

    def substitute(self, subst: Dict[str, Term]) -> "String":
        return String(self.val)

    def __repr__(self) -> str:
        return f"Str({self.val})"

    def __str__(self) -> str:
        return '"' + self.val + '"'


@dataclass
class Functional(Term):
    functor: str
    terms: Tuple[Term, ...]

    @cached_property
    def arity(self) -> int:
        return len(self.terms)

    def __lshift__(self, other: Term) -> bool:
        if isinstance(other, (Infimum, Number, SymbolicConstant, String)):
            return False
        elif isinstance(other, Functional):
            if self.arity < other.arity:
                return True
            elif self.arity == other.arity:
                if self.functor < other.functor:
                    return True
                elif self.functor == other.functor:
                    for self_term, other_term in zip(self.terms, other.terms):
                        if self_term > other_term:
                            return False
                    
                    return True

        return False

    def __repr__(self) -> str:
        return f"Func[{self.functor}]" + (f"({','.join([repr(term) for term in self.terms])})" if self.terms else '')

    def __str__(self) -> str:
        return self.functor + (f"({','.join([str(term) for term in self.terms])})" if self.terms else '')

    def substitute(self, subst: Dict[str, Term]) -> "Functional":
        return Functional(
            self.functor,
            tuple(term.substitute(subst) for term in self.terms)
        )


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
    def __lshift__(self, other: "Term") -> bool:
        return self.evaluate() << other

    @abstractmethod
    def evaluate(self) -> Number:
        pass


@dataclass
class Add(ArithTerm):
    loperand: Term
    roperand: Term

    def __repr__(self) -> str:
        return f"Add({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}+{str(self.roperand)}"

    def substitute(self, subst: Dict[str, Term]) -> "Add":
        return Add(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst),
        )

    def evaluate(self) -> Number:
        return Number(self.loperands.evaluate() + self.roperands.evaluate())


@dataclass
class Sub(ArithTerm):
    loperand: Term
    roperand: Term

    def __repr__(self) -> str:
        return f"Sub({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}-{str(self.roperand)}"

    def substitute(self, subst: Dict[str, Term]) -> "Sub":
        return Sub(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst),
        )

    def evaluate(self) -> Number:
        return Number(self.loperands.evaluate() - self.roperands.evaluate())


@dataclass
class Mult(ArithTerm):
    loperand: Term
    roperand: Term

    def __repr__(self) -> str:
        return f"Mult({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}*{str(self.roperand)}"

    def substitute(self, subst: Dict[str, Term]) -> "Mult":
        return Mult(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst),
        )

    def evaluate(self) -> Number:
        return Number(self.loperands.evaluate() * self.roperands.evaluate())


@dataclass
class Div(ArithTerm):
    loperand: Term
    roperand: Term

    def __repr__(self) -> str:
        return f"Div({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}/{str(self.roperand)}"

    def substitute(self, subst: Dict[str, Term]) -> "Div":
        return Div(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst),
        )

    def evaluate(self) -> Number:
        return Number(self.loperands.evaluate() // self.roperands.evaluate())


@dataclass
class Minus(ArithTerm):
    operand: Term

    def __repr__(self) -> str:
        return f"Minus({repr(self.operand)})"

    def __str__(self) -> str:
        return f"-{str(self.operand)}"

    def substitute(self, subst: Dict[str, Term]) -> "Minus":
        return Minus(
            self.operand.substitute(subst)
        )

    def evaluate(self) -> Number:
        # TODO: '~' or '-'?
        return ~self.operand.evaluate()


# TODO: use __pos__, __neg__ for annotating default/classical negation?

"""
@dataclass
class RootTerm: # TODO: change typings of all statements that expect a root term!
    ""TODO: should represent a FINAL term that is not part of another term.""
    term: Term

    def __eq__(self, other: Term) -> bool:
        ""Implements the binary '=' operator for terms.""
        return self.term == other

    def __ne__(self, other: Term) -> bool:
        ""Implements the binary '!=' operator for terms.""
        return self.term != other

    def __lt__(self, other: Term) -> bool:
        ""Implements the binary '<' operator for terms.""
        return self.term < other

    def __gt__(self, other: Term) -> bool:
        ""Implements the binary '>' operator for terms.""
        return self.term > other

    def __le__(self, other: Term) -> bool:
        ""Implements the binary '<=' operator for terms.""
        return self.term <= other

    def __ge__(self, other: Term) -> bool:
        ""Implements the binary '>=' operator for terms.""
        return self.term >= other

    def __lshift__(self, other: "Term") -> bool:
        ""Defines the total ordering operator defined for terms in ASP-Core-2.""
        return self.term << other

    def substitute(self, subst: Dict[str, Term]) -> "RootTerm":
        return RootTerm(
            self.term.substitute(subst)
        )
"""