from abc import ABC
from copy import deepcopy
from typing import TYPE_CHECKING, Set

from aspy.program.literals import PredicateLiteral
from aspy.program.substitution import Substitution
from aspy.program.symbol_table import SpecialChar
from aspy.program.terms import TermTuple

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.expression import Expr
    from aspy.program.variable_table import VariableTable


class AuxLiteral(PredicateLiteral, ABC):
    """TODO."""

    def __init__(self, name: str, *args, **kwargs) -> None:
        super().__init__("f", *args, **kwargs)
        self.name = name  # TODO: better way to avoid regex check in 'PredicateLiteral'?


class AlphaLiteral(AuxLiteral):
    """TODO."""

    def __init__(
        self, aggr_id: int, glob_vars: TermTuple, terms: TermTuple, naf: bool = False
    ) -> None:

        if len(glob_vars) != len(terms):
            raise ValueError(
                f"Number of global variables for {type(self)} does not match number of specified terms."
            )

        super().__init__(f"{SpecialChar.ALPHA.value}{aggr_id}", *terms, naf=naf)
        self.aggr_id = aggr_id
        self.glob_vars = glob_vars

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, AlphaLiteral)
            and self.aggr_id == other.aggr_id
            and self.glob_vars == other.glob_vars
            and self.terms == other.terms
        )

    def __hash__(self) -> int:
        return hash(("alpha literal", self.aggr_id, self.glob_vars, self.terms))

    def set_neg(self, value: bool = True) -> None:
        raise Exception(
            f"Classical negation cannot be set for literal of type {type(AlphaLiteral)}."
        )

    def pos_occ(self) -> Set["AlphaLiteral"]:
        if self.naf:
            return set()

        return {AlphaLiteral(self.aggr_id, self.glob_vars, self.terms)}

    def neg_occ(self) -> Set["AlphaLiteral"]:
        if not self.naf:
            return set()

        # NOTE: naf flag gets dropped
        return {AlphaLiteral(self.aggr_id, self.glob_vars, self.terms)}

    def substitute(self, subst: "Substitution") -> "AlphaLiteral":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return AlphaLiteral(
            self.aggr_id,
            self.glob_vars,
            TermTuple(*tuple(term.substitute(subst) for term in self.terms)),
            naf=self.naf,
        )

    def replace_arith(self, var_table: "VariableTable") -> "AlphaLiteral":
        return AlphaLiteral(self.aggr_id, self.glob_vars, self.terms, naf=self.naf)

    def gather_var_assignment(self) -> Substitution:
        """Get substitution of global variables from rules. Remaining variables will simply be mapped onto themselves."""
        return Substitution(
            {
                var: term
                for (var, term) in zip(self.glob_vars, self.terms)
                if var != term
            }
        )


class EpsLiteral(AuxLiteral):
    """TODO."""

    def __init__(self, aggr_id: int, glob_vars: TermTuple, terms: TermTuple) -> None:

        if len(glob_vars) != len(terms):
            raise ValueError(
                f"Number of global variables for {type(self)} does not match number of specified terms."
            )

        super().__init__(f"{SpecialChar.EPS.value}{aggr_id}", *terms)
        self.aggr_id = aggr_id
        # store tuple to have a fixed reference order for variables
        self.glob_vars = glob_vars

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, EpsLiteral)
            and self.aggr_id == other.aggr_id
            and self.glob_vars == other.glob_vars
            and self.terms == other.terms
        )

    def __hash__(self) -> int:
        return hash(("eps literal", self.aggr_id, self.glob_vars, self.terms))

    def set_naf(self, value: bool = True) -> None:
        raise Exception(
            f"Negation as failure cannot be set for literal of type {type(EpsLiteral)}."
        )

    def set_neg(self, value: bool = True) -> None:
        raise Exception(
            f"Classical negation cannot be set for literal of type {type(EpsLiteral)}."
        )

    def pos_occ(self) -> Set["EpsLiteral"]:
        if self.naf:
            return set()

        return {EpsLiteral(self.aggr_id, self.glob_vars, self.terms)}

    def neg_occ(self) -> Set["EpsLiteral"]:
        if not self.naf:
            return set()

        # NOTE: naf flag gets dropped
        return {EpsLiteral(self.aggr_id, self.glob_vars, self.terms)}

    def substitute(self, subst: "Substitution") -> "EpsLiteral":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return EpsLiteral(
            self.aggr_id,
            self.glob_vars,
            TermTuple(*tuple((term.substitute(subst) for term in self.terms))),
        )

    def replace_arith(self, var_table: "VariableTable") -> "EpsLiteral":
        return EpsLiteral(self.aggr_id, self.glob_vars, self.terms)

    def gather_var_assignment(self) -> Substitution:
        """Get substitution of global variables from rules. Remaining variables will simply be mapped onto themselves."""
        return Substitution(
            {
                var: term
                for (var, term) in zip(self.glob_vars, self.terms)
                if var != term
            }
        )


class EtaLiteral(AuxLiteral):
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
                f"Number of global/local variables for {type(self)} does not match number of specified terms."
            )

        super().__init__(f"{SpecialChar.ETA.value}{aggr_id}_{element_id}", *terms)
        self.aggr_id = aggr_id
        self.element_id = element_id
        # store tuples to have a fixed reference order for variables
        self.local_vars = local_vars
        self.glob_vars = glob_vars

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, EtaLiteral)
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
            f"Negation as failure cannot be set for literal of type {type(EtaLiteral)}."
        )

    def set_neg(self, value: bool = True) -> None:
        raise Exception(
            f"Classical negation cannot be set for literal of type {type(EtaLiteral)}."
        )

    def pos_occ(self) -> Set["EtaLiteral"]:
        if self.naf:
            return set()

        return {
            EtaLiteral(
                self.aggr_id,
                self.element_id,
                self.local_vars,
                self.glob_vars,
                self.terms,
            )
        }

    def neg_occ(self) -> Set["EtaLiteral"]:
        if not self.naf:
            return set()

        # NOTE: naf flag gets dropped
        return {
            EtaLiteral(
                self.aggr_id,
                self.element_id,
                self.local_vars,
                self.glob_vars,
                self.terms,
            )
        }

    def substitute(self, subst: "Substitution") -> "EtaLiteral":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return EtaLiteral(
            self.aggr_id,
            self.element_id,
            self.local_vars,
            self.glob_vars,
            TermTuple(*tuple(term.substitute(subst) for term in self.terms)),
        )

    def replace_arith(self, var_table: "VariableTable") -> "EtaLiteral":
        return EtaLiteral(
            self.aggr_id, self.element_id, self.local_vars, self.glob_vars, self.terms
        )

    def gather_var_assignment(self) -> Substitution:
        """Get substitution of global variables from rules. Remaining variables will simply be mapped onto themselves."""
        return Substitution(
            {
                var: term
                for (var, term) in zip(self.local_vars + self.glob_vars, self.terms)
                if var != term
            }
        )
