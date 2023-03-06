from typing import Union

from .aggregate import AggregateLiteral
from .predicate import PredicateLiteral


def Neg(
    literal: Union[PredicateLiteral, AggregateLiteral], value: bool = True
) -> Union[PredicateLiteral, AggregateLiteral]:
    if not isinstance(literal, PredicateLiteral):
        raise ValueError("Classical negation only applicable to predicate literals.")

    literal.set_neg(value)

    return literal
