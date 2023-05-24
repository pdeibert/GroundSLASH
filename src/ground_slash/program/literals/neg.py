from copy import deepcopy

from .literal import Literal


def Neg(literal: Literal, value: bool = True) -> Literal:
    """Sets the `neg` (classical negation) attribute of a given literal.

    Args:
        literal: `Literal` instance.
        value: Boolean value to be set for the `neg` property of the literal.

    Returns:
        `Literal` instance.
        Instances are the same as the input instances, but with the `neg` attribute set.

    Raises:
        ValueError: Literal of wrong type.
    """  # noqa
    naf_literal = deepcopy(literal)
    naf_literal.set_neg(value)

    return naf_literal
