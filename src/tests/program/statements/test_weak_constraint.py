import unittest

import aspy
from aspy.program.literals import (
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
    PredLiteral,
)
from aspy.program.operators import RelOp
from aspy.program.statements import AggrBaseRule, AggrElemRule, WeakConstraint
from aspy.program.statements.weak_constraint import WeightAtLevel
from aspy.program.substitution import Substitution
from aspy.program.terms import ArithVariable, Minus, Number, String, TermTuple, Variable
from aspy.program.variable_table import VariableTable


class TestWeakConstraint(unittest.TestCase):
    def test_weight_at_level(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        ground_term = WeightAtLevel(Number(0), Number(1), (Number(2), Number(-1)))
        var_term = WeightAtLevel(Number(0), Variable("X"), (Variable("Y"), Number(-1)))

        # string representation
        self.assertEqual(str(ground_term), "[0@1, 2,-1]")
        self.assertEqual(str(var_term), "[0@X, Y,-1]")
        # equality
        self.assertEqual(
            ground_term, WeightAtLevel(Number(0), Number(1), (Number(2), Number(-1)))
        )
        self.assertEqual(
            var_term,
            WeightAtLevel(Number(0), Variable("X"), (Variable("Y"), Number(-1))),
        )
        # hashing
        self.assertEqual(
            hash(ground_term),
            hash(WeightAtLevel(Number(0), Number(1), (Number(2), Number(-1)))),
        )
        self.assertEqual(
            hash(var_term),
            hash(WeightAtLevel(Number(0), Variable("X"), (Variable("Y"), Number(-1)))),
        )
        # ground
        self.assertTrue(ground_term.ground)
        self.assertFalse(var_term.ground)
        # safety characterization
        self.assertTrue(Exception, ground_term.safety)
        self.assertTrue(Exception, var_term.safety)
        # variables
        self.assertTrue(ground_term.vars() == ground_term.global_vars() == set())
        self.assertTrue(
            var_term.vars() == var_term.global_vars() == {Variable("X"), Variable("Y")}
        )
        # replace arithmetic terms
        self.assertEqual(
            WeightAtLevel(
                Number(0), Minus(Variable("X")), (Variable("Y"), Number(-1))
            ).replace_arith(VariableTable()),
            WeightAtLevel(
                Number(0),
                ArithVariable(0, Minus(Variable("X"))),
                (Variable("Y"), Number(-1)),
            ),
        )

        # substitution
        self.assertEqual(
            var_term.substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            WeightAtLevel(Number(0), Number(1), (Variable("Y"), Number(-1))),
        )  # NOTE: substitution is invalid

    def test_weak_constraint(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        ground_rule = WeakConstraint(
            (PredLiteral("p", Number(0)), PredLiteral("q")),
            WeightAtLevel(Number(0), Number(1), (Number(2), Number(-1))),
        )
        var_rule = WeakConstraint(
            (PredLiteral("p", Variable("X")), PredLiteral("q", Variable("X"))),
            WeightAtLevel(Number(0), Variable("X"), (Variable("Y"), Number(-1))),
        )

        # string representation
        self.assertEqual(str(ground_rule), ":~ p(0),q. [0@1, 2,-1]")
        self.assertEqual(str(var_rule), ":~ p(X),q(X). [0@X, Y,-1]")
        # equality
        self.assertEqual(
            ground_rule,
            WeakConstraint(
                (PredLiteral("p", Number(0)), PredLiteral("q")),
                WeightAtLevel(Number(0), Number(1), (Number(2), Number(-1))),
            ),
        )
        self.assertEqual(
            var_rule,
            WeakConstraint(
                (PredLiteral("p", Variable("X")), PredLiteral("q", Variable("X"))),
                WeightAtLevel(Number(0), Variable("X"), (Variable("Y"), Number(-1))),
            ),
        )
        self.assertEqual(ground_rule.head, LiteralCollection())
        self.assertEqual(
            ground_rule.body,
            LiteralCollection(PredLiteral("p", Number(0)), PredLiteral("q")),
        )
        self.assertEqual(var_rule.head, LiteralCollection())
        self.assertEqual(
            var_rule.body,
            LiteralCollection(
                PredLiteral("p", Variable("X")),
                PredLiteral("q", Variable("X")),
            ),
        )
        # hashing
        self.assertEqual(
            hash(ground_rule),
            hash(
                WeakConstraint(
                    (PredLiteral("p", Number(0)), PredLiteral("q")),
                    WeightAtLevel(Number(0), Number(1), (Number(2), Number(-1))),
                ),
            ),
        )
        self.assertEqual(
            hash(var_rule),
            hash(
                WeakConstraint(
                    (PredLiteral("p", Variable("X")), PredLiteral("q", Variable("X"))),
                    WeightAtLevel(
                        Number(0), Variable("X"), (Variable("Y"), Number(-1))
                    ),
                ),
            ),
        )
        # ground
        self.assertTrue(ground_rule.ground)
        self.assertFalse(var_rule.ground)
        # safety
        self.assertTrue(ground_rule.safe)
        self.assertTrue(var_rule.safe)
        # contains aggregates
        self.assertFalse(ground_rule.contains_aggregates)
        self.assertFalse(var_rule.contains_aggregates)
        self.assertTrue(
            WeakConstraint(
                (
                    PredLiteral("p", Variable("X")),
                    AggrLiteral(
                        AggrCount(), tuple(), Guard(RelOp.EQUAL, Number(1), False)
                    ),
                ),
                WeightAtLevel(Number(0), Number(1), (Number(2), Number(-1))),
            ).contains_aggregates
        )
        # variables
        self.assertTrue(ground_rule.vars() == ground_rule.global_vars() == set())
        self.assertTrue(var_rule.vars() == var_rule.global_vars() == {Variable("X")})
        # replace arithmetic terms
        self.assertEqual(
            WeakConstraint(
                (PredLiteral("p", Number(0), Minus(Variable("X"))),),
                WeightAtLevel(
                    Number(0), Minus(Variable("X")), (Variable("Y"), Number(-1))
                ),
            ).replace_arith(VariableTable()),
            WeakConstraint(
                (PredLiteral("p", Number(0), ArithVariable(0, Minus(Variable("X")))),),
                WeightAtLevel(
                    Number(0),
                    ArithVariable(1, Minus(Variable("X"))),
                    (Variable("Y"), Number(-1)),
                ),
            ),
        )

        # substitution
        rule = WeakConstraint(
            (
                PredLiteral("p", Variable("X"), Number(0)),
                PredLiteral("q", Variable("X")),
            ),
            WeightAtLevel(Number(0), Variable("X"), (Variable("Y"), Number(-1))),
        )
        self.assertEqual(
            rule.substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            WeakConstraint(
                (
                    PredLiteral("p", Number(1), Number(0)),
                    PredLiteral("q", Number(1)),
                ),
                WeightAtLevel(Number(0), Number(1), (Variable("Y"), Number(-1))),
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
        rule = WeakConstraint(
            (
                PredLiteral("p", Variable("X"), Number(0)),
                AggrLiteral(
                    AggrCount(),
                    elements_1,
                    Guard(RelOp.GREATER_OR_EQ, Variable("X"), False),
                ),
                PredLiteral("q", Variable("X")),
                Equal(Number(0), Variable("X")),
                AggrLiteral(
                    AggrCount(), elements_2, Guard(RelOp.LESS_OR_EQ, Number(0), True)
                ),
            ),
            WeightAtLevel(Number(0), Number(1), (Number(2), Number(-1))),
        )
        target_rule = WeakConstraint(
            (
                PredLiteral("p", Variable("X"), Number(0)),
                AggrPlaceholder(1, TermTuple(Variable("X")), TermTuple(Variable("X"))),
                PredLiteral("q", Variable("X")),
                Equal(Number(0), Variable("X")),
                AggrPlaceholder(2, TermTuple(), TermTuple()),
            ),
            WeightAtLevel(Number(0), Number(1), (Number(2), Number(-1))),
        )
        aggr_map = dict()

        self.assertEqual(rule.rewrite_aggregates(1, aggr_map), target_rule)
        self.assertEqual(len(aggr_map), 2)

        aggr_literal, alpha_literal, eps_rule, eta_rules = aggr_map[1]
        self.assertEqual(aggr_literal, rule.body[1])
        self.assertEqual(alpha_literal, target_rule.body[1])
        self.assertEqual(
            eps_rule,
            AggrBaseRule(
                AggrBaseLiteral(1, TermTuple(Variable("X")), TermTuple(Variable("X"))),
                Guard(RelOp.GREATER_OR_EQ, Variable("X"), False),
                None,
                LiteralCollection(
                    GreaterEqual(Variable("X"), AggrCount().base),
                    PredLiteral("p", Variable("X"), Number(0)),
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
                    PredLiteral("p", Variable("X"), Number(0)),
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
                    PredLiteral("p", Variable("X"), Number(0)),
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
                    PredLiteral("p", Variable("X"), Number(0)),
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
                    PredLiteral("p", Variable("X"), Number(0)),
                    PredLiteral("q", Number(0)),
                    PredLiteral("q", Variable("X")),
                    Equal(Number(0), Variable("X")),
                ),
            ),
        )

        # assembling
        target_rule = WeakConstraint(
            (
                PredLiteral("p", Variable("X"), Number(0)),
                AggrPlaceholder(1, TermTuple(Variable("X")), TermTuple(Variable("X"))),
                PredLiteral("q", Variable("X")),
                Equal(Number(0), Variable("X")),
                AggrPlaceholder(2, TermTuple(), TermTuple()),
            ),
            WeightAtLevel(Number(0), Number(1), (Number(2), Number(-1))),
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
            WeakConstraint(
                (
                    PredLiteral("p", Variable("X"), Number(0)),
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
                WeightAtLevel(Number(0), Number(1), (Number(2), Number(-1))),
            ),
        )

        # TODO: propagate


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
