from .expression import Expr


class AssignmentError(Exception):
    def __init__(self, subst_1: "Substitution", subst_2: "Substitution") -> None:
        super().__init__(f"Substitution {subst_1} is inconsistent with substitution {subst_2}.")


class MatchError(Exception):
    def __init__(self, candidate: "Expr", target: "Expr") -> None:
        super().__init__(f"{candidate} cannot be matched to {target}.")


class Substitution(dict):
    def merge(self, other: "Substitution") -> None:
        for var in other.keys():
            if var in self.keys():
                # check if assignments differ
                matches = self[var].match(other[var])

                # if assignments do not match
                if len(matches) == 0 or not matches[0]:
                    raise AssignmentError(self, other)
            else:
                # integrate assignment
                self[var] = other[var]