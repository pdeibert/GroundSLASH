from abc import ABC
from copy import deepcopy
from typing import TYPE_CHECKING, Set

from aspy.program.literals import PredicateLiteral
from aspy.program.substitution import Substitution
from aspy.program.symbols import SpecialChar
from aspy.program.terms import TermTuple

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.expression import Expr
    from aspy.program.variable_table import VariableTable


class AuxLiteral(PredicateLiteral, ABC):
    """TODO."""

    def __init__(self, name: str, *args, **kwargs) -> None:
        super().__init__("f", *args, **kwargs)
        self.name = name  # TODO: better way to avoid regex check in 'PredicateLiteral'?


class AggrPlaceholder(AuxLiteral):
    """TODO."""

    def __init__(
        self, aggr_id: int, glob_vars: TermTuple, terms: TermTuple, naf: bool = False
    ) -> None:

        if len(glob_vars) != len(terms):
            raise ValueError(
                f"Number of global variables for {type(self)} does not match number of specified terms."  # noqa
            )

        super().__init__(f"{SpecialChar.ALPHA.value}{aggr_id}", *terms, naf=naf)
        self.aggr_id = aggr_id
        self.glob_vars = glob_vars

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, AggrPlaceholder)
            and self.aggr_id == other.aggr_id
            and self.glob_vars == other.glob_vars
            and self.terms == other.terms
        )

    def __hash__(self) -> int:
        return hash(("alpha literal", self.aggr_id, self.glob_vars, self.terms))

    def set_neg(self, value: bool = True) -> None:
        raise Exception(
            f"Classical negation cannot be set for literal of type {type(AggrPlaceholder)}."  # noqa
        )

    def pos_occ(self) -> Set["AggrPlaceholder"]:
        if self.naf:
            return set()

        return {AggrPlaceholder(self.aggr_id, self.glob_vars, self.terms)}

    def neg_occ(self) -> Set["AggrPlaceholder"]:
        if not self.naf:
            return set()

        # NOTE: naf flag gets dropped
        return {AggrPlaceholder(self.aggr_id, self.glob_vars, self.terms)}

    def substitute(self, subst: "Substitution") -> "AggrPlaceholder":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return AggrPlaceholder(
            self.aggr_id,
            self.glob_vars,
            TermTuple(*tuple(term.substitute(subst) for term in self.terms)),
            naf=self.naf,
        )

    def replace_arith(self, var_table: "VariableTable") -> "AggrPlaceholder":
        return AggrPlaceholder(self.aggr_id, self.glob_vars, self.terms, naf=self.naf)

    def gather_var_assignment(self) -> Substitution:
        """Get substitution of global variables from rules. Remaining variables will simply be mapped onto themselves."""  # noqa
        return Substitution(
            {
                var: term
                for (var, term) in zip(self.glob_vars, self.terms)
                if var != term
            }
        )


