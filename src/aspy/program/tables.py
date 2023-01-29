from .terms import Variable, AnonVariable


class VariableTable:
    def __init__(self) -> None:
        self.variables = set()
        self.anon_counter = 0

    def __contains__(self, var: str) -> bool:
        if var in self.variables:
            return True
        
        return False

    def __repr__(self) -> str:
        return f"VariableTable({self.variables},{self.anon_counter})"

    def __str__(self) -> str:
        return str(self.variables)

    def register(self, symbol: str="_", safe: bool=False) -> Variable:
        # anonymous variable
        if symbol == "_":
            # get current id for anonymous variables
            id = self.anon_counter
            # increase counter
            self.anon_counter += 1

            # create new variable
            var = AnonVariable(id)

            # register new variable
            self.variables.add(var)
        # variable
        else:
            # check if variable is already known
            for var in self.variables:
                if symbol == var.val:
                    # return existing variable
                    return var

            # create new variable
            var = Variable(symbol)

            # register new variable
            self.variables.add(var)

        # return newly created variable
        return var