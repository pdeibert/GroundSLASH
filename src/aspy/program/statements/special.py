from typing import Optional, Set, TYPE_CHECKING

import aspy
from aspy.program.terms import TermTuple
from aspy.program.literals import PredicateLiteral
from aspy.program.symbol_table import SpecialChar
from aspy.program.substitution import Substitution

from .normal import NormalRule

if TYPE_CHECKING:
    from aspy.program.terms import Term
    from aspy.program.literals import Guard, LiteralTuple, AggregateElement


class EpsRule(NormalRule):
    """TODO."""
    def __init__(self, aggr_id: int, global_vars: TermTuple, base_value: "Term", lguard: Optional["Guard"], rguard: Optional["Guard"], non_aggr_literals: "LiteralTuple") -> None:

        # check if global vars is tuple (important for FIXED order)
        if aspy.debug() and not isinstance(global_vars, TermTuple):
            raise ValueError("Argument 'global_vars' for {type(self)} must be of type {TermTuple}.")

        lguard_literal = lguard.op.ast(lguard.bound, base_value) if lguard is not None else None
        rguard_literal = rguard.op.ast(base_value, rguard.bound) if rguard is not None else None

        super().__init__(
            PredicateLiteral(f"{SpecialChar.EPS}{aggr_id}", *global_vars),
            *tuple(guard_literal for guard_literal in {lguard_literal, rguard_literal} if guard_literal is not None),
            *non_aggr_literals
        )

        self.aggr_id = aggr_id
        self.global_vars = global_vars
        self.guards = (lguard, rguard)

    # TODO: other methods?

    def get_glob_subst(self) -> Substitution:
        """Get substitution of global variables from rules. Existing variables will simply be mapped onto themselves."""
        return Substitution({var: term for var, term in zip(self.global_vars, self.atom.terms) if var != term})


class EtaRule(NormalRule):
    """TODO."""
    def __init__(self, aggr_id: int, element_id: int, global_vars: TermTuple, element: "AggregateElement", non_aggr_literals: "LiteralTuple") -> None:

        # check if global vars is tuple (important for FIXED order)
        if aspy.debug() and not isinstance(global_vars, TermTuple):
            raise ValueError("Argument 'global_vars' for {type(self)} must be of type {TermTuple}.")

        super().__init__(
            PredicateLiteral(f"{SpecialChar.ETA}{aggr_id}_{element_id}", *global_vars, *element.terms),
            *element.literals,
            *non_aggr_literals
        )

        self.aggr_id = aggr_id
        self.element_id = element_id
        self.global_vars = global_vars
        self.element = element

    # TODO: other methods?

    def get_glob_subst(self) -> Substitution:
        """Get substitution of global variables from rules. Existing variables will simply be mapped onto themselves."""
        """Get substitution of global variables from rules. Existing variables will simply be mapped onto themselves."""
        return Substitution({var: term for var, term in zip(self.global_vars, self.atom.terms) if var != term})
