from typing import Optional, Tuple, Union, Set, TYPE_CHECKING
from copy import deepcopy
from functools import cached_property

from aspy.program.symbol_table import CHAR_ALPHA, CHAR_EPS, CHAR_ETA
from aspy.program.literals import LiteralTuple, AggregateLiteral, PredicateLiteral, BuiltinLiteral

from .statement import Fact, Rule

if TYPE_CHECKING:
    from aspy.program.expression import Expr
    from aspy.program.substitution import Substitution
    from aspy.program.literals import PredicateLiteral, Literal
    from aspy.program.terms import Variable
    from aspy.program.safety_characterization import SafetyTriplet

    from .statement import Statement


class NormalFact(Fact):
    """Normal fact.

    Rule of form

        h :- .

    for a classical atom h. The symbol ':-' may be omitted.

    Semantically, any answer set must include h.
    """
    def __init__(self, atom: "PredicateLiteral") -> None:
        self.atom = atom
        self.ground = atom.ground

    def __str__(self) -> str:
        return f"{str(self.atom)}."

    @property
    def head(self) -> LiteralTuple:
        return LiteralTuple([self.atom])

    @property
    def body(self) -> LiteralTuple:
        return LiteralTuple()

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return self.atom.vars(global_only)

    def safety(self, rule: Optional["Statement"]=None, global_vars: Optional[Set["Variable"]]=None) -> "SafetyTriplet":
        raise Exception()

    @cached_property
    def safe(self) -> bool:
        return len(self.vars()) > 0

    def substitute(self, subst: "Substitution") -> "NormalFact":
        return NormalFact(self.atom.substitute(subst))

    def match(self, other: "Expr") -> Set["Substitution"]:
        raise Exception("Matching for normal facts not supported yet.")


class NormalRule(Rule):
    """Normal rule.

    Rule of form:

        h :- b_1, ..., b_n .

    for a classical atom h and literals b_1,...,b_n.

    Semantically, any answer set that includes b_1,...,b_n must also include h.
    """
    def __init__(self, head: "PredicateLiteral", body: Union[LiteralTuple, Tuple["Literal", ...]]) -> None:
        self.atom = head
        self.literals = body if isinstance(body, LiteralTuple) else LiteralTuple(body)
        self.ground = self.atom.ground and self.body.ground

    def __str__(self) -> str:
        return f"{str(self.atom)} :- {', '.join([str(literal) for literal in self.body])}."

    @property
    def head(self) -> LiteralTuple:
        return LiteralTuple([self.atom])

    @property
    def body(self) -> LiteralTuple:
        return self.literals

    @cached_property
    def safe(self) -> bool:
        global_vars = self.vars(global_only=True)
        body_safety = SafetyTriplet.closure(self.body.safety(global_vars=global_vars))

        return body_safety == SafetyTriplet(global_vars)

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return set().union(self.atom.vars(), *self.body.vars(global_only))

    def safety(self, rule: Optional["Statement"]=None, global_vars: Optional[Set["Variable"]]=None) -> "SafetyTriplet":
        raise Exception()

    def substitute(self, subst: "Substitution") -> "NormalRule":
        return NormalRule(self.atom.substitute(subst), self.literals.substitute(subst))

    def match(self, other: "Expr") -> Set["Substitution"]:
        raise Exception("Matching for normal rules not supported yet.")