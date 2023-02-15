from typing import NamedTuple, Optional, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .terms import Variable


class SafetyRule(NamedTuple):
    depender: "Variable"
    dependees: set["Variable"]


class SafetyTriplet:
    def __init__(self, safe: Optional[Set["Variable"]]=None, unsafe: Optional[Set["Variable"]]=None, rules: Optional[Set[SafetyRule]]=None) -> None:
        self.safe   = safe if safe is not None else set()
        self.unsafe = unsafe if unsafe is not None else set()
        self.rules  = rules if rules is not None else set()

    def __eq__(self, other: "SafetyTriplet") -> bool:
        return self.safe == other.safe and self.unsafe == self.unsafe and self.rules == other.rules

    def copy(self) -> "SafetyTriplet":
        return SafetyTriplet(
            self.safe.copy(),
            self.unsafe.copy(),
            self.rules.copy()
        )

    def normalize(self) -> "SafetyTriplet":
        """Algorithm 1 in Bicheler (2015): "Optimizing Non-Ground Answer Set Programs via Rule Decomposition"."""

        # create copy of current safety characterization
        safety = self.copy()

        for rule in safety.rules:
            # remove rules whose depender depends on itself
            if rule.depender in rule.dependees:
                safety.rules.remove(rule)

        last_safety = None

        # until there is no more change
        while safety != last_safety:

            last_safety = safety.copy()

            for rule in self.rules:
                # if depender is safe
                if rule.depender in self.safe:
                    self.rules.remove(rule)
                # if depender is unsafe
                else:
                    # remove safe variables from dependees
                    rule.dependees = rule.dependees.setminus(self.safe)

                    # if set of dependees empty
                    if not rule.dependees:
                        # add depender to safe variables
                        self.safe.add(rule.depender)
                        # remove saftey rule
                        self.rules.remove(rule)

        for rule in self.rules:
            # mark rule variables as unsafe
            safety.unsafe.add(rule.depender)
            safety.unsafe.update(rule.dependees)

        # remove safe variables from set of unsafe ones
        safety.unsafe = safety.unsafe.setminus(safety.safe)

        return safety

    @classmethod
    def closure(cls, safeties: Iterable["SafetyTriplet"]) -> "SafetyTriplet":

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