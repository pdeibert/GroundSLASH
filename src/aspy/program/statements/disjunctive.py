from typing import Optional, Tuple, Set, Dict, TYPE_CHECKING
from dataclasses import dataclass

from .statement import Fact, Rule

if TYPE_CHECKING:
    from aspy.program.expression import Expr, Substitution
    from aspy.program.terms import Term, Variable
    from aspy.program.literals import Literal, PredicateLiteral


@dataclass
class DisjunctiveFact(Fact):
    """Disjunctive fact.
    
    Rule of form

        h_1 | ... | h_m :- .

    for classical atoms h_1,...,h_m. The symbol ':-' may be omitted.

    Semantically, any answer set must include exactly one classical atom h_i.
    """
    atoms: Tuple["PredicateLiteral", ...]

    def __repr__(self) -> str:
        return f"DisjunctiveFact[{'| '.join([repr(atom) for atom in self.atoms])}]"

    def __str__(self) -> str:
        return ' | '.join([str(atom) for atom in self.atoms]) + '.'

    @property
    def head(self) -> Tuple["PredicateLiteral"]:
        return self.atoms

    @property
    def body(self) -> Tuple["Literal"]:
        return tuple()

    def vars(self) -> Set["Variable"]:
        return set().union(*[atom.vars() for atom in self.head])

    def global_vars(self) -> Set["Variable"]:
        return self.vars()

    def substitute(self, subst: Dict[str, "Term"]) -> "DisjunctiveFact":
        return DisjunctiveFact(tuple([atom.substitute(subst) for atom in self.atoms]))

    def match(self, other: "Expr", subst: Optional["Substitution"]=None) -> "Substitution":
        pass


class DisjunctiveRule(Rule):
    """Disjunctive rule.
    
    Rule of form:

        h_1 | ... | h_m :- b_1,...,b_n .

    for classical atoms h_1,...,h_m and literals b_1,...,b_n.

    Semantically, any answer set that includes b_1,...,b_n must also include exactly one h_i.
    """
    def __init__(self, head: Tuple["PredicateLiteral", ...], body: Tuple["Literal", ...]) -> None:
        self.atoms = head
        self.literals = body

    def __repr__(self) -> str:
        return f"DisjunctiveRule[{' | '.join([repr(atom) for atom in self.head])}]({', '.join([repr(literal) for literal in self.body])})"

    def __str__(self) -> str:
        return f"{' | '.join([repr(atom) for atom in self.head])} :- {', '.join([str(literal) for literal in self.body])}."

    @property
    def head(self) -> Tuple["Literal"]:
        return self.atoms

    @property
    def body(self) -> Tuple["Literal"]:
        return self.literals

    def vars(self) -> Set["Variable"]:
        return set().union(*[atom.vars() for atom in self.head]).union(*[literal.vars() for literal in self.body])

    def substitute(self, subst: Dict[str, "Term"]) -> "DisjunctiveRule":
        return DisjunctiveFact(tuple([atom.substitute(subst) for atom in self.head]), tuple([literal.substitute(subst) for literal in self.body]))

    def match(self, other: "Expr", subst: Optional["Substitution"]=None) -> "Substitution":
        pass