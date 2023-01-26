from abc import ABC

from .expression import Expr


class Literal(Expr, ABC): # TODO: inherit Expr ?
    """Abstract base class for all literals."""
    pass


class NafLiteral(Literal, ABC):
    """Negation-as-failure (Naf) literal.
    
    Can be either a built-in atom, a classical atom or the (default) negation of a classical atom.

    A Naf-literal is positive, if it is a built-in atom or a classical atom, else negative.
    """
    pass