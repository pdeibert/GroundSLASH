from typing import Set, Tuple, TYPE_CHECKING
from dataclasses import dataclass

from .variable_set import VariableSet

if TYPE_CHECKING:
    from .terms import Variable


@dataclass
class SafetyRule:
    depender: "Variable"
    dependees: VariableSet


@dataclass
class Safety:
    safe: VariableSet
    unsafe: VariableSet
    rules: Set[SafetyRule]

    def copy(self) -> "Safety":
        return Safety(
            self.safe.copy(),
            self.unsafe.copy(),
            self.rules.copy()
        )

    def normalize(self) -> "Safety":
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
    def closure(cls, safeties: Tuple["Safety"]) -> "Safety":

        safe = VariableSet()
        unsafe = VariableSet()
        rules = set()

        # combine all safeties
        for safety in safeties:
            safe = safe.union(safety.safe)
            unsafe = unsafe.union(safety.unsafe)
            rules = rules.union(safety.rules)
        
        # return normalized combined safety
        return Safety(safe, unsafe, rules).normalize()