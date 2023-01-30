from typing import Optional, Tuple, Dict, Set, TYPE_CHECKING
from abc import ABC
from dataclasses import dataclass

from aspy.program.expression import Expr
from aspy.program.safety import Safety
from aspy.program.variable_set import VariableSet

from .statement import Statement
from .weak_constraint import WeakConstraint

if TYPE_CHECKING:
    from aspy.program.expression import Substitution
    from aspy.program.terms import Term
    from aspy.program.literals import Literal


@dataclass
class OptimizeElement(Expr):
    """Optimization element for optimize statements.
    
    Expression of form:

        w @ l,t_1,...,t_m : b_1,...,b_n

    for terms w,l,t_1,...,t_m and literals b_1,...,b_n.
    '@ l' may be omitted if l=0.
    """
    weight: "Term"
    level: "Term"
    terms: Tuple["Term", ...]
    literals: Tuple["Literal", ...]

    def __repr__(self) -> str:
        return f"OptimizeElement({repr(self.weight)}@{repr(self.level)}, {', '.join([repr(term) for term in self.terms])} : {', '.join([repr(literal) for literal in self.literals])})"

    def __str__(self) -> str:
        return f"{str(self.weight)}@{str(self.level)}, {', '.join([str(term) for term in self.terms])} : {', '.join([str(literal) for literal in self.literals])}"

    @property
    def head(self) -> Tuple["Term", ...]:
        return (self.weight, self.level, *self.terms)

    @property
    def body(self) -> Tuple["Term", ...]:
        return self.literals

    def vars(self) -> VariableSet:
        # TODO: ugly
        return sum([self.weight.vars(), self.level.vars()] + [term.vars() for term in self.terms] + [literal.vars() for literal in self.literals], VariableSet())

    def safety(self) -> Safety:
        return Safety.closure([literal.safety() for literal in self.literals])

    def substitute(self, subst: Dict[str, "Term"]) -> "OptimizeElement":
        return OptimizeElement(self.weight.substitute(subst), self.level.substitute(subst), tuple([term.substitute(subst) for term in self.terms]), tuple([literal.substitute(subst) for literal in self.literals]))

    def match(self, other: Expr, subst: Optional["Substitution"]=None) -> "Substitution":
        pass


@dataclass
class OptimizeStatement(Statement, ABC):
    """Abstract base class for all optimize statement."""
    elements: Tuple[OptimizeElement, ...]
    minimize: bool

    @property
    def head(self) -> Tuple["Term", ...]:
        return sum([element.head() for element in self.elements])

    @property
    def body(self) -> Tuple["Term", ...]:
        return sum([element.body() for element in self.elements])

    def transform(self) -> Tuple[WeakConstraint, ...]:
        """Transforms the optimize statement into (possibly multiple) weak constraints."""
        # transform each optimize element into a weak constraint
        return tuple(
            WeakConstraint(
                element.literals,
                element.weight,
                element.level,
                element.terms
            )
            for element in self.elements
        )

    def vars(self) -> VariableSet:
        return sum([element.vars() for element in self.elements], VariableSet())


class MinimizeStatement(OptimizeStatement):
    """Minimize statement.

    Statement of the form:

        #minimize{w_1@l_1,t_{11},...,t_{1m}:b_{11},...,b_{1n};...;w_k@l_k,t_{k1},...,t_{km}:b_{k1},...,b_{kn}}

    for literals b_{11},...,b_{1n},...,b_{k1},...,b_{kn} and terms w_1,...,w_k,l_1,...,l_k,t_{11},...,t_{1m},t_{k1},...,t_{km}.

    Can alternatively be written as multiple weak constraints:

        :~ b_{11},...,b_{1n}. [w_1@l_1,t_{11},...,t_{1m}]
        ...
        :~ b_{k1},...,b_{kn}. [w_k@l_1,t_{k1},...,t_{km}]
    """
    def __init__(self, elements: Tuple[OptimizeElement, ...]) -> None:
        super().__init__(elements, True)

    def __repr__(self) -> str:
        return f"Minimize({', '.join([repr(element) for element in self.elements])})"

    def __str__(self) -> str:
        return f"#minimize{{{' ; '.join([str(element) for element in self.elements])}}}"

    def substitute(self, subst: Dict[str, "Term"]) -> "MinimizeStatement":
        return OptimizeStatement(
            self.elements.substitute(subst)
        )

    def match(self, other: Expr, subst: Optional["Substitution"]=None) -> "Substitution":
        pass


class MaximizeStatement(OptimizeStatement):
    """Maximize statement.

    Statement of the form:

        #maximize{w_1@l_1,t_{11},...,t_{1m}:b_{11},...,b_{1n};...;w_k@l_k,t_{k1},...,t_{km}:b_{k1},...,b_{kn}}

    for literals b_{11},...,b_{1n},...,b_{k1},...,b_{kn} and terms w_1,...,w_k,l_1,...,l_k,t_{11},...,t_{1m},t_{k1},...,t_{km}.

    Can alternatively be written as multiple weak constraints:

        :~ b_{11},...,b_{1n}. [-w_1@l_1,t_{11},...,t_{1m}]
        ...
        :~ b_{k1},...,b_{kn}. [-w_k@l_1,t_{k1},...,t_{km}]
    """
    def __init__(self, elements: Tuple[OptimizeElement, ...]) -> None:
        super().__init__(elements, False)

    def __repr__(self) -> str:
        return f"Maximize({', '.join([repr(element) for element in self.elements])})"

    def __str__(self) -> str:
        return f"#maximize{{{' ; '.join([str(element) for element in self.elements])}}}"

    def substitute(self, subst: Dict[str, "Term"]) -> "MaximizeStatement":
        return MaximizeStatement(
            self.elements.substitute(subst)
        )
    
    def match(self, other: Expr, subst: Optional["Substitution"]=None) -> "Substitution":
        pass