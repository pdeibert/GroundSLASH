from typing import Tuple

from statement import Statement
from query import Query
from tables import ConstantTable


class Program:
    """Program."""
    def __init__(self, statements: Tuple[Statement, ...], query: Query, constants: ConstantTable) -> None:
        self.statements = statements
        self.query = query
        self.constants = constants

    def __repr__(self) -> str:
        # TODO: output query
        return '\n'.join([repr(statement) for statement in self.statements])

    def __str__(self) -> str:
        # TODO: output query
        return '\n'.join([str(statement) for statement in self.statements])

    def is_safe(self) -> bool:
        # TODO: are queries relevant?
        return all([statement.is_safe() for statement in self.statements])