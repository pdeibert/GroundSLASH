from typing import Tuple, TYPE_CHECKING

#from .statements import Fact, Rule, Constraint, WeakConstraint

if TYPE_CHECKING:
    from .statements import Statement
    from .query import Query


class Program:
    """Program."""
    def __init__(self, statements: Tuple["Statement", ...], query: "Query") -> None:
        self.statements = statements
        self.query = query

    def __str__(self) -> str:
        return '\n'.join('\n'.join([str(statement) for statement in self.statements]), str(self.query))

    """
    @property
    def rules(self) -> Tuple[Rule, ...]:
        return self.facts + self.non_facts

    def facts(self) -> Tuple[Fact, ...]:
        return tuple([statement for statement in self.statements if isinstance(statement, Fact)])

    def non_facts(self) -> Tuple[Rule, ...]:
        return tuple([statement for statement in self.statements if isinstance(statement, Rule) and not isinstance(statement, Fact)])

    def constraints(self) -> Tuple[Constraint, ...]:
        return tuple([statement for statement in self.statements if isinstance(statement, Constraint)])

    def weak_constraints(self) -> Tuple[WeakConstraint, ...]:
        return tuple([statement for statement in self.statements if isinstance(statement, WeakConstraint)])
    """