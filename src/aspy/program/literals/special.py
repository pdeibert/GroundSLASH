from abc import ABC
from copy import deepcopy
from typing import TYPE_CHECKING, Set

from aspy.program.literals import PredLiteral
from aspy.program.substitution import Substitution
from aspy.program.symbols import SpecialChar
from aspy.program.terms import TermTuple

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.expression import Expr
    from aspy.program.variable_table import VariableTable


class AuxLiteral(PredLiteral, ABC):
    """Abstract base class for auxiliary predicate literals."""

    def __init__(self, name: str, *args, **kwargs) -> None:
        """Initializes the auxiliary literal instance.

        Args:
            name: String representing the predicate identifier.
                Does not need to standard identifier limitations, but should
                make sense when printed.
        """
        super().__init__("f", *args, **kwargs)
        self.name = name  # TODO: better way to avoid regex check in 'PredLiteral'?


class PropPlaceholder(AuxLiteral):
    """TODO"""

    def __init__(
        self,
        prefix: str,
        ref_id: int,
        glob_vars: TermTuple,
        terms: TermTuple,
        naf: bool = False,
    ) -> None:

        if len(glob_vars) != len(terms):
            raise ValueError(
                f"Number of global variables for {type(self)} does not match number of specified terms."  # noqa
            )

        super().__init__(f"{prefix}{ref_id}", *terms, naf=naf)
        self.prefix = prefix
        self.ref_id = ref_id
        self.glob_vars = glob_vars

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, type(self))
            and self.prefix == other.prefix
            and self.ref_id == other.ref_id
            and set(self.glob_vars) == set(other.glob_vars)
            and {v: t for v, t in zip(self.glob_vars, self.terms)}
            == {v: t for v, t in zip(other.glob_vars, other.terms)}
        )

    def __hash__(self) -> int:
        return hash(
            (
                "prop placeholder",
                self.prefix,
                self.ref_id,
                frozenset((v, t) for v, t in zip(self.glob_vars, self.terms)),
            )
        )

    def set_neg(self, value: bool = True) -> None:
        raise Exception(
            f"Classical negation cannot be set for literal of type {type(self)}."  # noqa
        )

    def pos_occ(self) -> Set["PropPlaceholder"]:
        if self.naf:
            return set()

        return {
            type(self)(
                prefix=self.prefix,
                ref_id=self.ref_id,
                glob_vars=self.glob_vars,
                terms=self.terms,
            )
        }

    def neg_occ(self) -> Set["PropPlaceholder"]:
        if not self.naf:
            return set()

        # NOTE: naf flag gets dropped
        return {
            type(self)(
                prefix=self.prefix,
                ref_id=self.ref_id,
                glob_vars=self.glob_vars,
                terms=self.terms,
            )
        }

    def substitute(self, subst: "Substitution") -> "PropPlaceholder":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return type(self)(
            prefix=self.prefix,
            ref_id=self.ref_id,
            glob_vars=self.glob_vars,
            terms=TermTuple(*tuple(term.substitute(subst) for term in self.terms)),
            naf=self.naf,
        )

    def replace_arith(self, var_table: "VariableTable") -> "PropPlaceholder":
        return type(self)(
            prefix=self.prefix,
            ref_id=self.ref_id,
            glob_vars=self.glob_vars,
            terms=self.terms,
            naf=self.naf,
        )

    def gather_var_assignment(self) -> Substitution:
        """Get substitution of global variables from rules. Remaining variables will simply be mapped onto themselves."""  # noqa
        return Substitution(
            {
                var: term
                for (var, term) in zip(self.glob_vars, self.terms)
                if var != term
            }
        )


