from typing import Tuple, Optional, Union, Set, TYPE_CHECKING
from functools import cached_property

import aspy
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.substitution import Substitution
from aspy.program.terms import TermTuple
from aspy.program.symbol_table import SYM_CONST_RE

from .literal import Literal

if TYPE_CHECKING:
    from aspy.program.expression import Expr
    from aspy.program.terms import Term, Variable
    from aspy.program.statements import Statement
    from aspy.program.query import Query
    from aspy.program.variable_table import VariableTable


class PredicateLiteral(Literal):
    """Predicate."""
    def __init__(self, name: str, *terms: "Term") -> None:
        super().__init__(False)

        # check if predicate name is valid
        if aspy.debug() and not SYM_CONST_RE.fullmatch(name):
            raise ValueError(f"Invalid value for {type(self)}: {name}")

        self.name = name
        self.neg = False
        self.terms = TermTuple(*terms)

    def __eq__(self, other: "Expr") -> bool:
        return self.name == self.name and self.terms == self.terms and self.neg == other.neg and self.naf == other.naf

    def __hash__(self) -> int:
        return hash( (self.naf, self.neg, self.name, *self.terms) )

    def __str__(self) -> str:
        terms_str = (f"({','.join([str(term) for term in self.terms])})" if self.terms else '')
        return f"{('not ' if self.naf else '')}{('-' if self.neg else '')}{self.name}{terms_str}"

    @property
    def arity(self) -> int:
        return len(self.terms)

    @cached_property
    def ground(self) -> bool:
        return all(term.ground for term in self.terms)

    def set_neg(self, value: bool=True) -> None:
        self.neg = value

    def set_naf(self, value: bool=True) -> None:
        self.naf = value

    def pred(self) -> Tuple[str, int]:
        return (self.name, self.arity)

    def pos_occ(self) -> Set["Literal"]:
        if self.naf:
            return set()

        literal = PredicateLiteral(self.name, *self.terms.terms)
        literal.set_neg(self.neg)

        return {literal}

    def neg_occ(self) -> Set["Literal"]:
        if not self.naf:
            return set()

        # NOTE: naf flag gets dropped
        literal = PredicateLiteral(self.name, *self.terms.terms)
        literal.set_neg(self.neg)

        return {literal}

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return set().union(self.terms.vars(global_only))

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> Tuple[SafetyTriplet, ...]:
        return SafetyTriplet.closure(*self.terms.safety()) if not self.naf else SafetyTriplet(unsafe=self.vars())

    def match(self, other: "Expr") -> Set[Substitution]:
        """Tries to match the expression with another one."""
        if isinstance(other, PredicateLiteral) and self.name == other.name and self.arity == other.arity and self.neg == other.neg:

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
        literal = PredicateLiteral(self.name, *tuple((term.substitute(subst) for term in self.terms)))
        literal.set_neg(self.neg)
        literal.set_naf(self.naf)

        return literal

    def replace_arith(self, var_table: "VariableTable") -> "PredicateLiteral":
        literal = PredicateLiteral(self.name, *tuple(term.replace_arith(var_table) for term in self.terms))
        literal.set_neg(self.neg)
        literal.set_naf(self.naf)

        return literal