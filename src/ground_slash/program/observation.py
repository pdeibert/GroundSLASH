from typing import Any

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

from .statements import Constraint


class Observation:
    """SLASH Observation.
    
    Attributes:
        constraints: Tuple of `Constraint` instances representing the observation.
    """

    def __init__(self: Self, *constraints: Constraint) -> None:
        """Initializes the observation instance.
        
        Args:
            *constraints: Sequence of `Constraint` instances.

        Raises:
            ValueError: No constraint specified.
        """
        if len(constraints) < 1:
            raise ValueError("Observation requires at least one constraint to be characterized.")

        self.constraints = constraints

    def __str__(self: Self) -> str:
        """Returns the string representation for the program.

        Returns:
            String representing the program.
            Contains the string representations of all constraints separated by spaces.
        """
        return " ".join([str(constr) for constr in self.constraints])

    def __eq__(self: Self, other: Any) -> bool:
        """Compares the observation to a given object.

        Args:
            other: `Any` instance to be compared to.

        Returns:
            Boolean indicating whether or not the observation is considered equal to the given object.
        """  # noqa
        return isinstance(other, type(self)) and set(self.constraints) == set(
            other.constraints
        )

    def __hash__(self: Self) -> int:
        return hash((type(self), frozenset(self.constraints)))
