from typing import Optional, Tuple, Set, Dict, TYPE_CHECKING
from dataclasses import dataclass

from .statement import Fact, Rule

if TYPE_CHECKING:
    from aspy.program.terms import Term
    from aspy.program.expression import Expr, Substitution
    from aspy.program.literals import Literal, PredicateLiteral
    from aspy.program.variable_set import VariableSet


@dataclass
class NormalFact(Fact):
    """Normal fact.

    Rule of form

        h :- .

    for a classical atom h. The symbol ':-' may be omitted.

    Semantically, any answer set must include h.
    """
    atom: "PredicateLiteral"

    def __repr__(self) -> str:
        return f"NormalFact[{repr(self.atom)}]"

    def __str__(self) -> str:
        return f"{str(self.atom)}."

    @property
    def head(self) -> Tuple["PredicateLiteral"]:
        return (self.atom,)

    @property
    def body(self) -> Tuple["Literal"]:
        return tuple()

    def vars(self) -> "VariableSet":
        return self.atom.vars()

    def global_vars(self) -> "VariableSet":
        return self.vars()

    def substitute(self, subst: Dict[str, "Term"]) -> "NormalFact":
        return NormalFact(self.atom.substitute(subst))

    def match(self, other: "Expr", subst: Optional["Substitution"]=None) -> "Substitution":
        raise Exception()


class NormalRule(Rule):
    """Normal rule.

    Rule of form:

        h :- b_1, ..., b_n .

    for a classical atom h and literals b_1,...,b_n.

    Semantically, any answer set that includes b_1,...,b_n must also include h.
    """
    def __init__(self, head: "PredicateLiteral", body: Tuple["Literal", ...]) -> None:
        self.atom = head
        self.literals = body

    def __repr__(self) -> str:
        return f"NormalRule[{repr(self.atom)}]({', '.join([repr(literal) for literal in self.body])})"

    def __str__(self) -> str:
        return f"{str(self.atom)} :- {', '.join([str(literal) for literal in self.body])}."

    @property
    def head(self) -> Tuple["PredicateLiteral"]:
        return (self.atom,)

    @property
    def body(self) -> Tuple["Literal"]:
        return self.literals

    def vars(self) -> "VariableSet":
        return sum([literal.vars() for literal in self.body], self.atom.vars())

    def substitute(self, subst: Dict[str, "Term"]) -> "NormalRule":
        return NormalRule(self.atom.substitute(subst), tuple([literal.substitute(subst) for literal in self.body]))

    def match(self, other: "Expr", subst: Optional["Substitution"]=None) -> "Substitution":
        raise Exception()