from copy import deepcopy
from functools import cached_property
from typing import TYPE_CHECKING, Optional, Set, Tuple, Union

import aspy
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.substitution import Substitution
from aspy.program.symbol_table import SYM_CONST_RE
from aspy.program.terms import TermTuple

from .literal import Literal

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.expression import Expr
    from aspy.program.query import Query
    from aspy.program.statements import Statement
    from aspy.program.terms import Term, Variable
    from aspy.program.variable_table import VariableTable


class PredicateLiteral(Literal):
    """Predicate."""

    def __init__(
        self, name: str, *terms: "Term", neg: bool = False, naf: bool = False
    ) -> None:
        super().__init__(naf)

        # check if predicate name is valid
        if aspy.debug() and not SYM_CONST_RE.fullmatch(name):
            raise ValueError(f"Invalid value for {type(self)}: {name}")

        self.name = name
        self.neg = neg
        self.terms = TermTuple(*terms)

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, PredicateLiteral)
            and self.name == other.name
            and self.terms == other.terms
            and self.neg == other.neg
            and self.naf == other.naf
        )

    def __hash__(self) -> int:
        return hash(("predicate literal", self.naf, self.neg, self.name, *self.terms))

    def __str__(self) -> str:
        terms_str = (
            f"({','.join([str(term) for term in self.terms])})" if self.terms else ""
        )
        return f"{('not ' if self.naf else '')}{('-' if self.neg else '')}{self.name}{terms_str}" # noqa

    @property
    def arity(self) -> int:
        return len(self.terms)

    @cached_property
    def ground(self) -> bool:
        return all(term.ground for term in self.terms)

    def set_neg(self, value: bool = True) -> None:
        self.neg = value

    def set_naf(self, value: bool = True) -> None:
        self.naf = value

    def pred(self) -> Tuple[str, int]:
        return (self.name, self.arity)

    def pos_occ(self) -> Set["Literal"]:
        if self.naf:
            return set()

        return {PredicateLiteral(self.name, *self.terms.terms, neg=self.neg)}

    def neg_occ(self) -> Set["Literal"]:
        if not self.naf:
            return set()

        # NOTE: naf flag gets dropped
        return {PredicateLiteral(self.name, *self.terms.terms, neg=self.neg)}

    def vars(self) -> Set["Variable"]:
        return set().union(self.terms.vars())

    def safety(
        self, rule: Optional[Union["Statement", "Query"]] = None
    ) -> Tuple[SafetyTriplet, ...]:
        return (
            SafetyTriplet.closure(*self.terms.safety())
            if not self.naf
            else SafetyTriplet(unsafe=self.vars())
        )

    def match(self, other: "Expr") -> Optional[Substitution]:
        """Tries to match the expression with another one."""
        if (
            isinstance(other, PredicateLiteral)
            and self.name == other.name
            and self.arity == other.arity
            and self.neg == other.neg
        ):
            return self.terms.match(other.terms)

        return None

    def substitute(self, subst: Substitution) -> "PredicateLiteral":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return PredicateLiteral(
            self.name,
            *tuple((term.substitute(subst) for term in self.terms)),
            neg=self.neg,
            naf=self.naf,
        )

    def replace_arith(self, var_table: "VariableTable") -> "PredicateLiteral":
        return PredicateLiteral(
            self.name, *self.terms.replace_arith(var_table), neg=self.neg, naf=self.naf
        )
