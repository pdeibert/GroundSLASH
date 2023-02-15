from typing import Any, Tuple
from abc import ABC, abstractmethod
from copy import deepcopy

from aspy.program.expression import Expr


class Statement(Expr, ABC):
    """Abstract base class for all statements."""
    @abstractmethod
    def __str__(self) -> str:
        pass

    @property
    @abstractmethod
    def head(self) -> Any:
        pass

    @property
    @abstractmethod
    def body(self) -> Any:
        pass

    @property
    @abstractmethod
    def safe(self) -> bool:
        pass


class Rule(Statement, ABC):
    """Abstract base class for all rules."""
    """
    def rewrite(self) -> Tuple["Rule"]:

        # TODO: sort literals (aggregate literals last)
        # TODO: rewrite all aggregate literals
        # TODO: replace all arithmetic terms with new special variable

        # TODO: What else to rewrite ??? (see mu-gringo) 
        # TODO: how does this translate to disjunctive or choice rules ????? same ?????

        rules = []

        non_aggr_literals = []
        aggr_literals = []
        replacement_literals = []

        for literal in self.body:
            if isinstance(literal, AggregateLiteral):
                aggr_literals.append(literal)
            else:
                non_aggr_literals.append(literal)

        
        for aggr in aggr_literals:
            vars = set()
            n = len(vars) # TODO: compute arity (number of global variables occurring in aggregate)

            # ----- create atom for aggregate occurrence -----
            alpha_symbol = self.sym_table.register(CHAR_ALPHA, n)
            replacement_literals.append(PredicateLiteral(alpha_symbol, vars, aggr.naf))

            # ----- epsilon rule -----
            eps_symbol = self.sym_table.register(CHAR_EPS, n)
            guard_literals = []

            # handle left guard
            if literal.lcomp is not None:
                op, term = aggr.lcomp

                # TODO: get value for empty set()
                val = None
                guard_literals.append(op.to_literal(term, val))
            if literal.rcomp is not None:
                op, term = aggr.rcomp

                # TODO: get value for empty set()
                val = None
                guard_literals.append(op.to_literal(val, term))
            # TODO: defaults? see mu-gringo!
            else:
                raise Exception()

            rules.append(
                NormalRule(
                    PredicateLiteral(eps_symbol, vars),
                    LiteralTuple(guard_literals + non_aggr_literals)
                )
            )

            # ----- eta rules -----
            for element in aggr.func.elements:
                eta_symbol = self.sym_table.register(CHAR_ETA, n + len(element.head))

                rules.append(
                    NormalRule(
                        PredicateLiteral(eta_symbol, element.head + vars),
                        LiteralTuple(element.body + non_aggr_literals)
                    )
                )
    
        # ----- replace original rule with modified rule -----
        rules.append(
            NormalRule(
                self.head,
                LiteralTuple(non_aggr_literals + replacement_literals)
            )
        )

        return rules
    """


class Fact(Rule, ABC):
    """Abstract base class for all facts."""

    def rewrite(self) -> Tuple["Fact"]:
        return (deepcopy(self), )