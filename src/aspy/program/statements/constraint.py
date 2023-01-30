from typing import Optional, Tuple, Set, Dict, TYPE_CHECKING
from dataclasses import dataclass

from aspy.program.variable_set import VariableSet

from .statement import Statement

if TYPE_CHECKING:
    from aspy.program.expression import Expr, Substitution
    from aspy.program.terms import Term
    from aspy.program.literals import Literal

    from .normal import NormalRule


@dataclass
class Constraint(Statement):
    """Constraint.

    Statement of form:

        :- b_1,...,b_n .

    for literals b_1,...,b_n.
    """
    literals: Tuple["Literal", ...]

    def __repr__(self) -> str:
        return f"Constraint({', '.join([repr(literal) for literal in self.body])})"

    def __str__(self) -> str:
        return f":- {', '.join([str(literal) for literal in self.body])}."

    @property
    def head(self) -> Tuple["Term", ...]:
        return tuple()

    @property
    def body(self) -> Tuple["Term", ...]:
        return self.literals

    def vars(self) -> VariableSet:
        return sum([literal.vars() for literal in self.body], VariableSet())

    def transform(self) -> Tuple["NormalRule"]:
        """TODO"""
        raise Exception("Transformation of constraints not supported yet.")

    def substitute(self, subst: Dict[str, "Term"]) -> "Constraint":
        return Constraint(tuple([literal.substitute(subst) for literal in self.body]))

    def match(self, other: "Expr", subst: Optional["Substitution"]=None) -> "Substitution":
        pass