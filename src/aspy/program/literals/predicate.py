from typing import Tuple, Optional, Union, Set, TYPE_CHECKING
from functools import cached_property

from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.substitution import Substitution
from aspy.program.terms import TermTuple

from .literal import Literal

if TYPE_CHECKING:
    from aspy.program.expression import Expr
    from aspy.program.terms import Term, Variable
    from aspy.program.statements import Statement
    from aspy.program.query import Query


class PredicateLiteral(Literal):
    """Predicate."""
    def __init__(self, name: str, terms: Optional[Union[TermTuple, Tuple["Term", ...]]]=None, cneg: bool=False, naf: bool=False) -> None:
        super().__init__(naf)

        if terms is None:
            terms = TermTuple()

        self.name = name
        self.terms = terms if isinstance(terms, TermTuple) else TermTuple(terms)
        self.cneg = cneg

    def __eq__(self, other: "PredicateLiteral") -> bool:
        return self.name == self.name and self.terms == self.terms and self.cneg == other.cneg and self.naf == other.naf

    def __hash__(self) -> int:
        return hash( (self.naf, self.cneg, self.name, *self.terms) )

    def __str__(self) -> str:
        terms_str = (f"({','.join([str(term) for term in self.terms])})" if self.terms else '')
        return f"{('not ' if self.naf else '')}{('- ' if self.cneg else '')}{self.name}{terms_str}"

    @property
    def arity(self) -> int:
        return len(self.terms)

    @cached_property
    def ground(self) -> bool:
        return all(term.ground for term in self.terms)

    def pred(self) -> Tuple[str, int]:
        return (self.name, self.arity)

    def pos(self) -> Set["Literal"]:
        # NOTE: naf flag gets dropped
        return {PredicateLiteral(self.name, self.terms, self.cneg)} if not self.naf else set()

    def neg(self) -> Set["Literal"]:
        # NOTE: naf flag gets dropped
        return {PredicateLiteral(self.name, self.terms, self.cneg)} if self.naf else set()

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return set().union(*self.terms(global_only))

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> Tuple[SafetyTriplet, ...]:
        return SafetyTriplet.closure(*self.terms.safety()) if not self.naf else SafetyTriplet(unsafe=self.vars())

    def match(self, other: "Expr") -> Set[Substitution]:
        """Tries to match the expression with another one."""
        if isinstance(other, PredicateLiteral) and self.name == other.name and self.arity == other.arity and self.cneg == other.cneg:

            subst = Substitution()

            # match terms
            for (self_term, other_term) in zip(self.terms, other.terms):
                matches = self_term.match(other_term)
            
            # no match found
            if len(matches) == 0:
                return set()

            # try to merge substitutions
            try:
                subst.merge(matches[0])
            except:
                return set()
        
            return set([subst])
        else:
            return set()

    def substitute(self, subst: Substitution) -> "PredicateLiteral":
        # substitute terms recursively
        terms = (term.substitute(subst) for term in self.terms)

        return PredicateLiteral(self.name, *terms, self.cneg)