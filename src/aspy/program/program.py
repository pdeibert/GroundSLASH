from functools import cached_property
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple

import antlr4  # type: ignore

from aspy.antlr.ASPCoreLexer import ASPCoreLexer
from aspy.antlr.ASPCoreParser import ASPCoreParser

from .program_builder import ProgramBuilder

# from .statements import Fact, Rule, Constraint, WeakConstraint

if TYPE_CHECKING:  # pragma: no cover
    from .literals import AggrPlaceholder
    from .query import Query
    from .statements import AggrBaseRule, AggrElemRule, Statement


class Program:
    """Program."""

    def __init__(
        self, statements: Tuple["Statement", ...], query: Optional["Query"] = None
    ) -> None:
        self.statements = statements
        self.query = query

    def __eq__(self, other: "Program") -> bool:
        return (
            set(self.statements) == set(other.statements) and self.query == other.query
        )

    def __str__(self) -> str:
        return "\n".join([str(statement) for statement in self.statements]) + (
            "\n" + str(self.query) if self.query is not None else ""
        )

    def reduct(self, preds: Set[Tuple[str, int]]) -> "Program":
        """Program reduction as described in Definition 15. in TODO."""
        return Program(
            tuple(
                statement
                for statement in self.statements
                if not any(
                    literal.pred() in preds for literal in statement.body.neg_occ()
                )
            )
        )

    def replace_arith(self) -> "Program":
        return Program(
            tuple(statement.replace_arith() for statement in self.statements),
            self.query,
        )

    def rewrite_aggregates(
        self,
    ) -> Tuple[
        "Program",
        "Program",
        "Program",
        Dict[int, Tuple["AggrPlaceholder", "AggrBaseRule", List["AggrElemRule"]]],
    ]:

        # TODO: get actual counter?
        aggr_counter = 0

        alpha_statements = []
        eps_statements = []
        eta_statements = []

        aggr_map = dict()

        for statement in self.statements:

            alpha_statement = statement.rewrite_aggregates(aggr_counter, aggr_map)

            for *_, eps_statement, eta_statements in aggr_map.values():
                eps_statements.append(eps_statement)
                eta_statements += eta_statements
                aggr_counter += 1

            alpha_statements.append(alpha_statement)

        return (
            Program(alpha_statements, self.query),
            Program(eps_statements),
            Program(eta_statements),
            aggr_map,
        )

    @cached_property
    def safe(self) -> bool:
        return all(statement.safe for statement in self.statements)  # TODO: query?

    @classmethod
    def from_string(cls, prog_str: str) -> "Program":

        input_stream = antlr4.InputStream(prog_str)  # type: ignore

        # tokenize input program
        lexer = ASPCoreLexer(input_stream)
        stream = antlr4.CommonTokenStream(lexer)  # type: ignore
        stream.fill()

        parser = ASPCoreParser(stream)
        tree = parser.program()

        # traverse parse tree using visitor
        statements, query = ProgramBuilder().visit(tree)

        return Program(tuple(statements), query)

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
