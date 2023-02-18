from typing import Optional, Dict, TYPE_CHECKING
from copy import deepcopy

from .expression import Expr

if TYPE_CHECKING:
    from aspy.program.terms import Variable, Term


class AssignmentError(Exception):
    def __init__(self, subst_1: "Substitution", subst_2: "Substitution") -> None:
        super().__init__(f"Substitution {subst_1} is inconsistent with substitution {subst_2}.")


#class MatchError(Exception):
#    def __init__(self, candidate: "Expr", target: "Expr") -> None:
#        super().__init__(f"{candidate} cannot be matched to {target}.")


class Substitution(dict):
    """Maps variables to terms replacing those variables"""
    def __init__(self, subst_dict: Optional[Dict["Variable", "Term"]]=None) -> None:
        if subst_dict is not None:
            self.update(subst_dict)

    def __getitem__(self, var: "Variable") -> "Term":
        # map variables to themselves if no substitution specified
        return deepcopy(dict.__getitem__(self, var)) if var in self else deepcopy(var)

    def __eq__(self, other: "Substitution") -> bool:
        return isinstance(other, Substitution) and super(Substitution, self).__eq__(other)

    def __hash__(self) -> int:
        return hash( ("substitution", frozenset(self.items())) )

    def __add__(self, other: "Substitution") -> "Substitution":
        subst = dict(self.items())

        for var, target in other.items():
            if var in subst:
                if not target == subst[var]:
                    raise AssignmentError(self, other)
            else:
                subst[var] = target
        
        return Substitution(subst)