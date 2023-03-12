import re
from enum import Enum


class SpecialChar(Enum):
    ALPHA = "\u03b1"  # α
    EPS = "\u03b5"  # ε
    ETA = "\u03b7"  # η
    TAU = "\u03C4"  # τ
    CHI = "\u03C7"  # χ


VARIABLE_RE = re.compile(rf"^[A-Z{SpecialChar.TAU.value}][a-zA-Z0-1_]*")
SYM_CONST_RE = re.compile(
    (
        rf"[a-z{SpecialChar.ALPHA.value}{SpecialChar.CHI.value}"
        rf" | {SpecialChar.EPS.value + SpecialChar.ALPHA.value}"
        rf" | {SpecialChar.ETA.value + SpecialChar.ALPHA.value}"
        rf" | {SpecialChar.EPS.value + SpecialChar.CHI.value}"
        rf" | {SpecialChar.EPS.value + SpecialChar.CHI.value}"
        rf"][a-zA-Z0-1_]*"
    )
)
