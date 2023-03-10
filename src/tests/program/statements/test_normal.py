import unittest

import aspy
from aspy.program.literals import (
    AggrBaseLiteral,
    AggregateCount,
    AggregateElement,
    AggregateLiteral,
    AggrElemLiteral,
    AggrPlaceholder,
    Equal,
    GreaterEqual,
    Guard,
    LessEqual,
    LiteralTuple,
    PredicateLiteral,
)
from aspy.program.operators import RelOp
from aspy.program.statements import AggrBaseRule, AggrElemRule, NormalFact, NormalRule
from aspy.program.substitution import Substitution
from aspy.program.terms import Number, String, TermTuple, Variable


class TestNormal(unittest.TestCase):
    def test_normal_fact(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        ground_rule = NormalFact(PredicateLiteral("p", Number(0)))
        var_rule = NormalFact(PredicateLiteral("p", Variable("X")))

        # string representation
        self.assertEqual(str(ground_rule), "p(0).")
        self.assertEqual(str(var_rule), "p(X).")
        # equality
        self.assertEqual(
            ground_rule.head, LiteralTuple(PredicateLiteral("p", Number(0)))
        )
        self.assertEqual(ground_rule.body, LiteralTuple())
        self.assertEqual(
            var_rule.head, LiteralTuple(PredicateLiteral("p", Variable("X")))
        )
        self.assertEqual(var_rule.body, LiteralTuple())
        # hashing
        self.assertEqual(
            hash(ground_rule), hash(NormalFact(PredicateLiteral("p", Number(0))))
        )
        self.assertEqual(
            hash(var_rule), hash(NormalFact(PredicateLiteral("p", Variable("X"))))
        )
        # ground
        self.assertTrue(ground_rule.ground)
        self.assertFalse(var_rule.ground)
        # safety
        self.assertTrue(ground_rule.safe)
        self.assertFalse(var_rule.safe)
        # variables
        self.assertTrue(ground_rule.vars() == ground_rule.global_vars() == set())
        self.assertTrue(var_rule.vars() == var_rule.global_vars() == {Variable("X")})
        # TODO: replace arithmetic terms

        # substitution
        rule = NormalFact(PredicateLiteral("p", Variable("X"), Number(0)))
        self.assertEqual(
            rule.substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            NormalFact(PredicateLiteral("p", Number(1), Number(0))),
        )  # NOTE: substitution is invalid

        # rewrite aggregates
        self.assertEqual(rule, rule.rewrite_aggregates(0, dict()))
        # assembling
        self.assertEqual(rule, rule.assemble_aggregates(dict()))

        # TODO: propagate

    def test_normal_rule(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        ground_rule = NormalRule(
            PredicateLiteral("p", Number(0)), PredicateLiteral("q")
        )
        unsafe_var_rule = NormalRule(
            PredicateLiteral("p", Variable("X")), PredicateLiteral("q")
        )
        safe_var_rule = NormalRule(
            PredicateLiteral("p", Variable("X")), PredicateLiteral("q", Variable("X"))
        )

        # string representation
        self.assertEqual(str(ground_rule), "p(0) :- q.")
        self.assertEqual(str(unsafe_var_rule), "p(X) :- q.")
        self.assertEqual(str(safe_var_rule), "p(X) :- q(X).")
        # equality
        self.assertEqual(
            ground_rule.head, LiteralTuple(PredicateLiteral("p", Number(0)))
        )
        self.assertEqual(ground_rule.body, LiteralTuple(PredicateLiteral("q")))
        self.assertEqual(
            unsafe_var_rule.head, LiteralTuple(PredicateLiteral("p", Variable("X")))
        )
        self.assertEqual(unsafe_var_rule.body, LiteralTuple(PredicateLiteral("q")))
        self.assertEqual(
            safe_var_rule.head, LiteralTuple(PredicateLiteral("p", Variable("X")))
        )
        self.assertEqual(
            safe_var_rule.body, LiteralTuple(PredicateLiteral("q", Variable("X")))
        )
        # hashing
        self.assertEqual(
            hash(ground_rule),
            hash(NormalRule(PredicateLiteral("p", Number(0)), PredicateLiteral("q"))),
        )
        self.assertEqual(
            hash(unsafe_var_rule),
            hash(
                NormalRule(PredicateLiteral("p", Variable("X")), PredicateLiteral("q"))
            ),
        )
        self.assertEqual(
            hash(safe_var_rule),
            hash(
                NormalRule(
                    PredicateLiteral("p", Variable("X")),
                    PredicateLiteral("q", Variable("X")),
                )
            ),
        )
        # ground
        self.assertTrue(ground_rule.ground)
        self.assertFalse(unsafe_var_rule.ground)
        self.assertFalse(safe_var_rule.ground)
        # safety
        self.assertTrue(ground_rule.safe)
        self.assertFalse(unsafe_var_rule.safe)
        self.assertTrue(safe_var_rule.safe)
        # contains aggregates
        self.assertFalse(ground_rule.contains_aggregates)
        self.assertFalse(unsafe_var_rule.contains_aggregates)
        self.assertFalse(safe_var_rule.contains_aggregates)
        self.assertTrue(
            NormalRule(
                PredicateLiteral("p", Variable("X")),
                AggregateLiteral(
                    AggregateCount(), tuple(), Guard(RelOp.EQUAL, Number(1), False)
                ),
            ).contains_aggregates
        )
        # variables
        self.assertTrue(ground_rule.vars() == ground_rule.global_vars() == set())
        self.assertTrue(
            unsafe_var_rule.vars() == unsafe_var_rule.global_vars() == {Variable("X")}
        )
        self.assertTrue(
            safe_var_rule.vars() == safe_var_rule.global_vars() == {Variable("X")}
        )
        # TODO: replace arithmetic terms

        # substitution
        rule = NormalRule(
            PredicateLiteral("p", Variable("X"), Number(0)),
            PredicateLiteral("q", Variable("X")),
        )
        self.assertEqual(
            rule.substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            NormalRule(
                PredicateLiteral("p", Number(1), Number(0)),
                PredicateLiteral("q", Number(1)),
            ),
        )  # NOTE: substitution is invalid

        # rewrite aggregates
        elements_1 = (
            AggregateElement(
                TermTuple(Variable("Y")),
                LiteralTuple(PredicateLiteral("p", Variable("Y"))),
            ),
            AggregateElement(
                TermTuple(Number(0)), LiteralTuple(PredicateLiteral("p", Number(0)))
            ),
        )
        elements_2 = (
            AggregateElement(
                TermTuple(Number(0)), LiteralTuple(PredicateLiteral("q", Number(0)))
            ),
        )
        rule = NormalRule(
            PredicateLiteral("p", Variable("X"), Number(0)),
            AggregateLiteral(
                AggregateCount(),
                elements_1,
                Guard(RelOp.GREATER_OR_EQ, Variable("X"), False),
            ),
            PredicateLiteral("q", Variable("X")),
            Equal(Number(0), Variable("X")),
            AggregateLiteral(
                AggregateCount(), elements_2, Guard(RelOp.LESS_OR_EQ, Number(0), True)
            ),
        )
        target_rule = NormalRule(
            PredicateLiteral("p", Variable("X"), Number(0)),
            AggrPlaceholder(1, TermTuple(Variable("X")), TermTuple(Variable("X"))),
            PredicateLiteral("q", Variable("X")),
            Equal(Number(0), Variable("X")),
            AggrPlaceholder(2, TermTuple(), TermTuple()),
        )
        aggr_map = dict()

        self.assertEqual(rule.rewrite_aggregates(1, aggr_map), target_rule)
        self.assertEqual(len(aggr_map), 2)

        aggr_literal, alpha_literal, eps_rule, eta_rules = aggr_map[1]
        self.assertEqual(aggr_literal, rule.body[0])
        self.assertEqual(alpha_literal, target_rule.body[0])
        self.assertEqual(
            eps_rule,
            AggrBaseRule(
                AggrBaseLiteral(1, TermTuple(Variable("X")), TermTuple(Variable("X"))),
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
            AggrElemRule(
                AggrElemLiteral(
                    1,
                    0,
                    TermTuple(Variable("Y")),
                    TermTuple(Variable("X")),
                    TermTuple(Variable("Y"), Variable("X")),
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
            AggrElemRule(
                AggrElemLiteral(
                    1,
                    1,
                    TermTuple(),
                    TermTuple(Variable("X")),
                    TermTuple(Variable("X")),
                ),
                elements_1[1],
                LiteralTuple(
                    PredicateLiteral("p", Number(0)),
                    PredicateLiteral("q", Variable("X")),
                    Equal(Number(0), Variable("X")),
                ),
            ),
        )

        aggr_literal, alpha_literal, eps_rule, eta_rules = aggr_map[2]
        self.assertEqual(aggr_literal, rule.body[-1])
        self.assertEqual(alpha_literal, target_rule.body[-1])
        self.assertEqual(
            eps_rule,
            AggrBaseRule(
                AggrBaseLiteral(2, TermTuple(), TermTuple()),
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
            AggrElemRule(
                AggrElemLiteral(2, 0, TermTuple(), TermTuple(), TermTuple()),
                elements_2[0],
                LiteralTuple(
                    PredicateLiteral("q", Number(0)),
                    PredicateLiteral("q", Variable("X")),
                    Equal(Number(0), Variable("X")),
                ),
            ),
        )

        # assembling
        target_rule = NormalRule(
            PredicateLiteral("p", Variable("X"), Number(0)),
            AggrPlaceholder(1, TermTuple(Variable("X")), TermTuple(Variable("X"))),
            PredicateLiteral("q", Variable("X")),
            Equal(Number(0), Variable("X")),
            AggrPlaceholder(2, TermTuple(), TermTuple()),
        )
        elements_1 = (
            AggregateElement(
                TermTuple(Variable("Y")),
                LiteralTuple(PredicateLiteral("p", Variable("Y"))),
            ),
            AggregateElement(
                TermTuple(Number(0)), LiteralTuple(PredicateLiteral("p", Number(0)))
            ),
        )
        elements_2 = (
            AggregateElement(
                TermTuple(Number(0)), LiteralTuple(PredicateLiteral("q", Number(0)))
            ),
        )

        self.assertEqual(
            target_rule.assemble_aggregates(
                {
                    AggrPlaceholder(
                        1, TermTuple(Variable("X")), TermTuple(Variable("X"))
                    ): AggregateLiteral(
                        AggregateCount(),
                        (
                            AggregateElement(
                                TermTuple(Number(0)),
                                LiteralTuple(PredicateLiteral("p", Number(0))),
                            ),
                            AggregateElement(TermTuple(String("f")), LiteralTuple()),
                        ),
                        Guard(RelOp.GREATER_OR_EQ, Number(-1), False),
                    ),
                    AggrPlaceholder(2, TermTuple(), TermTuple()): AggregateLiteral(
                        AggregateCount(),
                        (
                            AggregateElement(
                                TermTuple(Number(0)),
                                LiteralTuple(PredicateLiteral("q", Number(0))),
                            ),
                        ),
                        Guard(RelOp.LESS_OR_EQ, Number(0), True),
                    ),
                }
            ),
            NormalRule(
                PredicateLiteral("p", Variable("X"), Number(0)),
                AggregateLiteral(
                    AggregateCount(),
                    (
                        AggregateElement(
                            TermTuple(Number(0)),
                            LiteralTuple(PredicateLiteral("p", Number(0))),
                        ),
                        AggregateElement(TermTuple(String("f")), LiteralTuple()),
                    ),
                    Guard(RelOp.GREATER_OR_EQ, Number(-1), False),
                ),
                PredicateLiteral("q", Variable("X")),
                Equal(Number(0), Variable("X")),
                AggregateLiteral(
                    AggregateCount(),
                    (
                        AggregateElement(
                            TermTuple(Number(0)),
                            LiteralTuple(PredicateLiteral("q", Number(0))),
                        ),
                    ),
                    Guard(RelOp.LESS_OR_EQ, Number(0), True),
                ),
            ),
        )

        # TODO: propagate


if __name__ == "__main__":
    unittest.main()