class PropBaseLiteral(AuxLiteral):
    """TODO."""

    def __init__(
        self, prefix: str, ref_id: int, glob_vars: TermTuple, terms: TermTuple
    ) -> None:

        if len(glob_vars) != len(terms):
            raise ValueError(
                f"Number of global variables for {type(self)} does not match number of specified terms."  # noqa
            )

        super().__init__(f"{SpecialChar.EPS.value}{prefix}{ref_id}", *terms)
        self.prefix = prefix
        self.ref_id = ref_id
        # store tuple to have a fixed reference order for variables
        self.glob_vars = glob_vars

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, type(self))
            and self.prefix == other.prefix
            and self.ref_id == other.ref_id
            and set(self.glob_vars) == set(other.glob_vars)
            and {v: t for v, t in zip(self.glob_vars, self.terms)}
            == {v: t for v, t in zip(other.glob_vars, other.terms)}
        )

    def __hash__(self) -> int:
        return hash(
            (
                "prop base literal",
                self.prefix,
                self.ref_id,
                frozenset((v, t) for v, t in zip(self.glob_vars, self.terms)),
            )
        )

    def set_naf(self, value: bool = True) -> None:
        raise Exception(
            f"Negation as failure cannot be set for literal of type {type(self)}."  # noqa
        )

    def set_neg(self, value: bool = True) -> None:
        raise Exception(
            f"Classical negation cannot be set for literal of type {type(self)}."  # noqa
        )

    def pos_occ(self) -> Set["PropBaseLiteral"]:
        if self.naf:
            return set()

        return {
            type(self)(
                prefix=self.prefix,
                ref_id=self.ref_id,
                glob_vars=self.glob_vars,
                terms=self.terms,
            )
        }

    def neg_occ(self) -> Set["PropBaseLiteral"]:
        if not self.naf:
            return set()

        # NOTE: naf flag gets dropped
        return {
            type(self)(
                prefix=self.prefix,
                ref_id=self.ref_id,
                glob_vars=self.glob_vars,
                terms=self.terms,
            )
        }

    def substitute(self, subst: "Substitution") -> "PropBaseLiteral":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return type(self)(
            prefix=self.prefix,
            ref_id=self.ref_id,
            glob_vars=self.glob_vars,
            terms=TermTuple(*tuple((term.substitute(subst) for term in self.terms))),
        )

    def replace_arith(self, var_table: "VariableTable") -> "PropBaseLiteral":
        return type(self)(
            prefix=self.prefix,
            ref_id=self.ref_id,
            glob_vars=self.glob_vars,
            terms=self.terms,
        )

    def gather_var_assignment(self) -> Substitution:
        """Get substitution of global variables from rules. Remaining variables will simply be mapped onto themselves."""  # noqa
        return Substitution(
            {
                var: term
                for (var, term) in zip(self.glob_vars, self.terms)
                if var != term
            }
        )


