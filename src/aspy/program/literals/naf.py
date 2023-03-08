from typing import Union

from .aggregate import AggregateLiteral
from .predicate import PredicateLiteral


def Naf(
    literal: Union[PredicateLiteral, AggregateLiteral], value: bool = True
) -> Union[PredicateLiteral, AggregateLiteral]:
    if not isinstance(literal, (PredicateLiteral, AggregateLiteral)):
        raise ValueError(
            "Negation as failure is only applicable to predicate and aggregate literals."  # noqa
        )

    literal.set_naf(value)

    return literal
