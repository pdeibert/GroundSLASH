import unittest

import aspy
from aspy.program.literals import (
    AggregateCount,
    AggregateElement,
    AggregateLiteral,
    AlphaLiteral,
    EpsLiteral,
    Equal,
    EtaLiteral,
    GreaterEqual,
    Guard,
    LessEqual,
    LiteralTuple,
    PredicateLiteral,
)
from aspy.program.operators import RelOp
from aspy.program.statements import EpsRule, EtaRule, rewrite_aggregate
from aspy.program.terms import Number, TermTuple, Variable


class TestRewrite(unittest.TestCase):
    def test_rewrite_aggregate(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        # rewrite aggregates
        elements_1 = (
            AggregateElement(TermTuple(Variable("Y")), LiteralTuple(PredicateLiteral("p", Variable("Y")))),
            AggregateElement(TermTuple(Number(0)), LiteralTuple(PredicateLiteral("p", Number(0)))),
        )
        aggregate_1 = AggregateLiteral(AggregateCount(), elements_1, Guard(RelOp.GREATER_OR_EQ, Variable("X"), False))

        elements_2 = (AggregateElement(TermTuple(Number(0)), LiteralTuple(PredicateLiteral("q", Number(0)))),)
        aggregate_2 = AggregateLiteral(AggregateCount(), elements_2, Guard(RelOp.LESS_OR_EQ, Number(0), True))

        alpha_literal, eps_rule, eta_rules = rewrite_aggregate(
            aggregate_1, 1, {Variable("X")}, [PredicateLiteral("q", Variable("X")), Equal(Number(0), Variable("X"))]
        )
        self.assertEqual(alpha_literal, AlphaLiteral(1, TermTuple(Variable("X")), TermTuple(Variable("X"))))
        self.assertEqual(
            eps_rule,
            EpsRule(
                EpsLiteral(1, TermTuple(Variable("X")), TermTuple(Variable("X"))),
                Guard(RelOp.GREATER_OR_EQ, Variable("X"), False),
                None,
                LiteralTuple(
                    GreaterEqual(Variable("X"), AggregateCount().base()),
                    PredicateLiteral("q", Variable("X")),
                    Equal(Number(0), Variable("X")),
                ),
            ),
        )
        self.assertEqual(len(eta_rules), 2)
        self.assertEqual(
            eta_rules[0],
            EtaRule(
                EtaLiteral(
                    1, 0, TermTuple(Variable("Y")), TermTuple(Variable("X")), TermTuple(Variable("Y"), Variable("X"))
                ),
                elements_1[0],
                LiteralTuple(
                    PredicateLiteral("p", Variable("Y")),
                    PredicateLiteral("q", Variable("X")),
                    Equal(Number(0), Variable("X")),
                ),
            ),
        )
        self.assertEqual(
            eta_rules[1],
            EtaRule(
                EtaLiteral(1, 1, TermTuple(), TermTuple(Variable("X")), TermTuple(Variable("X"))),
                elements_1[1],
                LiteralTuple(
                    PredicateLiteral("p", Number(0)),
                    PredicateLiteral("q", Variable("X")),
                    Equal(Number(0), Variable("X")),
                ),
            ),
        )

        alpha_literal, eps_rule, eta_rules = rewrite_aggregate(
            aggregate_2, 2, {Variable("X")}, [PredicateLiteral("q", Variable("X")), Equal(Number(0), Variable("X"))]
        )
        self.assertEqual(alpha_literal, AlphaLiteral(2, TermTuple(), TermTuple()))
        self.assertEqual(
            eps_rule,
            EpsRule(
                EpsLiteral(2, TermTuple(), TermTuple()),
                None,
                Guard(RelOp.LESS_OR_EQ, Number(0), True),
                LiteralTuple(
                    LessEqual(AggregateCount().base(), Number(0)),
                    PredicateLiteral("q", Variable("X")),
                    Equal(Number(0), Variable("X")),
                ),
            ),
        )
        self.assertEqual(len(eta_rules), 1)
        self.assertEqual(
            eta_rules[0],
            EtaRule(
                EtaLiteral(2, 0, TermTuple(), TermTuple(), TermTuple()),
                elements_2[0],
                LiteralTuple(
                    PredicateLiteral("q", Number(0)),
                    PredicateLiteral("q", Variable("X")),
                    Equal(Number(0), Variable("X")),
                ),
            ),
        )


if __name__ == "__main__":
    unittest.main()