class PropElemLiteral(AuxLiteral):
    """TODO."""

    def __init__(
        self,
        prefix: str,
        ref_id: int,
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
            f"{SpecialChar.ETA.value}{prefix}{ref_id}_{element_id}",
            *terms,
        )
        self.prefix = prefix
        self.ref_id = ref_id
        self.element_id = element_id
        # store tuples to have a fixed reference order for variables
        self.local_vars = local_vars
        self.glob_vars = glob_vars

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, type(self))
            and self.prefix == other.prefix
            and self.ref_id == other.ref_id
            and self.element_id == other.element_id
            and set(self.glob_vars) == set(other.glob_vars)
            and set(self.local_vars) == set(other.local_vars)
            and {v: t for v, t in zip(self.local_vars + self.glob_vars, self.terms)}
            == {v: t for v, t in zip(other.local_vars + other.glob_vars, other.terms)}
        )

    def __hash__(self) -> int:
        return hash(
            (
                "prop element literal",
                self.prefix,
                self.ref_id,
                self.element_id,
                frozenset(
                    (v, t)
                    for v, t in zip(self.local_vars, self.terms[: len(self.local_vars)])
                ),
                frozenset(
                    (v, t)
                    for v, t in zip(self.glob_vars, self.terms[len(self.local_vars) :])
                ),
            )
        )

    def set_naf(self, value: bool = True) -> None:
        raise Exception(
            f"Negation as failure cannot be set for literal of type {type(self)}."  # noqa
        )

    def set_neg(self, value: bool = True) -> None:
        raise Exception(
            f"Classical negation cannot be set for literal of type {type(self)}."  # noqa
        )

    def pos_occ(self) -> Set["PropElemLiteral"]:
        if self.naf:
            return set()

        return {
            type(self)(
                prefix=self.prefix,
                ref_id=self.ref_id,
                element_id=self.element_id,
                local_vars=self.local_vars,
                glob_vars=self.glob_vars,
                terms=self.terms,
            )
        }

    def neg_occ(self) -> Set["PropElemLiteral"]:
        if not self.naf:
            return set()

        # NOTE: naf flag gets dropped
        return {
            type(self)(
                prefix=self.prefix,
                ref_id=self.ref_id,
                element_id=self.element_id,
                local_vars=self.local_vars,
                glob_vars=self.glob_vars,
                terms=self.terms,
            )
        }

    def substitute(self, subst: "Substitution") -> "PropElemLiteral":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        return type(self)(
            prefix=self.prefix,
            ref_id=self.ref_id,
            element_id=self.element_id,
            local_vars=self.local_vars,
            glob_vars=self.glob_vars,
            terms=TermTuple(*tuple(term.substitute(subst) for term in self.terms)),
        )

    def replace_arith(self, var_table: "VariableTable") -> "PropElemLiteral":
        return type(self)(
            prefix=self.prefix,
            ref_id=self.ref_id,
            element_id=self.element_id,
            local_vars=self.local_vars,
            glob_vars=self.glob_vars,
            terms=self.terms,
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


class AggrPlaceholder(PropPlaceholder):
    """TODO."""

    def __init__(
        self,
        ref_id: int,
        glob_vars: TermTuple,
        terms: TermTuple,
        naf: bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(SpecialChar.ALPHA.value, ref_id, glob_vars, terms, naf=naf)


class AggrBaseLiteral(PropBaseLiteral):
    """TODO."""

    def __init__(
        self, ref_id: int, glob_vars: TermTuple, terms: TermTuple, *args, **kwargs
    ) -> None:
        super().__init__(SpecialChar.ALPHA.value, ref_id, glob_vars, terms)


class AggrElemLiteral(PropElemLiteral):
    """TODO."""

    def __init__(
        self,
        ref_id: int,
        element_id: int,
        local_vars: "TermTuple",
        glob_vars: "TermTuple",
        terms: "TermTuple",
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            SpecialChar.ALPHA.value, ref_id, element_id, local_vars, glob_vars, terms
        )


class ChoicePlaceholder(PropPlaceholder):
    """TODO."""

    def __init__(
        self,
        ref_id: int,
        glob_vars: TermTuple,
        terms: TermTuple,
        naf: bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(SpecialChar.CHI.value, ref_id, glob_vars, terms, naf=naf)

    def set_naf(self, value: bool = True) -> None:
        raise Exception(
            f"Negation-as-failure cannot be set for literal of type {ChoicePlaceholder}."  # noqa
        )


class ChoiceBaseLiteral(PropBaseLiteral):
    """TODO."""

    def __init__(
        self, ref_id: int, glob_vars: TermTuple, terms: TermTuple, *args, **kwargs
    ) -> None:
        super().__init__(SpecialChar.CHI.value, ref_id, glob_vars, terms)


class ChoiceElemLiteral(PropElemLiteral):
    """TODO."""

    def __init__(
        self,
        ref_id: int,
        element_id: int,
        local_vars: "TermTuple",
        glob_vars: "TermTuple",
        terms: "TermTuple",
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            SpecialChar.CHI.value, ref_id, element_id, local_vars, glob_vars, terms
        )
