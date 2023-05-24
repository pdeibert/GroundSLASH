from copy import deepcopy

from .literal import Literal


def Naf(literal: Literal, value: bool = True) -> Literal:
    """Sets the `naf` (negation-as-failure) attribute of a given literal.

    Args:
        literal: `Literal` instance.
        value: Boolean value to be set for the `naf` property of the literal.

    Returns:
        `Literal` instance.
        Instances are the same as the input instances, but with the `naf` attribute set.

    Raises:
        ValueError: Literal of wrong type.
    """  # noqa
    naf_literal = deepcopy(literal)
    naf_literal.set_naf(value)

    return naf_literal
