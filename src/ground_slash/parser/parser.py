from typing import TYPE_CHECKING, Self

from lark import Lark

if TYPE_CHECKING:
    from lark import Tree


class Parser:
    def __init__(self: Self, mode: str = "earley") -> None:
        # cast string to lower case
        mode = mode.lower()

        # check if mode is valid
        if mode not in ("earley", "lalr"):
            raise ValueError(f"Invalid value {mode} for 'mode'.")

        self.lark = Lark.open(
            f"SLASH_{mode}.lark",
            rel_to=__file__,
            parser=mode,
            start="program",
        )

    def parse(self: Self, prog_str: str) -> "Tree":
        return self.lark.parse(prog_str)
