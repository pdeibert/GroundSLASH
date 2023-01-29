from typing import Tuple, TYPE_CHECKING
from functools import cached_property

from .statements import Fact, Rule, Constraint, WeakConstraint

if TYPE_CHECKING:
    from .statements import Statement
    from .query import Query


class Program:
    """Program."""
    def __init__(self, statements: Tuple["Statement", ...], query: "Query") -> None:
        self.statements = statements
        self.query = query

    def __repr__(self) -> str:
        return '\n'.join([repr(statement) for statement in self.statements]) + '\n' + repr(self.query)

    def __str__(self) -> str:
        return '\n'.join([str(statement) for statement in self.statements]) + '\n' + str(self.query)

    def is_safe(self) -> bool:
        # TODO: are queries relevant?
        return all([statement.is_safe for statement in self.statements])

    def rules(self) -> Tuple[Rule, ...]:
        return self.facts + self.non_facts

    @cached_property
    def facts(self) -> Tuple[Fact, ...]:
        return tuple([statement for statement in self.statements if isinstance(statement, Fact)])

    @cached_property
    def non_facts(self) -> Tuple[Rule, ...]:
        return tuple([statement for statement in self.statements if isinstance(statement, Rule) and not isinstance(statement, Fact)])

    @cached_property
    def constraints(self) -> Tuple[Constraint, ...]:
        return tuple([statement for statement in self.statements if isinstance(statement, Constraint)])

    @cached_property
    def weak_constraints(self) -> Tuple[WeakConstraint, ...]:
        return tuple([statement for statement in self.statements if isinstance(statement, WeakConstraint)])