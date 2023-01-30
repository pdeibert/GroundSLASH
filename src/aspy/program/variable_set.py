from typing import Iterable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .terms import Variable


class VariableSet:
    def __init__(self, variables: Optional[Iterable["Variable"]]=None) -> None:

        self.elements = []

        if variables is None:
            variables = []

        for var in variables:
            for elem in self.elements:
                # variable already known
                if var.val == elem.val:
                    break
            # variable not known
            else:
                self.elements.append(var)

    def __repr__(self) -> str:
        return f"VariableSet({','.join([repr(elem) for elem in self.elements])})"

    def __str__(self) -> str:
        return f"{{{','.join([str(elem) for elem in self.elements])}}}"

    def __contains__(self, var: "Variable") -> bool:
        for elem in self.elements:
            if var.val == elem.val:
                return True

        return False

    def __getitem__(self, val: str) -> "Variable":
        for elem in self.elements:
            if val == elem.val:
                return elem

        raise LookupError(f"Variable set does not contain variable of value {val}.")

    def __eq__(self, other: "VariableSet") -> bool:

        if len(self.elements) != len(other.elements):
            return False

        for var in self.elements:
            if not var in other:
                return False
        
        return True

    def __add__(self, other: "VariableSet") -> "VariableSet":
        return self.union(other)

    def __sub__(self, other: "VariableSet") -> "VariableSet":
        return self.setminus(other)

    def copy(self) -> "VariableSet":
        # since we already know that this is a 'VariableSet', we can assume there are no duplicates (can exploited to speed up process by bypassing constructor check)
        var_set = VariableSet()
        var_set.elements = self.elements.copy()

        return var_set

    def add(self, var: "Variable") -> None:
        for elem in self.elements:
            # variable already in set
            if elem.val == var.val:
                break
        else:
            self.elements.append(var)

    def update(self, other: "VariableSet") -> None:
        # since we already know that both are 'VariableSet's, we can assume they contain no duplicates (can exploited to speed up process by bypassing constructor check)

        # values (i.e., variable names) of variables in this 'set'
        self_vals = [var.val for var in self.elements]

        for var in other.elements:
            if var.val not in self_vals:
                self.elements.append(var)

    def union(self, other: "VariableSet") -> "VariableSet":
        # since we already know that both are 'VariableSet's, we can assume they contain no duplicates (can exploited to speed up process by bypassing constructor check)
        elements = self.elements.copy()

        # values (i.e., variable names) of variables in this 'set'
        self_vals = [var.val for var in self.elements]

        for var in other.elements:
            if var.val not in self_vals:
                elements.append(var)

        var_set = VariableSet()
        # set elements manually
        var_set.elements = elements

        return var_set

    def intersection(self, other: "VariableSet") -> "VariableSet":
        # since we already know that both are 'VariableSet's, we can assume they contain no duplicates (can exploited to speed up process by bypassing constructor check)
        elements = []

        for var in self.elements:
            for elem in other.elements:
                # variable in both sets
                if var.val == elem.val:
                    elements.append(var)
                    break

        var_set = VariableSet()
        # set elements manually
        var_set.elements = elements

        return var_set

    def setminus(self, other: "VariableSet") -> "VariableSet":
        # since we already know that both are 'VariableSet's, we can assume they contain no duplicates (can exploited to speed up process by bypassing constructor check)
        elements = []

        for var in self.elements:
            for elem in other.elements:
                # variable in both sets
                if var.val == elem.val:
                    break
            else:
                elements.append(var)

        var_set = VariableSet()
        # set elements manually
        var_set.elements = elements

        return var_set