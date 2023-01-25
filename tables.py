from typing import List, Union
from dataclasses import dataclass

from term import Variable, AnonVariable


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
    variables: List[str]

    def __init__(self) -> None:
        self.variables = []
        self.anon_counter = 0

    def __contains__(self, var: str) -> bool:
        if var in self.variables:
            return True
        
        return False

    def register(self, var: str="_") -> Union[Variable, AnonVariable]:

        # anonymous variable
        if var == "_":
            # get current id for anonymous variables
            id = self.anon_counter
            # increase counter
            self.anon_counter += 1

            # create new variable symbol
            symbol = AnonVariable(id)

            # register new variable symbol
            self.variables.append(f"_{id}")
        # variable
        else:
            # check if variable is already known
            if var not in self.variables:
                # register new variable symbol
                self.variables.append(var)

            # create new variable symbol
            symbol = Variable(var)

        # return newly created symbol
        return symbol