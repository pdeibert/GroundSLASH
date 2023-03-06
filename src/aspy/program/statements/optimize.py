from abc import ABC
from copy import deepcopy
from functools import cached_property
from typing import TYPE_CHECKING, Optional, Set, Tuple

from aspy.program.expression import Expr
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.terms import TermTuple

from .statement import Statement

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.literals import LiteralTuple
    from aspy.program.substitution import Substitution
    from aspy.program.terms import Term, Variable


class OptimizeElement(Expr):
    """Optimization element for optimize statements.

    Expression of form:

        w @ l,t_1,...,t_m : b_1,...,b_n

    for terms w,l,t_1,...,t_m and literals b_1,...,b_n.
    '@ l' may be omitted if l=0.
    """

    def __init__(self, weight: "Term", level: "Term", terms: TermTuple, literals: "LiteralTuple") -> None:
        self.weight = weight
        self.level = level
        self.terms = terms
        self.literals = literals

    def __str__(self) -> str:
        return f"{str(self.weight)}@{str(self.level)}, {', '.join([str(term) for term in self.terms])} : {', '.join([str(literal) for literal in self.literals])}"

    @property
    def head(self) -> TermTuple:
        return TermTuple(self.weight, self.level) + self.terms

    @property
    def body(self) -> "LiteralTuple":
        return self.literals

    @property
    def ground(self) -> bool:
        return self.weight.ground and self.level.ground and self.terms.ground and self.literals.ground

    def vars(self, global_only: bool = False) -> Set["Variable"]:
        return set().union(
            self.weight.vars(global_only),
            self.level.vars(global_only),
            self.terms.vars(global_only),
            self.literals.vars(global_only),
        )

    def safety(self, rule: Optional["Statement"], global_vars: Optional[Set["Variable"]] = None) -> "SafetyTriplet":
        raise Exception("Safety characterization for optimize elements not supported yet.")

    def substitute(self, subst: "Substitution") -> "OptimizeElement":
        raise Exception("Substitution for optimize elements not supported yet.")


class OptimizeStatement(Statement, ABC):
    """Abstract base class for all optimize statement."""

    def __init__(self, elements: Tuple[OptimizeElement, ...], minimize: bool, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.elements = elements
        self.minimize = minimize

    @property
    def head(self) -> TermTuple:
        # TODO: correct?
        return sum([element.head() for element in self.elements])

    @property
    def body(self) -> "LiteralTuple":
        # TODO: correct?
        return sum([element.body() for element in self.elements])

    @cached_property
    def safe(self) -> bool:
        raise Exception("Safety for optimize statements not supported yet.")

    @cached_property
    def ground(self) -> bool:
        return all(element.ground for element in self.elements)

    def safety(self, rule: Optional["Statement"], global_vars: Optional[Set["Variable"]] = None) -> "SafetyTriplet":
        raise Exception("Safety characterization for optimize statements not supported yet.")


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

    def __str__(self) -> str:
        return f"#minimize{{{' ; '.join([str(element) for element in self.elements])}}}"

    def substitute(self, subst: "Substitution") -> "MinimizeStatement":
        if self.ground:
            return deepcopy(self)

        # substitute elements recursively
        elements = (element.substitute(subst) for element in self.elements)

        return MinimizeStatement(elements)


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

    def __str__(self) -> str:
        return f"#maximize{{{' ; '.join([str(element) for element in self.elements])}}}"

    def substitute(self, subst: "Substitution") -> "MaximizeStatement":
        if self.ground:
            return deepcopy(self)

        # substitute elements recursively
        elements = (element.substitute(subst) for element in self.elements)

        return MaximizeStatement(elements)
