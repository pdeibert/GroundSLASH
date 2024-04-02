from typing import TYPE_CHECKING, Optional, Self, Tuple

from lark import Lark  # type: ignore

from .earley_transformer import EarleyTransformer
from .lalr_transformer import LALRTransformer
from .standalone_parser import Lark_StandAlone as StandaloneParser
from .standalone_transformer import StandaloneTransformer

if TYPE_CHECKING:
    from ground_slash.program.literals import PredLiteral
    from ground_slash.program.statements import Statement


class Parser:
    def __init__(self: Self, mode: str = "standalone") -> None:
        # cast string to lower case
        self.mode = mode.lower()

        # check if mode is valid
        if self.mode not in ("earley", "lalr", "standalone"):
            raise ValueError(f"Invalid value {self.mode} for 'mode'.")

        if mode == "earley":
            self.transformer = EarleyTransformer()
            self.parser = Lark.open(
                "SLASH_earley.lark",
                rel_to=__file__,
                parser="earley",
                start="program",
            )
        elif mode == "lalr":
            self.transformer = LALRTransformer()
            self.parser = Lark.open(
                "SLASH_lalr.lark",
                rel_to=__file__,
                parser="lalr",
                start="program",
                transformer=self.transformer,
            )
        else:
            self.transformer = StandaloneTransformer()
            self.parser = StandaloneParser(transformer=self.transformer)

    def parse(
        self: Self, prog_str: str
    ) -> Tuple[Tuple["Statement", ...], Optional["PredLiteral"]]:
        # TODO: typing
        if self.mode == "earley":
            return self.transformer.transform(self.parser.parse(prog_str))
        else:
            return self.parser.parse(prog_str)
