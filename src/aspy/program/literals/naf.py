from typing import Union

from .aggregate import AggregateLiteral
from .predicate import PredicateLiteral


def Naf(
    literal: Union[PredicateLiteral, AggregateLiteral], value: bool = True
) -> Union[PredicateLiteral, AggregateLiteral]:
    """Sets the `naf` (negation-as-failure) attribute of a given aggregate or predicate literal.

    Args:
        literal: `PredicateLiteral` or `AggregateLiteral` instance.
        value: Boolean value to be set for the `naf` property of the literal.

    Returns:
        `PredicateLiteral` or `AggregateLiteral` instance.
        Instances are the same as the input instances, but with the `naf` attribute set.

    Raises:
        ValueError: Literal of wrong type (checked just in case).
    """  # noqa
    if not isinstance(literal, (PredicateLiteral, AggregateLiteral)):
        raise ValueError(
            "Negation as failure is only applicable to predicate and aggregate literals."  # noqa
        )

    literal.set_naf(value)

    return literal
