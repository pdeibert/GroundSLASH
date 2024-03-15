import unittest
from typing import Self

import ground_slash
from ground_slash.program.literals import (
    AggrBaseLiteral,
    AggrCount,
    AggrElement,
    AggrElemLiteral,
    AggrLiteral,
    AggrPlaceholder,
    Equal,
    GreaterEqual,
    Guard,
    LessEqual,
    LiteralCollection,
    Naf,
    PredLiteral,
)
from ground_slash.program.operators import RelOp
from ground_slash.program.statements import AggrBaseRule, AggrElemRule, DisjunctiveRule
from ground_slash.program.substitution import Substitution
from ground_slash.program.terms import (
    ArithVariable,
    Minus,
    Number,
    String,
    TermTuple,
    Variable,
)


class TestDisjunctive(unittest.TestCase):
    def test_disjunctive_fact(self: Self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        # invalid initialization
        self.assertRaises(
            ValueError, DisjunctiveRule, (PredLiteral("p", Number(0)),)
        )  # not enough atoms
        self.assertRaises(
            ValueError,
            DisjunctiveRule,
            (PredLiteral("p", Number(0)), Naf(PredLiteral("q", Number(0)))),
        )  # not all positive predicate literals

        ground_rule = DisjunctiveRule(
            (PredLiteral("p", Number(1)), PredLiteral("p", Number(0)))
        )
        var_rule = DisjunctiveRule(
            (PredLiteral("p", Number(1)), PredLiteral("p", Variable("X")))
        )

        # string representation
        self.assertEqual(str(ground_rule), "p(1) | p(0).")
        self.assertEqual(str(var_rule), "p(1) | p(X).")
        # equality
        self.assertEqual(
            ground_rule.head,
            LiteralCollection(PredLiteral("p", Number(1)), PredLiteral("p", Number(0))),
        )
        self.assertEqual(ground_rule.body, LiteralCollection())
        self.assertEqual(
            var_rule.head,
            LiteralCollection(
                PredLiteral("p", Number(1)), PredLiteral("p", Variable("X"))
            ),
        )
        self.assertEqual(var_rule.body, LiteralCollection())
        # hashing
        self.assertEqual(
            hash(ground_rule),
            hash(
                DisjunctiveRule(
                    (PredLiteral("p", Number(1)), PredLiteral("p", Number(0)))
                )
            ),
        )
        self.assertEqual(
            hash(var_rule),
            hash(
                DisjunctiveRule(
                    (
                        PredLiteral("p", Number(1)),
                        PredLiteral("p", Variable("X")),
                    )
                )
            ),
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
        # replace arithmetic terms
        self.assertEqual(
            DisjunctiveRule(
                (
                    PredLiteral("q", Number(0)),
                    PredLiteral("p", Minus(Variable("X"))),
                )
            ).replace_arith(),
            DisjunctiveRule(
                (
                    PredLiteral("q", Number(0)),
                    PredLiteral("p", ArithVariable(0, Minus(Variable("X")))),
                )
            ),
        )
        # safety characterization
        # self.assertEqual(ground_rule.safety(), SafetyTriplet())
        # self.assertEqual(var_rule.safety(), SafetyTriplet(unsafe={Variable("X")}))

        # substitution
        rule = DisjunctiveRule(
            (
                PredLiteral("p", Number(1)),
                PredLiteral("p", Variable("X"), Number(0)),
            )
        )
        self.assertEqual(
            rule.substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            DisjunctiveRule(
                (
                    PredLiteral("p", Number(1)),
                    PredLiteral("p", Number(1), Number(0)),
                )
            ),
        )  # NOTE: substitution is invalid

        # rewrite aggregates
        self.assertEqual(rule, rule.rewrite_aggregates(0, dict()))
        # assembling
        self.assertEqual(rule, rule.assemble_aggregates(dict()))

        # TODO: propagate

    def test_disjunctive_rule(self: Self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        # invalid initialization
        self.assertRaises(
            ValueError,
            DisjunctiveRule,
            (PredLiteral("p", Number(0)),),
            (PredLiteral("q", Number(0)),),
        )  # not enough atoms
        self.assertRaises(
            ValueError,
            DisjunctiveRule,
            (PredLiteral("p", Number(0)), Naf(PredLiteral("q", Number(0)))),
            (PredLiteral("q"),),
        )  # not all positive predicate literals in head

        ground_rule = DisjunctiveRule(
            (PredLiteral("p", Number(1)), PredLiteral("p", Number(0))),
            (PredLiteral("q"),),
        )
        unsafe_var_rule = DisjunctiveRule(
            (PredLiteral("p", Number(1)), PredLiteral("p", Variable("X"))),
            (PredLiteral("q"),),
        )
        safe_var_rule = DisjunctiveRule(
            (PredLiteral("p", Number(1)), PredLiteral("p", Variable("X"))),
            (PredLiteral("q", Variable("X")),),
        )

        # string representation
        self.assertEqual(str(ground_rule), "p(1) | p(0) :- q.")
        self.assertEqual(str(unsafe_var_rule), "p(1) | p(X) :- q.")
        self.assertEqual(str(safe_var_rule), "p(1) | p(X) :- q(X).")
        # equality
        self.assertEqual(
            ground_rule.head,
            LiteralCollection(PredLiteral("p", Number(1)), PredLiteral("p", Number(0))),
        )
        self.assertEqual(ground_rule.body, LiteralCollection(PredLiteral("q")))
        self.assertEqual(
            unsafe_var_rule.head,
            LiteralCollection(
                PredLiteral("p", Number(1)), PredLiteral("p", Variable("X"))
            ),
        )
        self.assertEqual(unsafe_var_rule.body, LiteralCollection(PredLiteral("q")))
        self.assertEqual(
            safe_var_rule.head,
            LiteralCollection(
                PredLiteral("p", Number(1)), PredLiteral("p", Variable("X"))
            ),
        )
        self.assertEqual(
            safe_var_rule.body, LiteralCollection(PredLiteral("q", Variable("X")))
        )
        # hashing
        self.assertEqual(
            hash(ground_rule),
            hash(
                DisjunctiveRule(
                    (
                        PredLiteral("p", Number(1)),
                        PredLiteral("p", Number(0)),
                    ),
                    (PredLiteral("q"),),
                )
            ),
        )
        self.assertEqual(
            hash(unsafe_var_rule),
            hash(
                DisjunctiveRule(
                    (
                        PredLiteral("p", Number(1)),
                        PredLiteral("p", Variable("X")),
                    ),
                    (PredLiteral("q"),),
                )
            ),
        )
        self.assertEqual(
            hash(safe_var_rule),
            hash(
                DisjunctiveRule(
                    (
                        PredLiteral("p", Number(1)),
                        PredLiteral("p", Variable("X")),
                    ),
                    (PredLiteral("q", Variable("X")),),
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
            DisjunctiveRule(
                (
                    PredLiteral("p", Number(1)),
                    PredLiteral("p", Variable("X")),
                ),
                (
                    AggrLiteral(
                        AggrCount(), tuple(), Guard(RelOp.EQUAL, Number(1), False)
                    ),
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
        # replace arithmetic terms
        self.assertEqual(
            DisjunctiveRule(
                (
                    PredLiteral("q", Number(0)),
                    PredLiteral("p", Minus(Variable("X"))),
                ),
                (PredLiteral("q", Minus(Variable("Y"))),),
            ).replace_arith(),
            DisjunctiveRule(
                (
                    PredLiteral("q", Number(0)),
                    PredLiteral("p", ArithVariable(0, Minus(Variable("X")))),
                ),
                (PredLiteral("q", ArithVariable(1, Minus(Variable("Y")))),),
            ),
        )

        # substitution
        self.assertEqual(
            DisjunctiveRule(
                (
                    PredLiteral("p", Number(1)),
                    PredLiteral("p", Number(0)),
                ),
                (PredLiteral("q", Number(1)),),
            ).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            DisjunctiveRule(
                (
                    PredLiteral("p", Number(1)),
                    PredLiteral("p", Number(0)),
                ),
                (PredLiteral("q", Number(1)),),
            ),
        )
        rule = DisjunctiveRule(
            (
                PredLiteral("p", Number(1)),
                PredLiteral("p", Variable("X"), Number(0)),
            ),
            (PredLiteral("q", Variable("X")),),
        )
        self.assertEqual(
            rule.substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            DisjunctiveRule(
                (
                    PredLiteral("p", Number(1)),
                    PredLiteral("p", Number(1), Number(0)),
                ),
                (PredLiteral("q", Number(1)),),
            ),
        )  # NOTE: substitution is invalid

        # rewrite aggregates
        elements_1 = (
            AggrElement(
                TermTuple(Variable("Y")),
                LiteralCollection(PredLiteral("p", Variable("Y"))),
            ),
            AggrElement(
                TermTuple(Number(0)), LiteralCollection(PredLiteral("p", Number(0)))
            ),
        )
        elements_2 = (
            AggrElement(
                TermTuple(Number(0)), LiteralCollection(PredLiteral("q", Number(0)))
            ),
        )
        rule = DisjunctiveRule(
            (
                PredLiteral("p", Number(1)),
                PredLiteral("p", Variable("X"), Number(0)),
            ),
            (
                AggrLiteral(
                    AggrCount(),
                    elements_1,
                    Guard(RelOp.GREATER_OR_EQ, Variable("X"), False),
                ),
                PredLiteral("q", Variable("X")),
                Equal(Number(0), Variable("X")),
                AggrLiteral(
                    AggrCount(),
                    elements_2,
                    Guard(RelOp.LESS_OR_EQ, Number(0), True),
                ),
            ),
        )
        target_rule = DisjunctiveRule(
            (
                PredLiteral("p", Number(1)),
                PredLiteral("p", Variable("X"), Number(0)),
            ),
            (
                AggrPlaceholder(1, TermTuple(Variable("X")), TermTuple(Variable("X"))),
                PredLiteral("q", Variable("X")),
                Equal(Number(0), Variable("X")),
                AggrPlaceholder(2, TermTuple(), TermTuple()),
            ),
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
                LiteralCollection(
                    GreaterEqual(Variable("X"), AggrCount().base),
                    PredLiteral("q", Variable("X")),
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
                LiteralCollection(
                    PredLiteral("p", Variable("Y")),
                    PredLiteral("q", Variable("X")),
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
                LiteralCollection(
                    PredLiteral("p", Number(0)),
                    PredLiteral("q", Variable("X")),
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
                LiteralCollection(
                    LessEqual(AggrCount().base, Number(0)),
                    PredLiteral("q", Variable("X")),
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
                LiteralCollection(
                    PredLiteral("q", Number(0)),
                    PredLiteral("q", Variable("X")),
                    Equal(Number(0), Variable("X")),
                ),
            ),
        )

        # assembling
        target_rule = DisjunctiveRule(
            (
                PredLiteral("p", Number(1)),
                PredLiteral("p", Variable("X"), Number(0)),
            ),
            (
                AggrPlaceholder(1, TermTuple(Variable("X")), TermTuple(Variable("X"))),
                PredLiteral("q", Variable("X")),
                Equal(Number(0), Variable("X")),
                AggrPlaceholder(2, TermTuple(), TermTuple()),
            ),
        )
        elements_1 = (
            AggrElement(
                TermTuple(Variable("Y")),
                LiteralCollection(PredLiteral("p", Variable("Y"))),
            ),
            AggrElement(
                TermTuple(Number(0)), LiteralCollection(PredLiteral("p", Number(0)))
            ),
        )
        elements_2 = (
            AggrElement(
                TermTuple(Number(0)), LiteralCollection(PredLiteral("q", Number(0)))
            ),
        )

        self.assertEqual(
            target_rule.assemble_aggregates(
                {
                    AggrPlaceholder(
                        1, TermTuple(Variable("X")), TermTuple(Variable("X"))
                    ): AggrLiteral(
                        AggrCount(),
                        (
                            AggrElement(
                                TermTuple(Number(0)),
                                LiteralCollection(PredLiteral("p", Number(0))),
                            ),
                            AggrElement(TermTuple(String("f")), LiteralCollection()),
                        ),
                        Guard(RelOp.GREATER_OR_EQ, Number(-1), False),
                    ),
                    AggrPlaceholder(2, TermTuple(), TermTuple()): AggrLiteral(
                        AggrCount(),
                        (
                            AggrElement(
                                TermTuple(Number(0)),
                                LiteralCollection(PredLiteral("q", Number(0))),
                            ),
                        ),
                        Guard(RelOp.LESS_OR_EQ, Number(0), True),
                    ),
                }
            ),
            DisjunctiveRule(
                (
                    PredLiteral("p", Number(1)),
                    PredLiteral("p", Variable("X"), Number(0)),
                ),
                (
                    AggrLiteral(
                        AggrCount(),
                        (
                            AggrElement(
                                TermTuple(Number(0)),
                                LiteralCollection(PredLiteral("p", Number(0))),
                            ),
                            AggrElement(TermTuple(String("f")), LiteralCollection()),
                        ),
                        Guard(RelOp.GREATER_OR_EQ, Number(-1), False),
                    ),
                    PredLiteral("q", Variable("X")),
                    Equal(Number(0), Variable("X")),
                    AggrLiteral(
                        AggrCount(),
                        (
                            AggrElement(
                                TermTuple(Number(0)),
                                LiteralCollection(PredLiteral("q", Number(0))),
                            ),
                        ),
                        Guard(RelOp.LESS_OR_EQ, Number(0), True),
                    ),
                ),
            ),
        )

        # TODO: propagate


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
