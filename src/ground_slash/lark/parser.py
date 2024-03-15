from typing import TYPE_CHECKING

from lark import Lark

if TYPE_CHECKING:
    from lark import Tree


class SLASHParser:
    def __init__(self) -> None:
        self.lark = Lark.open(
            "SLASH.lark",
            rel_to=__file__,
            parser="earley",
            start="program",
        )

    def parse(self, prog_str: str) -> "Tree":
        return self.lark.parse(prog_str)