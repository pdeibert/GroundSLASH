from typing import Tuple, Dict, Set, Optional, TYPE_CHECKING
from functools import cached_property

from aspy.program.safety import Safety
from aspy.program.variable_set import VariableSet

from .literal import Literal

if TYPE_CHECKING:
    from aspy.program.expression import Expr, Substitution
    from aspy.program.terms import Term


class PredicateLiteral(Literal):
    """Predicate."""
    def __init__(self, name: str, terms: Optional[Tuple["Term", ...]]=None, cneg: bool=False, naf: bool=False) -> None:
        super().__init__(naf)

        if terms is None:
            terms = tuple()

        self.name = name
        self.terms = terms
        self.cneg = cneg

    def __repr__(self) -> str:
        literal_str = ('-' if self.cneg else "") + f"PredicateLiteral[{self.name}]({','.join([repr(term) for term in self.terms])})"

        if self.naf:
            literal_str = f"Naf({literal_str})"

        return literal_str

    def __repr__(self) -> str:
        return ('not ' if self.naf else "") + ('- ' if self.cneg else "") + self.name + (f"({','.join([str(term) for term in self.terms])})" if self.terms else "")

    @cached_property
    def arity(self) -> int:
        return len(self.terms)

    def vars(self) -> VariableSet:
        return sum([term.vars() for term in self.terms], VariableSet())

    def safety(self) -> Safety:
        # literal is negative (NaF-negated)
        if self.naf:
            return Safety(VariableSet(), self.vars(), set())
        # literal is positive
        else:
            return Safety.closure(tuple([term.safety() for term in self.terms]))

    def substitute(self, subst: Dict[str, "Term"]) -> "PredicateLiteral":
        return PredicateLiteral(
            self.name,
            tuple(term.substitute(subst) for term in self.terms),
            self.cneg,
            self.naf
        )

    def match(self, other: "Expr", subst: Optional["Substitution"]=None) -> "Substitution":
        raise Exception()