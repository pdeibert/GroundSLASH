from copy import deepcopy
from typing import TYPE_CHECKING, Optional

import aspy
from aspy.program.literals import (
    AggrBaseLiteral,
    AggrElemLiteral,
    ChoiceBaseLiteral,
    ChoiceElemLiteral,
    LiteralTuple,
)
from aspy.program.literals.builtin import op2rel
from aspy.program.substitution import Substitution
from aspy.program.terms import Number, TermTuple

from .normal import NormalRule

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.expression import Expr
    from aspy.program.literals import AggregateElement, Guard
    from aspy.program.statements.choice import ChoiceElement
    from aspy.program.terms import Term
    from aspy.program.variable_table import VariableTable


class AggrBaseRule(NormalRule):
    """TODO."""

    def __init__(
        self,
        atom: AggrBaseLiteral,
        lguard: Optional["Guard"],
        rguard: Optional["Guard"],
        literals: "LiteralTuple",
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
    ) -> "AggrBaseRule":

        # check if global vars is tuple (important for FIXED order)
        if aspy.debug():
            if not isinstance(glob_vars, TermTuple):
                raise ValueError(
                    f"Argument 'global_vars' for {cls} must be of type {TermTuple}."
                )
            if (lguard is not None and lguard.right) or (
                rguard is not None and not rguard.right
            ):
                raise ValueError(
                    f"Left or right guard for {cls} must indicate the correct side."
                )

        # create head atom/literal
        atom = AggrBaseLiteral(aggr_id, glob_vars, deepcopy(glob_vars))
        # compute guard literals and combine them with non-aggregate literals
        lguard_literal = (
            op2rel[lguard.op](lguard.bound, base_value) if lguard is not None else None
        )
        rguard_literal = (
            op2rel[rguard.op](base_value, rguard.bound) if rguard is not None else None
        )
        guard_literals = LiteralTuple(
            *tuple(
                guard_literal
                for guard_literal in (lguard_literal, rguard_literal)
                if guard_literal is not None
            )
        )

        return AggrBaseRule(atom, lguard, rguard, guard_literals + non_aggr_literals)

    def substitute(self, subst: "Substitution") -> "AggrBaseRule":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return AggrBaseRule(
            self.atom.substitute(subst), *self.guards, self.literals.substitute(subst)
        )

    def replace_arith(self, var_table: "VariableTable") -> "AggrBaseRule":
        return AggrBaseRule(
            self.atom.replace_arith(var_table),
            *self.guards,
            self.literals.replace_arith(var_table),
        )

    def gather_var_assignment(self) -> Substitution:
        """Get substitution of local and global variables from rules. Remaining variables will simply be mapped onto themselves."""  # noqa
        return self.atom.gather_var_assignment()


class AggrElemRule(NormalRule):
    """TODO."""

    def __init__(
        self,
        atom: AggrElemLiteral,
        element: "AggregateElement",
        literals: "LiteralTuple",
    ) -> None:
        super().__init__(atom, *literals)
        self.element = element

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, AggrElemRule)
            and self.atom == other.atom
            and self.literals == other.literals
            and self.element == other.element
        )

    def __hash__(self) -> int:
        return hash(("aggr element rule", self.atom, self.literals, self.element))

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
    ) -> "AggrElemRule":

        # compute local variables
        local_vars = TermTuple(
            *tuple(var for var in element.vars() if var not in glob_vars)
        )

        # create head atom/literal
        atom = AggrElemLiteral(
            aggr_id, element_id, local_vars, glob_vars, local_vars + glob_vars
        )
        # combine element literals with non-aggregate literals
        literals = element.literals + non_aggr_literals

        return AggrElemRule(atom, element, literals)

    def substitute(self, subst: "Substitution") -> "AggrElemRule":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return AggrElemRule(
            self.atom.substitute(subst), self.element, self.literals.substitute(subst)
        )

    def replace_arith(self, var_table: "VariableTable") -> "AggrElemRule":
        return AggrElemRule(
            self.atom.replace_arith(var_table),
            self.element,
            self.literals.replace_arith(var_table),
        )

    def gather_var_assignment(self) -> Substitution:
        """Get substitution of local and global variables from rules. Remaining variables will simply be mapped onto themselves."""  # noqa
        return self.atom.gather_var_assignment()


