from typing import Optional, Tuple, Set, TYPE_CHECKING
from functools import cached_property

from aspy.program.expression import Expr
from aspy.program.literals import LiteralTuple
from aspy.program.safety_characterization import SafetyTriplet

from .statement import Fact, Rule

if TYPE_CHECKING:
    from aspy.program.substitution import Substitution
    from aspy.program.terms import Term, Variable
    from aspy.program.literals import PredicateLiteral
    from aspy.program.operators import RelOp

    from .statement import Statement


class ChoiceElement(Expr):
    """Choice element."""
    def __init__(self, atom: "PredicateLiteral", literals: Optional["LiteralTuple"]=None) -> None:
        if literals is None:
            literals = LiteralTuple()

        self.atom = atom
        self.literals = literals
        self.ground = atom.ground and all(literal.ground for literal in literals)

    def __str__(self) -> str:
        return f"{str(self.atom)}:{','.join([str(literal) for literal in self.literals])}"

    @property
    def head(self) -> LiteralTuple:
        return LiteralTuple([self.atom])

    @property
    def body(self) -> LiteralTuple:
        return self.literals

    def vars(self, global_only: bool=False, bound_only: bool=False) -> Set["Variable"]:
        # TODO: bound, global !!!
        if bound_only or global_only:
            raise Exception()

        return set().union(literal.vars() for literal in self.literals)

    def safety(self, rule: Optional["Statement"], global_vars: Optional[Set["Variable"]]=None) -> "SafetyTriplet":
        raise Exception()

    def substitute(self, subst: "Substitution") -> "ChoiceElement":
        raise Exception("Substitution for choice elements not supported yet.")

    def match(self, other: Expr) -> Set["Substitution"]:
        raise Exception("Matching for choice elements not supported yet.")


class Choice(Expr):
    """Choice."""
    def __init__(self, elements: Optional[Tuple[ChoiceElement]]=None, lcomp: Optional[Tuple["RelOp", "Term"]]=None, rcomp: Optional[Tuple["RelOp", "Term"]]=None):
        if elements is None:
            elements = tuple()

        self.elements = elements
        self.lcomp = lcomp
        self.rcomp = rcomp
        self.ground = all(element.ground for element in elements)

    def __str__(self) -> str:
        return (f"{str(self.lcomp[1])} {str(self.lcomp[0])}" if self.lcomp else "") + f"{{{';'.join([str(literal) for literal in self.elements])}}}" + (f"{str(self.lcomp[0])} {str(self.lcomp[1])}" if self.lcomp else "")

    def guards(self) -> Tuple[Tuple["RelOp", "Term"], Tuple["RelOp", "Term"]]:
        return (self.lcomp, self.rcomp)

    def vars(self, global_only: bool=False, bound_only: bool=False) -> Set["Variable"]:
        # TODO: bound, global !!!
        if bound_only or global_only:
            raise Exception()

        return set().union(guard[1].vars() for guard in self.guards() if not guard is None)

    def substitute(self, subst: "Substitution") -> "Choice":
        # substitute elements recursively
        elements = (element.substitute(subst) for element in self.elements)
    
        # substitute guard terms recursively
        lcomp = (self.lcomp[0], self.lcomp[1].substitute(subst))
        rcomp = (self.rcomp[0], self.rcomp[1].substitute(subst))

        return Choice(elements, lcomp, rcomp)

    def match(self, other: Expr) -> Set["Substitution"]:
        raise Exception("Matching for choice expressions not supported yet.")


class ChoiceFact(Fact):
    """Choice fact.

    Rule of form

        u_1 R_1 { h_1,...,h_m } R_2 u_2 :- .

    for classical atoms h_1,...,h_m, terms u_1,u_2 and comparison operators R_1,R_2.
    The symbol ':-' may be omitted.

    TODO: R_1, R_2 may be omitted
    TODO: u_1,R_1 u_2,R_2 may be omitted.

    Semantically, any answer set may include any subset of {h_1,...,h_m} (including the empty set).
    """
    def __init__(self, head: Choice) -> None:
        self.choice = head
        self.ground = head.ground

    def __str__(self) -> str:
        return f"{{{','.join([str(literal) for literal in self.head.elements])}}}."

    @property
    def head(self) -> Choice:
        return self.choice

    @property
    def body(self) -> LiteralTuple:
        return LiteralTuple()

    def vars(self, global_only: bool=False, bound_only: bool=False) -> Set["Variable"]:
        # TODO: bound, global !!!
        if bound_only or global_only:
            raise Exception()

        return self.head.vars()

    def safety(self, rule: Optional["Statement"], global_vars: Optional[Set["Variable"]]=None) -> "SafetyTriplet":
        raise Exception()

    @cached_property
    def safe(self) -> bool:
        return len(self.vars()) > 0

    def substitute(self, subst: "Substitution") -> "ChoiceFact":
        return ChoiceFact(self.head.substitute(subst))

    def match(self, other: Expr) -> Set["Substitution"]:
        raise Exception("Matching for choice facts not supported yet.")


class ChoiceRule(Rule):
    """Choice rule.

    Rule of form:

        u_1 R_1 { h_1 ; ... ; h_m } R_2 u_2 :- b_1,...,b_n .

    for classical atoms h_1,...,h_m, literals b_1,...,b_n, terms u_1,u_2 and comparison operators R_1,R_2.

    Semantically, any answer set that includes b_1,...,b_n may also include any subset of {h_1,...,h_m} (including the empty set).
    """
    def __init__(self, head: Choice, body: LiteralTuple) -> None:
        self.head = head
        self.body = body
        self.ground = head.ground and body.ground

    def __str__(self) -> str:
        return f"{str(self.head)} :- {', '.join([str(literal) for literal in self.body])}."

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return set().union(*self.head.vars(global_only), *self.body.vars(global_only))

    def safety(self, rule: Optional["Statement"], global_vars: Optional[Set["Variable"]]=None) -> "SafetyTriplet":
        raise Exception()

    @cached_property
    def safe(self) -> bool:
        global_vars = self.vars(global_only=True)
        body_safety = SafetyTriplet.closure(self.body.safety(global_vars=global_vars))

        return body_safety == SafetyTriplet(global_vars)

    def substitute(self, subst: "Substitution") -> "ChoiceRule":
        return ChoiceRule(self.head.substitute(subst), self.body.substitute(subst))

    def match(self, other: Expr) -> Set["Substitution"]:
        raise Exception("Matching for choice rules not supported yet.")