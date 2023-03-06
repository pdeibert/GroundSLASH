import re
from enum import Enum


class SpecialChar(Enum):
    ALPHA = "\u03b1"  # α
    EPS = "\u03b5"  # ε
    ETA = "\u03b7"  # η
    TAU = "\u03C4"  # τ


VARIABLE_RE = re.compile(fr"^[A-Z{SpecialChar.TAU.value}][a-zA-Z0-1_]*")
SYM_CONST_RE = re.compile(
    fr"^[a-z{SpecialChar.ALPHA.value}{SpecialChar.EPS.value}{SpecialChar.ETA.value}][a-zA-Z0-1_]*"
)


class SymbolTable:
    def __init__(self) -> None:
        self.symbols = set()
        self.alpha_counter = 0
        self.epsilon_counter = 0
        self.eta_counter = 0

    def __contains__(self, symbol: str, arity: int = -1) -> bool:

        # ignore arity and only check if predicate symbol present
        if arity == -1:
            for (s, a) in self.symbols:
                if symbol == s:
                    return True
        else:
            for (s, a) in self.symbols:
                if symbol == s and arity == a:
                    return True

        return False

    def __str__(self) -> str:
        return str(self.symbols)

    def register(self, symbol: str, arity: int) -> str:

        # α
        if symbol == SpecialChar.ALPHA:
            # get current id for alpha symbols
            id = self.alpha_counter
            # increase counter
            self.alpha_counter += 1

            # set correct symbol
            symbol = f"{symbol}_{id}"

            # register new symbol
            self.symbols.add((symbol, arity))
        # ε
        elif symbol == SpecialChar.EPS:
            # get current id for epsilon symbols
            id = self.epsilon_counter
            # increase counter
            self.epsilon_counter += 1

            # set correct symbol
            symbol = f"{symbol}_{id}"

            # register new symbol
            self.symbols.add((symbol, arity))
        # η
        elif symbol == SpecialChar.ETA:
            # get current id for eta symbols
            id = self.eta_counter
            # increase counter
            self.eta_counter += 1

            # set correct symbol
            symbol = f"{symbol}_{id}"

            # register new symbol
            self.symbols.add((symbol, arity))
        # regular symbol
        else:
            # register new symbol
            self.symbols.add((symbol, arity))

        # return symbol string
        return symbol
