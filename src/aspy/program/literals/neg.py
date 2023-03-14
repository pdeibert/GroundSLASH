from typing import Union

from .aggregate import AggregateLiteral
from .predicate import PredicateLiteral


def Neg(
    literal: Union[PredicateLiteral, AggregateLiteral], value: bool = True
) -> Union[PredicateLiteral, AggregateLiteral]:
    """Sets the `neg` (classical negation) attribute of a given aggregate or predicate literal.

    Args:
        literal: `PredicateLiteral` or `AggregateLiteral` instance.
        value: Boolean value to be set for the `neg` property of the literal.

    Returns:
        `PredicateLiteral` or `AggregateLiteral` instance.
        Instances are the same as the input instances, but with the `neg` attribute set.

    Raises:
        ValueError: Literal of wrong type (checked just in case).
    """  # noqa
    if not isinstance(literal, PredicateLiteral):
        raise ValueError("Classical negation only applicable to predicate literals.")

    literal.set_neg(value)

    return literal
