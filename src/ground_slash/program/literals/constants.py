from typing import Any, Dict, Set

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

from ground_slash.program.expression import Expr
from ground_slash.program.terms import Term

from .literal import Literal, LiteralCollection

# TODO: must also include changes to grounder (or at least throw error))


class TrueConstant(Literal):
    def __eq__(self: Self, other: Any) -> bool:
        return isinstance(other, type(self))

    def __hash__(self: Self) -> int:
        return hash((type(self),))

    def __str__(self: Self) -> str:
        return "#true"

    def match(self: Self, *args, **kwargs) -> None:  # TODO: signature!!!
        raise NotImplementedError("Matching not defined for special '#true' constant.")

    def pos_occ(self: Self, *args, **kwargs) -> LiteralCollection:  # TODO: signature!!!
        return LiteralCollection(self)

    def neg_occ(self: Self, *args, **kwargs) -> LiteralCollection:  # TODO: signature!!!
        return LiteralCollection()

    def safety(self: Self, *args, **kwargs) -> None:  # TODO: signature!!!
        raise NotImplementedError(
            "Safety characterization not defined for special '#true' constant."
        )

    def vars(self: Self, *args, **kwargs) -> Set:  # TODO: signature!!!
        return set()

    def substitute(self: Self, subst: Dict[str, Term]) -> Expr:
        return self  # TODO: correct?


class FalseConstant(Literal):
    def __eq__(self: Self, other: Any) -> bool:
        return isinstance(other, type(self))

    def __hash__(self: Self) -> int:
        return hash((type(self),))

    def __str__(self: Self) -> str:
        return "#false"

    def match(self: Self, *args, **kwargs) -> None:  # TODO: signature!!!
        raise NotImplementedError("Matching not defined for special '#false' constant.")

    def pos_occ(self: Self, *args, **kwargs) -> LiteralCollection:  # TODO: signature!!!
        return LiteralCollection(self)

    def neg_occ(self: Self, *args, **kwargs) -> LiteralCollection:  # TODO: signature!!!
        return LiteralCollection()

    def safety(self: Self, *args, **kwargs) -> None:  # TODO: signature!!!
        raise NotImplementedError(
            "Safety characterization not defined for special '#false' constant."
        )

    def vars(self: Self, *args, **kwargs) -> Set:  # TODO: signature!!!
        return set()

    def substitute(self: Self, subst: Dict[str, Term]) -> Expr:
        return self  # TODO: correct?
