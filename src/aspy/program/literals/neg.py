from copy import deepcopy
from typing import Union

from .aggregate import AggrLiteral
from .predicate import PredLiteral


def Neg(
    literal: Union[PredLiteral, AggrLiteral], value: bool = True
) -> Union[PredLiteral, AggrLiteral]:
    """Sets the `neg` (classical negation) attribute of a given aggregate or predicate literal.

    Args:
        literal: `PredLiteral` or `AggrLiteral` instance.
        value: Boolean value to be set for the `neg` property of the literal.

    Returns:
        `PredLiteral` or `AggrLiteral` instance.
        Instances are the same as the input instances, but with the `neg` attribute set.

    Raises:
        ValueError: Literal of wrong type (checked just in case).
    """  # noqa
    if not isinstance(literal, PredLiteral):
        raise ValueError("Classical negation only applicable to predicate literals.")

    naf_literal = deepcopy(literal)
    naf_literal.set_neg(value)

    return naf_literal

    return literal
