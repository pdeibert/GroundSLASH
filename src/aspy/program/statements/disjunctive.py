from typing import Set, Union, Tuple, Optional, TYPE_CHECKING
from functools import cached_property

import aspy
from aspy.program.symbol_table import SymbolTable
from aspy.program.literals import LiteralTuple, PredicateLiteral
from aspy.program.safety_characterization import SafetyTriplet

from .statement import Fact, Rule
from .normal import NormalFact, NormalRule

if TYPE_CHECKING:
    from aspy.program.expression import Expr
    from aspy.program.terms import Variable
    from aspy.program.substitution import Substitution
    from aspy.program.statements import Statement
    from aspy.program.literals import Literal


class DisjunctiveFact(Fact):
    """Disjunctive fact.
    
    Rule of form

        h_1 | ... | h_m :- .

    for classical atoms h_1,...,h_m. The symbol ':-' may be omitted.

    Semantically, any answer set must include exactly one classical atom h_i.
    """
    def __init__(self, *atoms: PredicateLiteral, **kwargs) -> None:
        super().__init__(**kwargs)

        if len(atoms) < 2:
            raise ValueError(f"Head for {type(self)} requires at least two literals. Use {type(NormalFact)} instead.")

        if aspy.debug() and not all(isinstance(atom, PredicateLiteral) and not atom.naf for atom in atoms):
            raise ValueError(f"Head literals for {type(self)} must all be positive literals of type {type(PredicateLiteral)}.")

        self.atoms = LiteralTuple(*atoms)

    def __str__(self) -> str:
        return '|'.join([str(atom) for atom in self.head]) + '.'

    @property
    def head(self) -> LiteralTuple:
        return self.atoms

    @property
    def body(self) -> LiteralTuple:
        return LiteralTuple()

    def safety(self, rule: Optional["Statement"], global_vars: Optional[Set["Variable"]]=None) -> "SafetyTriplet":
        raise Exception()

    @cached_property
    def safe(self) -> bool:
        return len(self.vars()) == 0

    @cached_property
    def ground(self) -> bool:
        return self.head.ground

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
    def __init__(self, head: Union[LiteralTuple, Tuple["Literal", ...]], *body: "Literal", **kwargs) -> None:
        super().__init__(**kwargs)

        if len(head) < 2:
            raise ValueError(f"Head for {type(self)} requires at least two literals. Use {type(NormalRule)} instead.")
        if len(body) == 0:
            raise ValueError(f"Body for {type(DisjunctiveRule)} may not be empty.")

        if aspy.debug() and not all(isinstance(atom, PredicateLiteral) and not atom.naf for atom in head):
            raise ValueError(f"Head literals for {type(self)} must all be positive literals of type {type(PredicateLiteral)}.")

        self.atoms = head if isinstance(head, LiteralTuple) else LiteralTuple(*head)
        self.literals = LiteralTuple(*body)

    def __str__(self) -> str:
        return f"{'|'.join([str(atom) for atom in self.head])} :- {', '.join([str(literal) for literal in self.body])}."

    @property
    def head(self) -> LiteralTuple:
        return self.atoms

    @property
    def body(self) -> LiteralTuple:
        return self.literals

    @cached_property
    def safe(self) -> bool:
        global_vars = self.vars(global_only=True)
        body_safety = SafetyTriplet.closure(*self.body.safety(global_vars=global_vars))

        return body_safety == SafetyTriplet(global_vars)

    @cached_property
    def ground(self) -> bool:
        return self.head.ground and self.body.ground

    def substitute(self, subst: "Substitution") -> "DisjunctiveRule":
        return DisjunctiveRule(self.head.substitute(subst), self.literals.substitute(subst))

    def match(self, other: "Expr") -> Set["Substitution"]:
        raise Exception("Matching for disjunctive rules not supported yet.")

    def rewrite(self, sym_table: SymbolTable) -> Tuple["Rule"]:
        raise Exception("Rewritten for disjunctive rules not supported yet.")