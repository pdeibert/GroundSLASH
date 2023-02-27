from typing import Set, Tuple, List, TYPE_CHECKING

from aspy.program.literals import AlphaLiteral
from .special import EpsRule, EtaRule

if TYPE_CHECKING:
    from aspy.program.terms import Variable, TermTuple
    from aspy.program.literals import Literal, AggregateLiteral, LiteralTuple


def rewrite_aggregate(literal: "AggregateLiteral", aggr_counter: int, glob_vars: Set["Variable"], body_literals: Set["Literal"]) -> Tuple["AlphaLiteral", "EpsRule", List["EtaRule"]]:

        # TODO: if this does not work due to circular imports, provide it as a method in program (or someplace else)
        aggr_glob_vars = glob_vars.intersection(literal.vars())

        # ----- create predicate literal for each aggregate occurrence -----
        alpha_literal = AlphaLiteral(aggr_counter, aggr_glob_vars, naf=literal.naf)

        # ----- epsilon rule -----
        eps_rule = EpsRule.from_scratch(
            aggr_counter,
            TermTuple(*aggr_glob_vars),
            *literal.guards,
            literal.func.base(),
            LiteralTuple(*body_literals)
        )

        # ----- eta rules -----
        eta_rules = []

        for element_counter, element in enumerate(literal.func.elements):
            eta_rules.append(
                EtaRule.from_scratch(
                    aggr_counter,
                    element_counter,
                    TermTuple(aggr_glob_vars),
                    element,
                    LiteralTuple(*body_literals)
                )
            )

        return (alpha_literal, eps_rule, eta_rules)