class AggrBaseLiteral(AuxLiteral):
    """TODO."""

    def __init__(self, aggr_id: int, glob_vars: TermTuple, terms: TermTuple) -> None:

        if len(glob_vars) != len(terms):
            raise ValueError(
                f"Number of global variables for {type(self)} does not match number of specified terms."  # noqa
            )

        super().__init__(
            f"{SpecialChar.EPS.value}{SpecialChar.ALPHA.value}{aggr_id}", *terms
        )
        self.aggr_id = aggr_id
        # store tuple to have a fixed reference order for variables
        self.glob_vars = glob_vars

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, AggrBaseLiteral)
            and self.aggr_id == other.aggr_id
            and self.glob_vars == other.glob_vars
            and self.terms == other.terms
        )

    def __hash__(self) -> int:
        return hash(("eps literal", self.aggr_id, self.glob_vars, self.terms))

    def set_naf(self, value: bool = True) -> None:
        raise Exception(
            f"Negation as failure cannot be set for literal of type {type(AggrBaseLiteral)}."
        )

    def set_neg(self, value: bool = True) -> None:
        raise Exception(
            f"Classical negation cannot be set for literal of type {type(AggrBaseLiteral)}."
        )

    def pos_occ(self) -> Set["AggrBaseLiteral"]:
        if self.naf:
            return set()

        return {AggrBaseLiteral(self.aggr_id, self.glob_vars, self.terms)}

    def neg_occ(self) -> Set["AggrBaseLiteral"]:
        if not self.naf:
            return set()

        # NOTE: naf flag gets dropped
        return {AggrBaseLiteral(self.aggr_id, self.glob_vars, self.terms)}

    def substitute(self, subst: "Substitution") -> "AggrBaseLiteral":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return AggrBaseLiteral(
            self.aggr_id,
            self.glob_vars,
            TermTuple(*tuple((term.substitute(subst) for term in self.terms))),
        )

    def replace_arith(self, var_table: "VariableTable") -> "AggrBaseLiteral":
        return AggrBaseLiteral(self.aggr_id, self.glob_vars, self.terms)

    def gather_var_assignment(self) -> Substitution:
        """Get substitution of global variables from rules. Remaining variables will simply be mapped onto themselves."""  # noqa
        return Substitution(
            {
                var: term
                for (var, term) in zip(self.glob_vars, self.terms)
                if var != term
            }
        )


class AggrElemLiteral(AuxLiteral):
    """TODO."""

    def __init__(
        self,
        aggr_id: int,
        element_id: int,
        local_vars: "TermTuple",
        glob_vars: "TermTuple",
        terms: "TermTuple",
    ) -> None:

        if len(glob_vars) + len(local_vars) != len(terms):
            raise ValueError(
                f"Number of global/local variables for {type(self)} does not match number of specified terms."  # noqa
            )

        super().__init__(
            f"{SpecialChar.ETA.value}{SpecialChar.ALPHA.value}{aggr_id}_{element_id}",
            *terms,
        )
        self.aggr_id = aggr_id
        self.element_id = element_id
        # store tuples to have a fixed reference order for variables
        self.local_vars = local_vars
        self.glob_vars = glob_vars

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, AggrElemLiteral)
            and self.aggr_id == other.aggr_id
            and self.element_id == other.element_id
            and self.local_vars == other.local_vars
            and self.glob_vars == other.glob_vars
            and self.terms == other.terms
        )

    def __hash__(self) -> int:
        return hash(
            (
                "eta literal",
                self.aggr_id,
                self.element_id,
                self.local_vars,
                self.glob_vars,
                self.terms,
            )
        )

    def set_naf(self, value: bool = True) -> None:
        raise Exception(
            f"Negation as failure cannot be set for literal of type {type(AggrElemLiteral)}."
        )

    def set_neg(self, value: bool = True) -> None:
        raise Exception(
            f"Classical negation cannot be set for literal of type {type(AggrElemLiteral)}."
        )

    def pos_occ(self) -> Set["AggrElemLiteral"]:
        if self.naf:
            return set()

        return {
            AggrElemLiteral(
                self.aggr_id,
                self.element_id,
                self.local_vars,
                self.glob_vars,
                self.terms,
            )
        }

    def neg_occ(self) -> Set["AggrElemLiteral"]:
        if not self.naf:
            return set()

        # NOTE: naf flag gets dropped
        return {
            AggrElemLiteral(
                self.aggr_id,
                self.element_id,
                self.local_vars,
                self.glob_vars,
                self.terms,
            )
        }

    def substitute(self, subst: "Substitution") -> "AggrElemLiteral":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return AggrElemLiteral(
            self.aggr_id,
            self.element_id,
            self.local_vars,
            self.glob_vars,
            TermTuple(*tuple(term.substitute(subst) for term in self.terms)),
        )

    def replace_arith(self, var_table: "VariableTable") -> "AggrElemLiteral":
        return AggrElemLiteral(
            self.aggr_id, self.element_id, self.local_vars, self.glob_vars, self.terms
        )

    def gather_var_assignment(self) -> Substitution:
        """Get substitution of global variables from rules. Remaining variables will simply be mapped onto themselves."""  # noqa
        return Substitution(
            {
                var: term
                for (var, term) in zip(self.local_vars + self.glob_vars, self.terms)
                if var != term
            }
        )


