from typing import Tuple

from statement import Statement
from query import Query
from tables import ConstantTable


class Program:
    def __init__(self, statements: Tuple[Statement, ...], query: Query, constants: ConstantTable) -> None:
        self.statements = statements
        self.query = query
        self.constants = constants