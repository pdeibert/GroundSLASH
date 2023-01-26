from typing import Dict, List, Union
from dataclasses import dataclass

from .term import Variable, AnonVariable


@dataclass
class ConstantTable:
    constants: List[Union[str, int]]

    def __init__(self) -> None:
        self.constants = []

    def __contains__(self, constant: Union[str, int]) -> bool:
        if constant in self.constants:
            return True
        
        return False

    def register(self, constant: Union[str, int]) -> None:

        # check if constant is already known
        if constant not in self.constants:
            # register new constant symbol
            self.constants.append(constant)


class VariableTable:
    def __init__(self) -> None:
        self.variables: Dict[str,bool] = {} # name : safe
        self.anon_counter = 0

    def __contains__(self, var: str) -> bool:
        if var in self.variables:
            return True
        
        return False

    def __repr__(self) -> str:
        return f"VariableTable({self.variables},{self.anon_counter})"

    def __str__(self) -> str:
        return str(self.variables)

    def merge(self, other: "VariableTable") -> "VariableTable":
        for var, safe in other.variables.items():
            if not var in self.variables:
                self.variables[var] = safe
            elif safe:
                self.variables[var] = safe
        
        return self

    def register(self, var: str="_", safe: bool=False) -> Union[Variable, AnonVariable]:
        # anonymous variable
        if var == "_":
            # get current id for anonymous variables
            id = self.anon_counter
            # increase counter
            self.anon_counter += 1

            # create new variable symbol
            symbol = AnonVariable(id)

            # register new variable symbol
            self.variables[f"_{id}"] = safe
        # variable
        else:
            # check if variable is already known
            if var not in self.variables:
                # register new variable symbol
                self.variables[var] = safe
            # variable known, but registered as safe (overwrite)
            elif safe:
                self.safe[self.variables.index(var)] = safe

            # create new variable symbol
            symbol = Variable(var)

        # return newly created symbol
        return symbol

    def set_safe(self, safe: Union[bool, Dict[str, bool]]) -> None:
        if isinstance(safe, bool):
            # set boolean value for all variables
            for var in self.variables.keys():
                self.variables[var] = safe
        else:
            self.variables.update(safe)

    def is_safe(self) -> bool:
        return all(self.safe)