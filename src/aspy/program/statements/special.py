from copy import deepcopy
from typing import TYPE_CHECKING, Optional

import aspy
from aspy.program.literals import EpsLiteral, EtaLiteral, LiteralTuple
from aspy.program.literals.builtin import op2rel
from aspy.program.substitution import Substitution
from aspy.program.terms import TermTuple

from .normal import NormalRule

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.expression import Expr
    from aspy.program.literals import AggregateElement, Guard
    from aspy.program.terms import Term
    from aspy.program.variable_table import VariableTable


class EpsRule(NormalRule):
    """TODO."""

    def __init__(
        self, atom: EpsLiteral, lguard: Optional["Guard"], rguard: Optional["Guard"], literals: "LiteralTuple"
    ) -> None:

        super().__init__(atom, *literals)
        self.guards = (lguard, rguard)

    @property
    def aggr_id(self) -> int:
        return self.atom.aggr_id

    @property
    def glob_vars(self) -> TermTuple:
        return self.atom.glob_vars

    @classmethod
    def from_scratch(
        cls,
        aggr_id: int,
        glob_vars: TermTuple,
        lguard: Optional["Guard"],
        rguard: Optional["Guard"],
        base_value: "Term",
        non_aggr_literals: "LiteralTuple",
    ) -> "EpsRule":

        # check if global vars is tuple (important for FIXED order)
        if aspy.debug():
            if not isinstance(glob_vars, TermTuple):
                raise ValueError(f"Argument 'global_vars' for {cls} must be of type {TermTuple}.")
            if (lguard is not None and lguard.right) or (rguard is not None and not rguard.right):
                raise ValueError(f"Left or right guard for {cls} must indicate the correct side.")

        # create head atom/literal
        atom = EpsLiteral(aggr_id, glob_vars, deepcopy(glob_vars))
        # compute guard literals and combine them with non-aggregate literals
        lguard_literal = op2rel[lguard.op](lguard.bound, base_value) if lguard is not None else None
        rguard_literal = op2rel[rguard.op](base_value, rguard.bound) if rguard is not None else None
        guard_literals = LiteralTuple(
            *tuple(guard_literal for guard_literal in (lguard_literal, rguard_literal) if guard_literal is not None)
        )

        return EpsRule(atom, lguard, rguard, guard_literals + non_aggr_literals)

    def substitute(self, subst: "Substitution") -> "EpsRule":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return EpsRule(self.atom.substitute(subst), *self.guards, self.literals.substitute(subst))

    def replace_arith(self, var_table: "VariableTable") -> "EpsRule":
        return EpsRule(self.atom.replace_arith(var_table), *self.guards, self.literals.replace_arith(var_table))

    def gather_var_assignment(self) -> Substitution:
        """Get substitution of local and global variables from rules. Remaining variables will simply be mapped onto themselves."""
        return self.atom.gather_var_assignment()


class EtaRule(NormalRule):
    """TODO."""

    def __init__(self, atom: EtaLiteral, element: "AggregateElement", literals: "LiteralTuple") -> None:
        super().__init__(atom, *literals)
        self.element = element

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, EtaRule)
            and self.atom == other.atom
            and self.literals == other.literals
            and self.element == other.element
        )

    def __hash__(self) -> int:
        return hash(("eta rule", self.atom, self.literals, self.element))

    @property
    def aggr_id(self) -> int:
        return self.atom.aggr_id

    @property
    def element_id(self) -> int:
        return self.atom.element_id

    @property
    def local_vars(self) -> int:
        return self.atom.local_vars

    @property
    def glob_vars(self) -> int:
        return self.atom.glob_vars

    @classmethod
    def from_scratch(
        cls,
        aggr_id: int,
        element_id: int,
        glob_vars: TermTuple,
        element: "AggregateElement",
        non_aggr_literals: "LiteralTuple",
    ) -> "EtaRule":

        # compute local variables
        local_vars = TermTuple(*tuple(var for var in element.vars() if var not in glob_vars))

        # create head atom/literal
        atom = EtaLiteral(aggr_id, element_id, local_vars, glob_vars, local_vars + glob_vars)
        # combine element literals with non-aggregate literals
        literals = element.literals + non_aggr_literals

        return EtaRule(atom, element, literals)

    def substitute(self, subst: "Substitution") -> "EtaRule":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return EtaRule(self.atom.substitute(subst), self.element, self.literals.substitute(subst))

    def replace_arith(self, var_table: "VariableTable") -> "EtaRule":
        return EtaRule(self.atom.replace_arith(var_table), self.element, self.literals.replace_arith(var_table))

    def gather_var_assignment(self) -> Substitution:
        """Get substitution of local and global variables from rules. Remaining variables will simply be mapped onto themselves."""
        return self.atom.gather_var_assignment()
