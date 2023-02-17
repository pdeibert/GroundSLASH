from typing import Union

from .predicate import PredicateLiteral
from .aggregate import AggregateLiteral


def Neg(literal: Union[PredicateLiteral, AggregateLiteral], value: bool=True) -> Union[PredicateLiteral, AggregateLiteral]:
    if not isinstance(literal, PredicateLiteral):
        raise ValueError("Classical negation only applicable to predicate literals.")

    literal.neg = value

    return literal