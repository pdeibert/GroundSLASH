from typing import Set, Optional, TYPE_CHECKING
from functools import cached_property

from aspy.program.literals import LiteralTuple
from aspy.program.safety_characterization import SafetyTriplet

from .statement import Statement

if TYPE_CHECKING:
    from aspy.program.expression import Expr
    from aspy.program.terms import Variable
    from aspy.program.substitution import Substitution


class Constraint(Statement):
    """Constraint.

    Statement of form:

        :- b_1,...,b_n .

    for literals b_1,...,b_n.
    """
    def __init__(self, literals: LiteralTuple) -> None:
        self.literals = literals
        self.ground = all(literal.ground for literal in literals)

    def __str__(self) -> str:
        return f":- {', '.join([str(literal) for literal in self.body])}."

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return set().union(*self.body.vars(global_only))

    def safety(self, rule: Optional[Statement], global_vars: Optional[Set["Variable"]]=None) -> "SafetyTriplet":
        raise Exception()

    @cached_property
    def safe(self) -> bool:
        global_vars = self.vars(global_only=True)
        body_safety = SafetyTriplet.closure(self.body.safety(global_vars=global_vars))

        return body_safety == SafetyTriplet(global_vars)

    def substitute(self, subst: "Substitution") -> "Constraint":
        return Constraint(self.literals.substitute(subst))

    def match(self, other: "Expr") -> Set["Substitution"]:
        raise Exception("Matching for constraints not supported yet.")