class ChoicePlaceholder(AuxLiteral):
    """TODO."""

    def __init__(self, choice_id: int, glob_vars: TermTuple, terms: TermTuple) -> None:

        if len(glob_vars) != len(terms):
            raise ValueError(
                f"Number of global variables for {type(self)} does not match number of specified terms."  # noqa
            )

        super().__init__(f"{SpecialChar.ALPHA.value}{choice_id}", *terms)
        self.choice_id = choice_id
        self.glob_vars = glob_vars

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, ChoicePlaceholder)
            and self.choice_id == other.choice_id
            and self.glob_vars == other.glob_vars
            and self.terms == other.terms
        )

    def __hash__(self) -> int:
        return hash(("gamma literal", self.choice_id, self.glob_vars, self.terms))

    def set_neg(self, value: bool = True) -> None:
        raise Exception(
            f"Classical negation cannot be set for literal of type {type(ChoicePlaceholder)}."  # noqa
        )

    def set_naf(self, value: bool = True) -> None:
        raise Exception(
            f"Negation-as-failure cannot be set for literal of type {type(ChoicePlaceholder)}."  # noqa
        )

    def pos_occ(self) -> Set["ChoicePlaceholder"]:
        # Gamma literals are always supposed to be positive
        return {ChoicePlaceholder(self.choice_id, self.glob_vars, self.terms)}

    def neg_occ(self) -> Set["ChoicePlaceholder"]:
        # Gamma literals are never supposed to be negative
        return set()

    def substitute(self, subst: "Substitution") -> "ChoicePlaceholder":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return ChoicePlaceholder(
            self.choice_id,
            self.glob_vars,
            TermTuple(*tuple(term.substitute(subst) for term in self.terms)),
            naf=self.naf,
        )

    def replace_arith(self, var_table: "VariableTable") -> "AggrPlaceholder":
        return ChoicePlaceholder(self.choice_id, self.glob_vars, self.terms)

    def gather_var_assignment(self) -> Substitution:
        """Get substitution of global variables from rules. Remaining variables will simply be mapped onto themselves."""  # noqa
        return Substitution(
            {
                var: term
                for (var, term) in zip(self.glob_vars, self.terms)
                if var != term
            }
        )


class ChoiceBaseLiteral(AuxLiteral):
    """TODO."""

    def __init__(self, aggr_id: int, glob_vars: TermTuple, terms: TermTuple) -> None:

        if len(glob_vars) != len(terms):
            raise ValueError(
                f"Number of global variables for {type(self)} does not match number of specified terms."  # noqa
            )

        super().__init__(
            f"{SpecialChar.EPS.value}{SpecialChar.ALPHA.value}{aggr_id}", *terms
        )
        self.aggr_id = aggr_id
        # store tuple to have a fixed reference order for variables
        self.glob_vars = glob_vars

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, AggrBaseLiteral)
            and self.aggr_id == other.aggr_id
            and self.glob_vars == other.glob_vars
            and self.terms == other.terms
        )

    def __hash__(self) -> int:
        return hash(("eps literal", self.aggr_id, self.glob_vars, self.terms))

    def set_naf(self, value: bool = True) -> None:
        raise Exception(
            f"Negation as failure cannot be set for literal of type {type(AggrBaseLiteral)}."
        )

    def set_neg(self, value: bool = True) -> None:
        raise Exception(
            f"Classical negation cannot be set for literal of type {type(AggrBaseLiteral)}."
        )

    def pos_occ(self) -> Set["AggrBaseLiteral"]:
        if self.naf:
            return set()

        return {AggrBaseLiteral(self.aggr_id, self.glob_vars, self.terms)}

    def neg_occ(self) -> Set["AggrBaseLiteral"]:
        if not self.naf:
            return set()

        # NOTE: naf flag gets dropped
        return {AggrBaseLiteral(self.aggr_id, self.glob_vars, self.terms)}

    def substitute(self, subst: "Substitution") -> "AggrBaseLiteral":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return AggrBaseLiteral(
            self.aggr_id,
            self.glob_vars,
            TermTuple(*tuple((term.substitute(subst) for term in self.terms))),
        )

    def replace_arith(self, var_table: "VariableTable") -> "AggrBaseLiteral":
        return AggrBaseLiteral(self.aggr_id, self.glob_vars, self.terms)

    def gather_var_assignment(self) -> Substitution:
        """Get substitution of global variables from rules. Remaining variables will simply be mapped onto themselves."""  # noqa
        return Substitution(
            {
                var: term
                for (var, term) in zip(self.glob_vars, self.terms)
                if var != term
            }
        )


