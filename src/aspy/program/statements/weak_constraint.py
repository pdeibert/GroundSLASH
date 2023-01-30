from typing import Optional, Tuple, Set, Dict, TYPE_CHECKING
from dataclasses import dataclass

from aspy.program.literals import AggregateLiteral
from aspy.program.variable_set import VariableSet

from .statement import Statement

if TYPE_CHECKING:
    from aspy.program.expression import Expr, Substitution
    from aspy.program.terms import Term
    from aspy.program.literals import Literal


@dataclass
class WeakConstraint(Statement):
    """Weak constraint.

    Statement of form:

        :~ b_1,...,b_n . [ w@l,t_1,...,t_m ]

    for literals b_1,...,b_n and terms w,l,t_1,...,t_m.
    '@ l' may be omitted if l=0.
    """
    literals: Tuple["Literal", ...]
    weight: "Term"
    level: "Term"
    terms: Tuple["Term", ...]

    def __repr__(self) -> str:
        return f"WeakConstraint({', '.join([repr(literal) for literal in self.body])},{repr(self.weight)}@{repr(self.level)},{', '.join([repr(term) for term in self.terms])})"

    def __str__(self) -> str:
        return f":~ {', '.join([str(literal) for literal in self.body])}. [{str(self.weight)}@{str(self.level)}, {', '.join([str(term) for term in self.terms])}]"

    @property
    def head(self) -> Tuple["Term", ...]:
        return (self.weight, self.level, *self.terms)

    @property
    def body(self) -> Tuple["Term", ...]:
        return self.literals

    def vars(self) -> VariableSet:
        return sum([self.weight.vars(), self.level.vars()] + [term.vars() for term in self.terms] + [literal.vars() for literal in self.body], VariableSet())

    def transform(self) -> Tuple["WeakConstraint", ...]:
        """Handles any aggregates in the constraint body."""

        pos_aggr_ids = []
        neg_aggr_ids = []

        for i, term in enumerate(self.body):
            if isinstance(term, AggregateLiteral):
                if term.neg:
                    # TODO
                    pass
                else:
                    pass

                # TODO: check if aggregate is NOT
                # TODO: call transform on resulting weak constraints to handle additional aggregates!
                break
        
        raise Exception("Transformation of weak constraints is not supported yet.")

    def substitute(self, subst: Dict[str, "Term"]) -> "WeakConstraint":
        return WeakConstraint(tuple([literal.substitute(subst) for literal in self.literal]), self.weight.substitute(subst), self.level.substitute(subst), tuple([term.substitute(subst) for term in self.body]))

    def match(self, other: "Expr", subst: Optional["Substitution"]=None) -> "Substitution":
        pass