class ChoiceBaseRule(NormalRule):
    """TODO."""

    def __init__(
        self,
        atom: ChoiceBaseLiteral,
        lguard: Optional["Guard"],
        rguard: Optional["Guard"],
        literals: "LiteralTuple",
    ) -> None:

        super().__init__(atom, *literals)
        self.guards = (lguard, rguard)

    @property
    def choice_id(self) -> int:
        return self.atom.choice_id

    @property
    def glob_vars(self) -> TermTuple:
        return self.atom.glob_vars

    @classmethod
    def from_scratch(
        cls,
        choice_id: int,
        glob_vars: TermTuple,
        lguard: Optional["Guard"],
        rguard: Optional["Guard"],
        non_aggr_literals: "LiteralTuple",
    ) -> "ChoiceBaseRule":

        # check if global vars is tuple (important for FIXED order)
        if aspy.debug():
            if not isinstance(glob_vars, TermTuple):
                raise ValueError(
                    f"Argument 'global_vars' for {cls} must be of type {TermTuple}."
                )
            if (lguard is not None and lguard.right) or (
                rguard is not None and not rguard.right
            ):
                raise ValueError(
                    f"Left or right guard for {cls} must indicate the correct side."
                )

        # create head atom/literal
        atom = ChoiceBaseLiteral(choice_id, glob_vars, deepcopy(glob_vars))
        # compute guard literals and combine them with non-aggregate literals
        lguard_literal = (
            op2rel[lguard.op](lguard.bound, Number(0)) if lguard is not None else None
        )
        rguard_literal = (
            op2rel[rguard.op](Number(0), rguard.bound) if rguard is not None else None
        )
        guard_literals = LiteralTuple(
            *tuple(
                guard_literal
                for guard_literal in (lguard_literal, rguard_literal)
                if guard_literal is not None
            )
        )

        return ChoiceBaseRule(atom, lguard, rguard, guard_literals + non_aggr_literals)

    def substitute(self, subst: "Substitution") -> "ChoiceBaseRule":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return ChoiceBaseRule(
            self.atom.substitute(subst), *self.guards, self.literals.substitute(subst)
        )

    def replace_arith(self, var_table: "VariableTable") -> "ChoiceBaseRule":
        return ChoiceBaseRule(
            self.atom.replace_arith(var_table),
            *self.guards,
            self.literals.replace_arith(var_table),
        )

    def gather_var_assignment(self) -> Substitution:
        """Get substitution of local and global variables from rules. Remaining variables will simply be mapped onto themselves."""  # noqa
        return self.atom.gather_var_assignment()


class ChoiceElemRule(NormalRule):
    """TODO."""

    def __init__(
        self,
        atom: ChoiceElemLiteral,
        element: "ChoiceElement",
        literals: "LiteralTuple",
    ) -> None:
        super().__init__(atom, *literals)
        self.element = element

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, ChoiceElemRule)
            and self.atom == other.atom
            and self.literals == other.literals
            and self.element == other.element
        )

    def __hash__(self) -> int:
        return hash(("choice element rule", self.atom, self.literals, self.element))

    @property
    def choice_id(self) -> int:
        return self.atom.choice_id

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
        element: "ChoiceElement",
        non_aggr_literals: "LiteralTuple",
    ) -> "ChoiceElemRule":

        # compute local variables
        local_vars = TermTuple(
            *tuple(var for var in element.vars() if var not in glob_vars)
        )

        # create head atom/literal
        atom = ChoiceElemLiteral(
            aggr_id, element_id, local_vars, glob_vars, local_vars + glob_vars
        )
        # combine element literals with non-aggregate literals
        literals = element.literals + non_aggr_literals

        return ChoiceElemRule(atom, element, literals)

    def substitute(self, subst: "Substitution") -> "AggrElemRule":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return ChoiceElemRule(
            self.atom.substitute(subst), self.element, self.literals.substitute(subst)
        )

    def replace_arith(self, var_table: "VariableTable") -> "ChoiceElemRule":
        return ChoiceElemRule(
            self.atom.replace_arith(var_table),
            self.element,
            self.literals.replace_arith(var_table),
        )

    def gather_var_assignment(self) -> Substitution:
        """Get substitution of local and global variables from rules. Remaining variables will simply be mapped onto themselves."""  # noqa
        return self.atom.gather_var_assignment()
