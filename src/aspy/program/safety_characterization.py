from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional, Set

if TYPE_CHECKING:  # pragma: no cover
    from .terms import Variable


@dataclass
class SafetyRule:
    """Safety rule for safety characterization.

    For details see Bicheler (2015): "Optimizing Non-Ground Answer Set Programs via Rule Decomposition".

    Attributes:
        depender: `Variable` instance representing the depender.
        dependees: Set of `Variable` instances representing the dependees.
    """  # noqa

    depender: "Variable"
    dependees: Set["Variable"]

    def __eq__(self, other: "Any") -> bool:
        """Compares the safety rule to a given object.

        Considered equal if the given object is also a `SafetyRule` instance with same
        depender and dependees.

        Args:
            other: `Any` instance to be compared to.

        Returns:
            Boolean indicating whether or not the safety rule is considered equal to the given object.
        """  # noqa
        return (
            isinstance(other, SafetyRule)
            and self.depender == other.depender
            and self.dependees == other.dependees
        )

    def __hash__(self) -> int:
        return hash(("safety rule", self.depender, frozenset(self.dependees)))


class SafetyTriplet:
    """Safety characterization.

    For details see Bicheler (2015): "Optimizing Non-Ground Answer Set Programs via Rule Decomposition".

    Attributes:
        safe: Set of `Variable` instances considered safe.
        unsafe: Set of `Variable` instances considered unsafe.
        rules: Set of `SafetyRule` instances.
    """  # noqa

    def __init__(
        self,
        safe: Optional[Set["Variable"]] = None,
        unsafe: Optional[Set["Variable"]] = None,
        rules: Optional[Set[SafetyRule]] = None,
    ) -> None:
        """Initializes the safety triplet instance.

        Args:
            safe: Set of `Variable` instances considered safe. Defaults to None.
            unsafe: Set of `Variable` instances considered unsafe. Defaults to None.
            rules: Optional set of `SafetyRule` instances. Defaults to None.
        """
        self.safe = safe if safe is not None else set()
        self.unsafe = unsafe if unsafe is not None else set()
        self.rules = rules if rules is not None else set()

    def __eq__(self, other: "Any") -> bool:
        """Compares the safety characterization to a given object.

        Considered equal if the given object is also a `SafetyTriplet` instance with same
        set of safe and unsafe variables as well as rules.

        Args:
            other: `Any` instance to be compared to.

        Returns:
            Boolean indicating whether or not the safety triplet is considered equal to the given object.
        """  # noqa
        return (
            isinstance(other, SafetyTriplet)
            and self.safe == other.safe
            and self.unsafe == self.unsafe
            and self.rules == other.rules
        )

    def normalize(self) -> "SafetyTriplet":
        """Normalizes the safety characterization.

        Implements Algorithm 1 in Bicheler (2015):
        "Optimizing Non-Ground Answer Set Programs via Rule Decomposition".

        Returns:
            Normalized `SafetyTriplet` instance.
        """  # noqa

        # create copy of current safety characterization
        safety = deepcopy(self)

        for rule in safety.rules.copy():
            # remove rules whose depender depends on itself
            if rule.depender in rule.dependees:
                safety.rules.remove(rule)

        last_safety = SafetyTriplet()

        # until there is no more change
        while safety != last_safety:

            last_safety = deepcopy(safety)
            # list of rules to remove
            remove = []

            for rule in safety.rules:
                # remove rules whose depender depends on itself
                if rule.depender in rule.dependees:
                    # mark rule for removal
                    remove.append(rule)

            for rule in remove:
                safety.rules.remove(rule)
            remove.clear()

            for rule in safety.rules:
                # if depender is safe
                if rule.depender in safety.safe:
                    # mark rule for removal
                    remove.append(rule)
                # if depender is unsafe
                else:
                    # remove safe variables from dependees
                    rule.dependees = rule.dependees - safety.safe

                    # if set of dependees empty
                    if not rule.dependees:
                        # add depender to safe variables
                        safety.safe.add(rule.depender)
                        # mark rule for removal
                        remove.append(rule)

            for rule in remove:
                safety.rules.remove(rule)
            remove.clear()

        for rule in safety.rules:
            # mark rule variables as unsafe
            safety.unsafe.add(rule.depender)
            safety.unsafe.update(rule.dependees)

        # remove safe variables from set of unsafe ones
        safety.unsafe = safety.unsafe - safety.safe

        return safety

    @classmethod
    def closure(cls, *safeties: "SafetyTriplet") -> "SafetyTriplet":
        """Computes the closure for specified safety characterizations.

        Args:
            *safeties: Sequence of `SafetyTriplet` instances.

        Returns:
            `SafetyTriplet` instance representing the closure of the specified
            safety characterizations.
        """
        safe = set()
        unsafe = set()
        rules = set()

        # combine all safeties
        for safety in safeties:
            safe = safe.union(safety.safe)
            unsafe = unsafe.union(safety.unsafe)
            rules = rules.union(safety.rules)

        # return normalized combined safety
        return SafetyTriplet(safe, unsafe, rules).normalize()
