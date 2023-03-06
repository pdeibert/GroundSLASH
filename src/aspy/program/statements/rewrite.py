from typing import TYPE_CHECKING, Iterable, List, Set, Tuple

from aspy.program.literals import AlphaLiteral, LiteralTuple
from aspy.program.terms import TermTuple

from .special import EpsRule, EtaRule

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.literals import AggregateLiteral, Literal, LiteralTuple
    from aspy.program.terms import Variable


def rewrite_aggregate(
    literal: "AggregateLiteral", aggr_counter: int, glob_vars: Set["Variable"], body_literals: Iterable["Literal"]
) -> Tuple["AlphaLiteral", "EpsRule", List["EtaRule"]]:

    # TODO: if this does not work due to circular imports, provide it as a method in program (or someplace else)
    aggr_glob_vars = glob_vars.intersection(literal.vars())
    var_tuple = TermTuple(*aggr_glob_vars)

    # ----- create predicate literal for each aggregate occurrence -----
    alpha_literal = AlphaLiteral(aggr_counter, var_tuple, var_tuple, naf=literal.naf)

    # ----- epsilon rule -----
    eps_rule = EpsRule.from_scratch(
        aggr_counter, var_tuple, *literal.guards, literal.func.base(), LiteralTuple(*body_literals)
    )

    # ----- eta rules -----
    eta_rules = []

    for element_counter, element in enumerate(literal.elements):
        eta_rules.append(
            EtaRule.from_scratch(aggr_counter, element_counter, var_tuple, element, LiteralTuple(*body_literals))
        )

    return (alpha_literal, eps_rule, eta_rules)
