from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Set

if TYPE_CHECKING:  # pragma: no cover
    from .terms import Variable


@dataclass
class SafetyRule:
    depender: "Variable"
    dependees: Set["Variable"]

    def __eq__(self, other: "SafetyRule") -> bool:
        return self.depender == other.depender and self.dependees == other.dependees

    def __hash__(self) -> int:
        return hash((self.depender, frozenset(self.dependees)))


class SafetyTriplet:
    def __init__(
        self,
        safe: Optional[Set["Variable"]] = None,
        unsafe: Optional[Set["Variable"]] = None,
        rules: Optional[Set[SafetyRule]] = None,
    ) -> None:
        self.safe = safe if safe is not None else set()
        self.unsafe = unsafe if unsafe is not None else set()
        self.rules = rules if rules is not None else set()

    def __eq__(self, other: "SafetyTriplet") -> bool:
        return (
            self.safe == other.safe
            and self.unsafe == self.unsafe
            and self.rules == other.rules
        )

    def normalize(self) -> "SafetyTriplet":
        """Algorithm 1 in Bicheler (2015): "Optimizing Non-Ground Answer Set Programs via Rule Decomposition"."""  # noqa

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
