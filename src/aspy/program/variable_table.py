from typing import Dict, Optional, Set, Union

from .symbols import SpecialChar
from .terms import AnonVariable, ArithTerm, ArithVariable, Variable


class VariableTable:
    def __init__(
        self, variables: Optional[Union[Dict[Variable, bool], Set[Variable]]] = None
    ) -> None:
        self.variables = dict()
        self.anon_counter = 0
        self.arith_counter = 0

        if variables is not None:
            self.update(variables)

    def __contains__(self, var: str) -> bool:
        if var in self.variables:
            return True

        return False

    def __str__(self) -> str:
        variables_str = ",".join(
            var.val if not is_global else f"{var.val}*"
            for (var, is_global) in self.variables.items()
        )

        return f"{{{variables_str}}}"

    def __getitem__(self, symbol: str) -> Variable:
        return self.variables[symbol]

    def __setitem__(self, symbol: str, is_global: bool) -> None:
        self.variables[symbol] = is_global

    def register(self, var: Variable, is_global: bool = False) -> None:
        # adjust counters if necessary
        if isinstance(var, AnonVariable):
            self.anon_counter = max(self.anon_counter, var.id + 1)
        elif isinstance(var, ArithVariable):
            self.arith_counter = max(self.arith_counter, var.id + 1)

        self.variables[var] = is_global

    def update(self, vars: Union[Dict[Variable, bool], Set[Variable]]) -> None:

        if isinstance(vars, Set):
            vars = {var: False for var in vars}

        self.variables.update(vars)

        # adjust counters if necessary
        for var in vars.keys():
            if isinstance(var, AnonVariable):
                self.anon_counter = max(self.anon_counter, var.id + 1)
            elif isinstance(var, ArithVariable):
                self.arith_counter = max(self.arith_counter, var.id + 1)

    def create(
        self,
        symbol: str = "_",
        register: bool = True,
        is_global: bool = False,
        orig_term: Optional["ArithTerm"] = None,
    ) -> Variable:
        # anonymous variable
        if symbol == "_":
            # get current id for anonymous variables
            id = self.anon_counter
            # increase counter
            self.anon_counter += 1

            # create new variable
            var = AnonVariable(id)
        # special 'arithmetic replacement' variable
        elif symbol == SpecialChar.TAU.value:

            if orig_term is None:
                raise ValueError(
                    "Variable table cannot create arithmetic variable without specifying 'orig_term'."  # noqa
                )

            # get current id for arithmetic variables
            id = self.arith_counter
            # increase counter
            self.arith_counter += 1

            # create new variable
            var = ArithVariable(id, orig_term)
        # variable
        else:
            # check if variable is already known
            # (to avoid duplicate variables where possible)
            for var in self.variables:
                if symbol == var.val:
                    # return existing variable
                    return var

            # create new variable
            var = Variable(symbol)

        if register:
            # register new variable
            self.register(var, is_global)

        # return newly created variable
        return var

    def vars(self) -> Set["Variable"]:
        return set(self.variables.keys())

    def global_vars(self) -> Set["Variable"]:
        return set(var for (var, is_global) in self.variables.items() if is_global)

    def arith_vars(self) -> Set["ArithVariable"]:
        return set(var for var in self.variables if isinstance(var, ArithVariable))
