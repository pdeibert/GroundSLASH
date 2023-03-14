from typing import Union

from .aggregate import AggrLiteral
from .predicate import PredLiteral


def Naf(
    literal: Union[PredLiteral, AggrLiteral], value: bool = True
) -> Union[PredLiteral, AggrLiteral]:
    """Sets the `naf` (negation-as-failure) attribute of a given aggregate or predicate literal.

    Args:
        literal: `PredLiteral` or `AggrLiteral` instance.
        value: Boolean value to be set for the `naf` property of the literal.

    Returns:
        `PredLiteral` or `AggrLiteral` instance.
        Instances are the same as the input instances, but with the `naf` attribute set.

    Raises:
        ValueError: Literal of wrong type (checked just in case).
    """  # noqa
    if not isinstance(literal, (PredLiteral, AggrLiteral)):
        raise ValueError(
            "Negation as failure is only applicable to predicate and aggregate literals."  # noqa
        )

    literal.set_naf(value)

    return literal
