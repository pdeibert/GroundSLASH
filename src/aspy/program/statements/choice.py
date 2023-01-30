from typing import Optional, Tuple, Union, Set, Dict, TYPE_CHECKING
from dataclasses import dataclass

from aspy.program.expression import Expr
from aspy.program.variable_set import VariableSet

from .statement import Fact, Rule

if TYPE_CHECKING:
    from aspy.program.expression import Substitution
    from aspy.program.terms import Term
    from aspy.program.literals import Literal, PredicateLiteral, CompOp
    
    from .disjunctive import DisjunctiveFact, DisjunctiveRule
    from .constraint import Constraint


class ChoiceElement(Expr):
    """Choice element."""
    def __init__(self, atom: "PredicateLiteral", literals: Optional[Tuple["Literal"]]=None) -> None:
        if literals is None:
            literals = tuple()

        self.atom = atom
        self.literals = literals

    def __repr__(self) -> str:
        return f"{repr(self.atom)}:{','.join([repr(literal) for literal in self.literals])}"

    def __str__(self) -> str:
        return f"{str(self.atom)}:{','.join([str(literal) for literal in self.literals])}"

    @property
    def head(self) -> Tuple["PredicateLiteral"]:
        return (self.atom,)

    @property
    def body(self) -> Tuple["Literal"]:
        return self.literals

    def vars(self) -> VariableSet:
        return sum([literal.vars() for literal in self.literals], VariableSet())

    def substitute(self, subst: Dict[str, "Term"]) -> "ChoiceElement":
        raise Exception()

    def match(self, other: "Expr", subst: Optional["Substitution"]=None) -> "Substitution":
        """Tries to match the expression with another one."""
        pass


class Choice(Expr):
    """Choice."""
    # TODO: rename literals to elements?
    def __init__(self, elements: Optional[Tuple[ChoiceElement]]=None, lcomp: Optional[Tuple["CompOp", "Term"]]=None, rcomp: Optional[Tuple["CompOp", "Term"]]=None):
        if elements is None:
            elements = tuple()

        self.elements = elements
        self.lcomp = lcomp
        self.rcomp = rcomp

    def __repr__(self) -> str:
        return "Choice(" + (f"{repr(self.lcomp[1])} {repr(self.lcomp[0])}" if self.lcomp else "") + f"{{{';'.join([repr(literal) for literal in self.elements])}}}" + (f"{repr(self.lcomp[0])} {repr(self.lcomp[1])}" if self.lcomp else "") + ")"

    def __str__(self) -> str:
        return (f"{str(self.lcomp[1])} {str(self.lcomp[0])}" if self.lcomp else "") + f"{{{';'.join([str(literal) for literal in self.elements])}}}" + (f"{str(self.lcomp[0])} {str(self.lcomp[1])}" if self.lcomp else "")

    def vars(self) -> VariableSet:

        vars = sum([literal.vars() for literal in self.elements], VariableSet())

        if not self.lcomp is None:
            vars.union(self.lcomp[1].vars())
        if not self.rcomp is None:
            vars.union(self.rcomp[1].vars())
        
        return vars

    def substitute(self, subst: Dict[str, "Term"]) -> "Choice":
        pass

    def match(self, other: "Expr", subst: Optional["Substitution"]=None) -> "Substitution":
        """Tries to match the expression with another one."""
        pass


@dataclass
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

    def __repr__(self) -> str:
        return f"ChoiceFact[{repr(self.head)}]"

    def __str__(self) -> str:
        return f"{{{','.join([str(literal) for literal in self.head.elements])}}}."

    @property
    def head(self) -> Choice:
        return self.choice

    @property
    def body(self) -> Tuple["Literal"]:
        return tuple()

    def vars(self) -> VariableSet:
        return self.head.vars()

    def transform(self) -> Tuple[Union["DisjunctiveFact", "Constraint"], ...]:
        """TODO"""
        raise Exception("Transformation of choice facts not supported yet.")

    def substitute(self, subst: Dict[str, "Term"]) -> "ChoiceFact":
        return ChoiceFact(self.head.substitute(subst))

    def match(self, other: "Expr", subst: Optional["Substitution"]=None) -> "Substitution":
        pass


@dataclass
class ChoiceRule(Rule):
    """Choice rule.

    Rule of form:

        u_1 R_1 { h_1 ; ... ; h_m } R_2 u_2 :- b_1,...,b_n .

    for classical atoms h_1,...,h_m, literals b_1,...,b_n, terms u_1,u_2 and comparison operators R_1,R_2.

    Semantically, any answer set that includes b_1,...,b_n may also include any subset of {h_1,...,h_m} (including the empty set).
    """
    head: Choice
    body: Tuple["Literal", ...]

    def __repr__(self) -> str:
        return f"ChoiceRule[{repr(self.head)}]({', '.join([repr(literal) for literal in self.body])})"

    def __str__(self) -> str:
        return f"{str(self.head)} :- {', '.join([str(literal) for literal in self.body])}."

    def vars(self) -> VariableSet:
        return sum([literal.vars() for literal in self.body], self.head.vars())

    def transform(self) -> Tuple[Union["DisjunctiveRule", "Constraint"], ...]:
        """TODO"""
        raise Exception("Transformation of choice rules not supported yet.")

    def substitute(self, subst: Dict[str, "Term"]) -> "ChoiceFact":
        return ChoiceFact(self.head.substitute(subst), tuple([literal.substitute(subst) for literal in self.body]))

    def match(self, other: "Expr", subst: Optional["Substitution"]=None) -> "Substitution":
        pass