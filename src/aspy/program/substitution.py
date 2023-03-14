from copy import deepcopy
from functools import reduce
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.terms import Term, Variable


class AssignmentError(Exception):
    def __init__(self, subst_1: "Substitution", subst_2: "Substitution") -> None:
        super().__init__(
            f"Substitution {subst_1} is inconsistent with substitution {subst_2}."
        )


class Substitution(dict):
    """Maps variables to terms replacing those variables"""

    def __init__(self, subst_dict: Optional[Dict["Variable", "Term"]] = None) -> None:
        if subst_dict is not None:
            self.update(subst_dict)

    def __getitem__(self, var: "Variable") -> "Term":
        # map variables to themselves if no substitution specified
        return deepcopy(dict.__getitem__(self, var)) if var in self else deepcopy(var)

    def __str__(self) -> str:
        assignments_str = ",".join(
            [f"{str(var)}:{str(target)}" for var, target in self.items()]
        )

        return f"{{{assignments_str}}}"

    def __eq__(self, other: "Substitution") -> bool:
        return isinstance(other, Substitution) and super(Substitution, self).__eq__(
            other
        )

    def __hash__(self) -> int:
        return hash(("substitution", frozenset(self.items())))

    def __add__(self, other: "Substitution") -> "Substitution":
        subst = dict(self.items())

        for var, target in other.items():
            if var in subst:
                if not target == subst[var]:
                    raise AssignmentError(self, other)
            else:
                subst[var] = target

        return Substitution(subst)

    def compose(self, other: "Substitution") -> "Substitution":

        # apply other substitution to substituted values
        subst = {var: target.substitute(other) for (var, target) in self.items()}
        # add substitution of variables that are not in the original substitution
        # (i.e., originally mapped onto themselves)
        subst.update(
            {var: target for (var, target) in other.items() if var not in subst}
        )

        return Substitution(subst)

    @classmethod
    def composition(cls, *substitutions: "Substitution") -> "Substitution":
        return reduce(lambda s1, s2: s1.compose(s2), substitutions)

    def is_identity(self) -> bool:
        return all(var == target for (var, target) in self.items())
