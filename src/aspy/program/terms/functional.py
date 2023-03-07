from copy import deepcopy
from functools import cached_property
from typing import TYPE_CHECKING, Optional, Set, Union

import aspy
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.substitution import Substitution
from aspy.program.symbol_table import SYM_CONST_RE

from .term import Infimum, Number, String, SymbolicConstant, Term, TermTuple

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.expression import Expr
    from aspy.program.query import Query
    from aspy.program.statements import Statement
    from aspy.program.terms import Variable
    from aspy.program.variable_table import VariableTable


class Functional(Term):
    """Represents a functional term."""

    def __init__(self, symbol: str, *terms: Term) -> None:

        # check if functor name is valid
        if aspy.debug() and not SYM_CONST_RE.fullmatch(symbol):
            raise ValueError(f"Invalid value for {type(self)}: {symbol}")

        self.symbol = symbol
        self.terms = TermTuple(*terms)

    def __str__(self) -> str:
        return self.symbol + (f"({','.join([str(term) for term in self.terms])})")

    def __eq__(self, other: "Expr") -> str:
        return (
            isinstance(other, Functional)
            and other.symbol == self.symbol
            and other.terms == self.terms
        )

    def __hash__(self) -> int:
        return hash(("functional", self.symbol, self.terms))

    @property
    def arity(self) -> int:
        return len(self.terms)

    @cached_property
    def ground(self) -> bool:
        return self.terms.ground

    def precedes(self, other: Term) -> bool:
        if isinstance(other, (Infimum, Number, SymbolicConstant, String)):
            return False
        elif isinstance(other, Functional):
            if self.arity < other.arity:
                return True
            elif self.arity == other.arity:
                if self.symbol < other.symbol:
                    return True
                elif self.symbol == other.symbol:
                    for self_term, other_term in zip(self.terms, other.terms):
                        # other_term < self_term
                        if other_term.precedes(self_term) and not self_term.precedes(
                            other_term
                        ):
                            return False

                    return True

        return False

    def vars(self) -> Set["Variable"]:
        return self.terms.vars()

    def safety(
        self, rule: Optional[Union["Statement", "Query"]] = None
    ) -> SafetyTriplet:
        return SafetyTriplet.closure(*self.terms.safety())

    def match(self, other: "Expr") -> Optional[Substitution]:
        """Tries to match the expression with another one."""
        if not (
            isinstance(other, Functional)
            and self.symbol == other.symbol
            and self.arity == other.arity
        ):
            return None

        return self.terms.match(other.terms)

    def substitute(self, subst: Substitution) -> "Functional":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        terms = (term.substitute(subst) for term in self.terms)

        return Functional(self.symbol, *terms)

    def replace_arith(self, var_table: "VariableTable") -> "Functional":
        return Functional(self.symbol, *self.terms.replace_arith(var_table))
