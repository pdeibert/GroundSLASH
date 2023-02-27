from typing import Union

from .predicate import PredicateLiteral
from .aggregate import AggregateLiteral


def Naf(literal: Union[PredicateLiteral, AggregateLiteral], value: bool=True) -> Union[PredicateLiteral, AggregateLiteral]:
    if not isinstance(literal, (PredicateLiteral, AggregateLiteral)):
        raise ValueError("Negation as failure is only applicable to predicate and aggregate literals.")

    literal.set_naf(value)

    return literal