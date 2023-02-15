from typing import Set, Optional, TYPE_CHECKING
from functools import cached_property

from .statement import Statement
from aspy.program.safety_characterization import SafetyTriplet

if TYPE_CHECKING:
    from aspy.program.expression import Expr
    from aspy.program.substitution import Substitution
    from aspy.program.terms import Term, TermTuple, Variable
    from aspy.program.literals import LiteralTuple

    from .statement import Statement


class WeakConstraint(Statement):
    """Weak constraint.

    Statement of form:

        :~ b_1,...,b_n . [ w@l,t_1,...,t_m ]

    for literals b_1,...,b_n and terms w,l,t_1,...,t_m.
    '@ l' may be omitted if l=0.
    """
    def __init__(self, literals: "LiteralTuple", weight: "Term", level: "Term", terms: "TermTuple") -> None:
        self.literals = literals
        self.weight = weight
        self.level = level
        self.terms = terms
        self.ground = weight.ground and level.ground and all(term.ground for term in terms) and all(literal.ground for literal in literals)

    def __str__(self) -> str:
        return f":~ {', '.join([str(literal) for literal in self.body])}. [{str(self.weight)}@{str(self.level)}, {', '.join([str(term) for term in self.terms])}]"

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return set().union(self.weight.vars(global_only), self.level.vars(global_only), *self.terms.vars(global_only), self.body.vars(global_only))

    def safety(self, rule: Optional["Statement"], global_vars: Optional[Set["Variable"]]=None) -> "SafetyTriplet":
        raise Exception()

    @cached_property
    def safe(self) -> bool:
        global_vars = self.vars(global_only=True)
        body_safety = SafetyTriplet.closure(self.body.safety(global_vars=global_vars))

        return body_safety == SafetyTriplet(global_vars)

    def substitute(self, subst: "Substitution") -> "WeakConstraint":
        return WeakConstraint(
            self.literals.substitute(subst),
            self.weight.substitute(subst),
            self.level.substitute(subst),
            self.terms.substitute(subst)
        )

    def match(self, other: "Expr") -> Set["Substitution"]:
        raise Exception("Matching for weak constraints not supported yet.")