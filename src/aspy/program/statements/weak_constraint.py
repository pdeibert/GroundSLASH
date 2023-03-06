from copy import deepcopy
from functools import cached_property
from typing import TYPE_CHECKING, Optional, Set

from aspy.program.literals import LiteralTuple
from aspy.program.safety_characterization import SafetyTriplet

from .statement import Statement

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.literals import LiteralTuple
    from aspy.program.substitution import Substitution
    from aspy.program.terms import Term, TermTuple, Variable

    from .statement import Statement


class WeakConstraint(Statement):
    """Weak constraint.

    Statement of form:

        :~ b_1,...,b_n . [ w@l,t_1,...,t_m ]

    for literals b_1,...,b_n and terms w,l,t_1,...,t_m.
    '@ l' may be omitted if l=0.
    """

    def __init__(
        self, literals: "LiteralTuple", weight: "Term", level: "Term", terms: "TermTuple", *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self.literals = literals
        self.weight = weight
        self.level = level
        self.terms = terms

    def __str__(self) -> str:
        return f":~ {', '.join([str(literal) for literal in self.body])}. [{str(self.weight)}@{str(self.level)}, {', '.join([str(term) for term in self.terms])}]"

    @property
    def head(self) -> LiteralTuple:
        return LiteralTuple()

    @property
    def body(self) -> LiteralTuple:
        return self.literals

    @cached_property
    def safe(self) -> bool:
        global_vars = self.vars(global_only=True)
        body_safety = SafetyTriplet.closure(self.body.safety(global_vars=global_vars))

        return body_safety == SafetyTriplet(global_vars)

    @cached_property
    def ground(self) -> bool:
        return (
            self.weight.ground
            and self.level.ground
            and all(term.ground for term in self.terms)
            and all(literal.ground for literal in self.literals)
        )

    def safety(self, rule: Optional["Statement"], global_vars: Optional[Set["Variable"]] = None) -> "SafetyTriplet":
        raise Exception("Safety characterization for weak constraints not supported yet.")

    def substitute(self, subst: "Substitution") -> "WeakConstraint":
        if self.ground:
            return deepcopy(self)

        return WeakConstraint(
            self.literals.substitute(subst),
            self.weight.substitute(subst),
            self.level.substitute(subst),
            self.terms.substitute(subst),
        )
