from typing import Set, Optional, TYPE_CHECKING
from functools import cached_property

from aspy.program.literals import LiteralTuple
from aspy.program.safety_characterization import SafetyTriplet

from .statement import Fact, Rule

if TYPE_CHECKING:
    from aspy.program.expression import Expr
    from aspy.program.terms import Variable
    from aspy.program.substitution import Substitution
    from aspy.program.statements import Statement


class DisjunctiveFact(Fact):
    """Disjunctive fact.
    
    Rule of form

        h_1 | ... | h_m :- .

    for classical atoms h_1,...,h_m. The symbol ':-' may be omitted.

    Semantically, any answer set must include exactly one classical atom h_i.
    """
    def __init__(self, atoms: LiteralTuple) -> None:
        self.atoms = atoms
        self.ground = all(atom.ground for atom in atoms)

    def __str__(self) -> str:
        return ' | '.join([str(atom) for atom in self.atoms]) + '.'

    @property
    def head(self) -> LiteralTuple:
        return self.atoms

    @property
    def body(self) -> LiteralTuple:
        return LiteralTuple()

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return set().union(*self.head.vars(global_only))

    def safety(self, rule: Optional["Statement"], global_vars: Optional[Set["Variable"]]=None) -> "SafetyTriplet":
        raise Exception()

    @cached_property
    def safe(self) -> bool:
        return len(self.vars()) > 0

    def substitute(self, subst: "Substitution") -> "DisjunctiveFact":
        return DisjunctiveFact(self.head.substitute(subst))

    def match(self, other: "Expr") -> Set["Substitution"]:
        raise Exception("Matching for disjunctive facts not supported yet.")


class DisjunctiveRule(Rule):
    """Disjunctive rule.
    
    Rule of form:

        h_1 | ... | h_m :- b_1,...,b_n .

    for classical atoms h_1,...,h_m and literals b_1,...,b_n.

    Semantically, any answer set that includes b_1,...,b_n must also include exactly one h_i.
    """
    def __init__(self, head: LiteralTuple, body: LiteralTuple) -> None:
        self.atoms = head
        self.literals = body
        self.ground = all(atom.ground for atom in head) and all(literal.ground for literal in body)

    def __str__(self) -> str:
        return f"{' | '.join([str(atom) for atom in self.head])} :- {', '.join([str(literal) for literal in self.body])}."

    @property
    def head(self) -> LiteralTuple:
        return self.atoms

    @property
    def body(self) -> LiteralTuple:
        return self.literals

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return set().union(*self.head.vars(global_only), *self.body.vars(global_only))

    def safety(self, rule: Optional["Statement"], global_vars: Optional[Set["Variable"]]=None) -> "SafetyTriplet":
        raise Exception()

    @cached_property
    def safe(self) -> bool:
        global_vars = self.vars(global_only=True)
        body_safety = SafetyTriplet.closure(self.body.safety(global_vars=global_vars))

        return body_safety == SafetyTriplet(global_vars)

    def substitute(self, subst: "Substitution") -> "DisjunctiveRule":
        return DisjunctiveRule(self.head.substitute(subst), self.literals.substitute(subst))

    def match(self, other: "Expr") -> Set["Substitution"]:
        raise Exception("Matching for disjunctive rules not supported yet.")