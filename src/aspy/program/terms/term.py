from typing import Dict, Optional, Set
from abc import ABC, abstractmethod
from dataclasses import dataclass

from sympy import Symbol # type: ignore
from sympy import Expr as SympyExpr # type: ignore

from aspy.program.expression import Expr, Substitution, MatchError, AssignmentError
from aspy.program.safety import Safety


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

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return "#inf"

    def vars(self) -> Set["Variable"]:
        return set()

    def safety(self) -> Safety:
        return Safety(set(), set(), set())

    def substitute(self, subst: Dict[str, Term]) -> "Infimum":
        return Infimum

    def match(self, other: Expr, subst: Optional[Substitution]=None) -> Substitution:
        if subst is None:
            subst = Substitution()

        if isinstance(other, Infimum):
            # return substitution (infimum has no variables)
            return subst
        else:
            raise MatchError(self, other)

  
class Supremum(Term):
    """Greatest element in a total ordering."""
    def __lshift__(self, other: Term) -> bool:
        return False

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return "#sup"

    def vars(self) -> Set["Variable"]:
        return set()

    def safety(self) -> Safety:
        return Safety(set(), set(), set())

    def substitute(self, subst: Dict[str, Term]) -> "Supremum":
        return Supremum

    def match(self, other: Expr, subst: Optional[Substitution]=None) -> Substitution:
        if subst is None:
            subst = Substitution()

        if isinstance(other, Supremum):
            # return substitution (supremum has no variables)
            return subst
        else:
            raise MatchError(self, other)

    def vars(self) -> Set["Variable"]:
        return set()


@dataclass
class Variable(Term):
    val: str

    def __lshift__(self, other: Term) -> bool:
        raise Exception("Total ordering if undefined for variables.")

    def __repr__(self) -> str:
        return f"Var({self.val})"

    def __str__(self) -> str:
        return self.val

    def __hash__(self) -> str:
        return hash(self.val)

    def vars(self) -> Set["Variable"]:
        return set([self])

    def safety(self) -> Safety:
        return Safety(set([self]), set(), set())

    def sympy(self) -> SympyExpr:
        return Symbol(self.val)

    def simplify(self) -> "Variable":
        return self

    def substitute(self, subst: Dict[str, Term]) -> Term:
        if self.val in subst:
            return subst[self.val]
        else:
            raise LookupError(f"Variable {self.val} is not assigned during instantiation.")

    def match(self, other: Expr, subst: Optional[Substitution]=None) -> Substitution:
        if subst is None:
            subst = Substitution()

        if isinstance(other, Term):
            try:
                var_subst = Substitution({self.val: other})

                # combine substitutions
                subst.merge(var_subst)

                return subst
            except AssignmentError:
                raise MatchError(self, other)
        else:
            raise MatchError(self, other)


class AnonVariable(Variable):
    def __init__(self, id: int) -> None:
        self.val = f"_{id}"

    def __lshift__(self, other: Term) -> bool:
        raise Exception("Total ordering is undefined for anonymous variables.")

    def __repr__(self) -> str:
        return f"Var({self.val})"

    def __str__(self) -> str:
        return "_"

    def vars(self) -> Set[Variable]:
        return set([self])

    def safety(self) -> Safety:
        return Safety(set(), set(), set())

    def sympy(self) -> SympyExpr:
        return Symbol(self.val)

    def simplify(self) -> "AnonVariable":
        return self

    def substitute(self, subst: Dict[str, Term]) -> Term:
        raise Exception("Instantiation of anonymous variables not supported yet.")

    def match(self, other: Expr, subst: Optional[Substitution]=None) -> Substitution:
        if subst is None:
            subst = Substitution()

        if isinstance(other, Term):
            try:
                var_subst = Substitution({self.val: other})

                # combine substitutions
                subst.merge(var_subst)

                return subst
            except AssignmentError:
                raise MatchError(self, other)
        else:
            raise MatchError(self, other)


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

    def __repr__(self) -> str:
        return f"Number({str(self.val)})"

    def __str__(self) -> str:
        return str(self.val)

    def vars(self) -> Set[Variable]:
        return set()

    def safety(self) -> Safety:
        return Safety(set(), set(), set())

    def sympy(self) -> SympyExpr:
        return self.val

    def simplify(self) -> "Number":
        return self

    def substitute(self, subst: Dict[str, Term]) -> "Number":
        return Number(self.val)

    def match(self, other: Expr, subst: Optional[Substitution]=None) -> Substitution:
        if subst is None:
            subst = Substitution()

        if isinstance(other, Number) and self.val == other.val:
            # return substitution (number has no variables)
            return subst
        else:
            raise MatchError(self, other)


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

    def __repr__(self) -> str:
        return f"SymConst({self.val})"

    def __str__(self) -> str:
        return self.val

    def vars(self) -> Set[Variable]:
        return set()

    def safety(self) -> Safety:
        return Safety(set(), set(), set())

    def substitute(self, subst: Dict[str, Term]) -> "SymbolicConstant":
        return SymbolicConstant(self.val)

    def match(self, other: Expr, subst: Optional[Substitution]=None) -> Substitution:
        if subst is None:
            subst = Substitution()

        if isinstance(other, SymbolicConstant) and self.val == other.val:
            # return substitution (symbolic constant has no variables)
            return subst
        else:
            raise MatchError(self, other)


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

    def __repr__(self) -> str:
        return f"Str({self.val})"

    def __str__(self) -> str:
        return '"' + self.val + '"'

    def vars(self) -> Set[Variable]:
        return set()

    def safety(self) -> Safety:
        return Safety(set(), set(), set())

    def substitute(self, subst: Dict[str, Term]) -> "String":
        return String(self.val)

    def match(self, other: Expr, subst: Optional[Substitution]=None) -> Substitution:
        if subst is None:
            subst = Substitution()

        if isinstance(other, String) and self.val == other.val:
            # return substitution (string has no variables)
            return subst
        else:
            raise MatchError(self, other)


# TODO: use __pos__, __neg__ for annotating default/classical negation?