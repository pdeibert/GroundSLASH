from typing import Optional, Tuple, Set, Dict, TYPE_CHECKING
from dataclasses import dataclass
from functools import cached_property

from aspy.program.expression import Substitution, MatchError, AssignmentError
from aspy.program.safety import Safety
from aspy.program.variable_set import VariableSet

from .term import Term, Infimum, Number, SymbolicConstant, String

if TYPE_CHECKING:
    from aspy.program.expression import Expr


@dataclass
class Functional(Term):
    functor: str
    terms: Tuple[Term, ...]

    def __lshift__(self, other: Term) -> bool:
        if isinstance(other, (Infimum, Number, SymbolicConstant, String)):
            return False
        elif isinstance(other, Functional):
            if self.arity < other.arity:
                return True
            elif self.arity == other.arity:
                if self.functor < other.functor:
                    return True
                elif self.functor == other.functor:
                    for self_term, other_term in zip(self.terms, other.terms):
                        if self_term > other_term:
                            return False
                    
                    return True

        return False

    def __repr__(self) -> str:
        return f"Func[{self.functor}]" + (f"({','.join([repr(term) for term in self.terms])})" if self.terms else '')

    def __str__(self) -> str:
        return self.functor + (f"({','.join([str(term) for term in self.terms])})" if self.terms else '')

    @cached_property
    def arity(self) -> int:
        return len(self.terms)

    def vars(self) -> VariableSet:
        return sum([term.vars() for term in self.terms], VariableSet())

    def safety(self) -> Safety:
        # return closure of terms' safety characterizations
        return Safety.closure(tuple([term.safety() for term in self.terms]))

    def substitute(self, subst: Dict[str, Term]) -> "Functional":
        return Functional(
            self.functor,
            tuple(term.substitute(subst) for term in self.terms)
        )

    def match(self, other: "Expr", subst: Optional[Substitution]=None) -> Substitution:
        if subst is None:
            subst = Substitution()

        # 'other' is a functional term with same symbol and arity
        if isinstance(other, Functional) and other.functor == self.functor and other.arity == self.arity:
            # match terms
            try:
                for my_term, other_term in zip(self.terms, other.terms):
                    term_subst = my_term.match(other_term)
                    
                    # combine substitutions
                    subst.merge(term_subst)
  
                # return final substitution
                return subst
            except (MatchError, AssignmentError):
                raise MatchError(self, other)
        else:
            # cannot be matched
            raise MatchError(self, other)