class ChoiceElemLiteral(AuxLiteral):
    """TODO."""

    def __init__(
        self,
        aggr_id: int,
        element_id: int,
        local_vars: "TermTuple",
        glob_vars: "TermTuple",
        terms: "TermTuple",
    ) -> None:

        if len(glob_vars) + len(local_vars) != len(terms):
            raise ValueError(
                f"Number of global/local variables for {type(self)} does not match number of specified terms."  # noqa
            )

        super().__init__(
            f"{SpecialChar.ETA.value}{SpecialChar.ALPHA.value}{aggr_id}_{element_id}",
            *terms,
        )
        self.aggr_id = aggr_id
        self.element_id = element_id
        # store tuples to have a fixed reference order for variables
        self.local_vars = local_vars
        self.glob_vars = glob_vars

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, AggrElemLiteral)
            and self.aggr_id == other.aggr_id
            and self.element_id == other.element_id
            and self.local_vars == other.local_vars
            and self.glob_vars == other.glob_vars
            and self.terms == other.terms
        )

    def __hash__(self) -> int:
        return hash(
            (
                "eta literal",
                self.aggr_id,
                self.element_id,
                self.local_vars,
                self.glob_vars,
                self.terms,
            )
        )

    def set_naf(self, value: bool = True) -> None:
        raise Exception(
            f"Negation as failure cannot be set for literal of type {type(AggrElemLiteral)}."
        )

    def set_neg(self, value: bool = True) -> None:
        raise Exception(
            f"Classical negation cannot be set for literal of type {type(AggrElemLiteral)}."
        )

    def pos_occ(self) -> Set["AggrElemLiteral"]:
        if self.naf:
            return set()

        return {
            AggrElemLiteral(
                self.aggr_id,
                self.element_id,
                self.local_vars,
                self.glob_vars,
                self.terms,
            )
        }

    def neg_occ(self) -> Set["AggrElemLiteral"]:
        if not self.naf:
            return set()

        # NOTE: naf flag gets dropped
        return {
            AggrElemLiteral(
                self.aggr_id,
                self.element_id,
                self.local_vars,
                self.glob_vars,
                self.terms,
            )
        }

    def substitute(self, subst: "Substitution") -> "AggrElemLiteral":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return AggrElemLiteral(
            self.aggr_id,
            self.element_id,
            self.local_vars,
            self.glob_vars,
            TermTuple(*tuple(term.substitute(subst) for term in self.terms)),
        )

    def replace_arith(self, var_table: "VariableTable") -> "AggrElemLiteral":
        return AggrElemLiteral(
            self.aggr_id, self.element_id, self.local_vars, self.glob_vars, self.terms
        )

    def gather_var_assignment(self) -> Substitution:
        """Get substitution of global variables from rules. Remaining variables will simply be mapped onto themselves."""  # noqa
        return Substitution(
            {
                var: term
                for (var, term) in zip(self.local_vars + self.glob_vars, self.terms)
                if var != term
            }
        )
