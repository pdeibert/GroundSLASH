import unittest

import aspy
from aspy.program.literals import (
    AggregateElement,
    EpsLiteral,
    EtaLiteral,
    GreaterEqual,
    Guard,
    LessEqual,
    LiteralTuple,
    PredicateLiteral,
)
from aspy.program.operators import RelOp
from aspy.program.statements import EpsRule, EtaRule
from aspy.program.substitution import Substitution
from aspy.program.symbol_table import SpecialChar
from aspy.program.terms import Number, TermTuple, Variable


class TestSpecial(unittest.TestCase):
    def test_eps_rule(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        # aggr_id: int, global_vars: TermTuple, base_value: "Term", lguard: Optional["Guard"], rguard: Optional["Guard"], non_aggr_literals: "LiteralTuple") -> None:
        global_vars = TermTuple(Variable("X"), Variable("Y"))
        base_value = Number(0)

        ground_guards = (Guard(RelOp.GREATER_OR_EQ, Number(-1), False), Guard(RelOp.LESS_OR_EQ, Number(10), True))
        ground_guard_literals = LiteralTuple(GreaterEqual(Number(-1), base_value), LessEqual(base_value, Number(10)))
        ground_eps_literal = EpsLiteral(1, global_vars, TermTuple(Number(10), Number(3)))
        ground_rule = EpsRule(
            ground_eps_literal,
            *ground_guards,
            ground_guard_literals + LiteralTuple(PredicateLiteral("p", Number(2), Number(3))),
        )

        var_guards = (Guard(RelOp.GREATER_OR_EQ, Number(-1), False), Guard(RelOp.LESS_OR_EQ, Variable("X"), True))
        var_guard_literals = LiteralTuple(GreaterEqual(Number(-1), base_value), LessEqual(base_value, Variable("X")))
        var_eps_literal = EpsLiteral(1, global_vars, global_vars)
        var_rule = EpsRule(
            var_eps_literal,
            *var_guards,
            var_guard_literals + LiteralTuple(PredicateLiteral("p", Number(2), Variable("Y"))),
        )

        # invalid initialization
        self.assertRaises(
            ValueError,
            EpsRule.from_scratch,
            1,
            {global_vars},
            *ground_guards,
            base_value,
            LiteralTuple(PredicateLiteral("p", Number(2), Number(3))),
        )  # non-tuple for 'global_vars'
        self.assertRaises(
            ValueError,
            EpsRule.from_scratch,
            1,
            global_vars,
            Guard(RelOp.GREATER_OR_EQ, Number(-1), False),
            Guard(RelOp.LESS_OR_EQ, Number(10), False),
            base_value,
            LiteralTuple(PredicateLiteral("p", Number(2), Number(3))),
        )  # two left guards
        # correct initialization
        self.assertTrue(ground_rule.aggr_id == var_rule.aggr_id == 1)
        # string representation
        self.assertEqual(str(ground_rule), f"{SpecialChar.EPS.value}{1}(10,3) :- -1>=0, 0<=10, p(2,3).")
        self.assertEqual(str(var_rule), f"{SpecialChar.EPS.value}{1}(X,Y) :- -1>=0, 0<=X, p(2,Y).")
        # equality
        self.assertEqual(len(ground_rule.body), 3)
        self.assertEqual(
            ground_rule.body[0], GreaterEqual(Number(-1), Number(0))
        )  # NOTE: order of operands in built-in terms
        self.assertEqual(
            ground_rule.body[1], LessEqual(Number(0), Number(10))
        )  # NOTE: order of operands in built-in terms
        self.assertEqual(ground_rule.body[2], PredicateLiteral("p", Number(2), Number(3)))
        self.assertEqual(len(var_rule.body), 3)
        self.assertEqual(
            var_rule.body[0], GreaterEqual(Number(-1), Number(0))
        )  # NOTE: order of operands in built-in terms
        self.assertEqual(
            var_rule.body[1], LessEqual(Number(0), Variable("X"))
        )  # NOTE: order of operands in built-in terms
        self.assertEqual(var_rule.body[2], PredicateLiteral("p", Number(2), Variable("Y")))
        self.assertEqual(ground_rule.head, LiteralTuple(ground_eps_literal))
        self.assertEqual(
            ground_rule.body, ground_guard_literals + LiteralTuple(PredicateLiteral("p", Number(2), Number(3)))
        )
        self.assertEqual(var_rule.head, LiteralTuple(var_eps_literal))
        self.assertEqual(
            var_rule.body, var_guard_literals + LiteralTuple(PredicateLiteral("p", Number(2), Variable("Y")))
        )
        # hashing
        self.assertEqual(
            hash(ground_rule),
            hash(
                EpsRule(
                    ground_eps_literal,
                    *ground_guards,
                    ground_guard_literals + LiteralTuple(PredicateLiteral("p", Number(2), Number(3))),
                )
            ),
        )
        self.assertEqual(
            hash(var_rule),
            hash(
                EpsRule(
                    var_eps_literal,
                    *var_guards,
                    var_guard_literals + LiteralTuple(PredicateLiteral("p", Number(2), Variable("Y"))),
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
        self.assertTrue(ground_rule.vars() == ground_rule.vars(True) == set())
        self.assertTrue(var_rule.vars() == var_rule.vars(True) == set(global_vars))
        # TODO: replace arithmetic terms
        # TODO: gather variable assignement

        # substitution
        self.assertEqual(
            var_rule.substitute(Substitution({Variable("X"): Number(10), Variable("Y"): Number(3)})), ground_rule
        )
        # match
        # self.assertEqual(var_rule.match(ground_rule), Substitution({Variable('X'): Number(10), Variable('Y'): Number(3)}))
        # TODO: ground terms don't match
        # TODO: assignment conflict

    def test_eta_rule(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        local_vars = TermTuple(Variable("L"))
        global_vars = TermTuple(Variable("X"), Variable("Y"))
        element = AggregateElement(TermTuple(Variable("L")), LiteralTuple(PredicateLiteral("p", Variable("L"))))

        ground_eta_literal = EtaLiteral(1, 3, local_vars, global_vars, TermTuple(Number(5), Number(10), Number(3)))
        ground_rule = EtaRule(
            ground_eta_literal,
            element,
            LiteralTuple(PredicateLiteral("p", Number(5)), PredicateLiteral("p", Number(2), Number(3))),
        )

        var_eta_literal = EtaLiteral(1, 3, local_vars, global_vars, local_vars + global_vars)
        var_rule = EtaRule(
            var_eta_literal, element, element.literals + LiteralTuple(PredicateLiteral("p", Number(2), Variable("Y")))
        )

        # correct initialization
        self.assertTrue(ground_rule.aggr_id == var_rule.aggr_id == 1)
        self.assertTrue(ground_rule.element_id == var_rule.element_id == 3)
        self.assertTrue(ground_rule.element == var_rule.element == element)
        # string representation
        self.assertEqual(str(ground_rule), f"{SpecialChar.ETA.value}{1}_{3}(5,10,3) :- p(5), p(2,3).")
        self.assertEqual(str(var_rule), f"{SpecialChar.ETA.value}{1}_{3}(L,X,Y) :- p(L), p(2,Y).")
        # equality
        self.assertEqual(len(ground_rule.body), 2)
        self.assertEqual(ground_rule.body[0], PredicateLiteral("p", Number(5)))
        self.assertEqual(ground_rule.body[1], PredicateLiteral("p", Number(2), Number(3)))
        self.assertEqual(len(var_rule.body), 2)
        self.assertEqual(var_rule.body[0], PredicateLiteral("p", Variable("L")))
        self.assertEqual(var_rule.body[1], PredicateLiteral("p", Number(2), Variable("Y")))
        # hashing
        self.assertEqual(
            hash(ground_rule),
            hash(
                EtaRule(
                    ground_eta_literal,
                    element,
                    LiteralTuple(PredicateLiteral("p", Number(5)), PredicateLiteral("p", Number(2), Number(3))),
                )
            ),
        )
        self.assertEqual(
            hash(var_rule),
            hash(
                EtaRule(
                    var_eta_literal,
                    element,
                    element.literals + LiteralTuple(PredicateLiteral("p", Number(2), Variable("Y"))),
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
        self.assertTrue(ground_rule.vars() == ground_rule.vars(True) == set())
        self.assertTrue(var_rule.vars() == var_rule.vars(True) == set(global_vars + local_vars))
        # TODO: replace arithmetic terms
        # TODO: gather variable assignement

        # substitution
        self.assertEqual(
            var_rule.substitute(
                Substitution({Variable("L"): Number(5), Variable("X"): Number(10), Variable("Y"): Number(3)})
            ),
            ground_rule,
        )
        # match
        # self.assertEqual(var_rule.match(ground_rule), Substitution({Variable('L'): Number(5), Variable('X'): Number(10), Variable('Y'): Number(3)}))
        # TODO: ground terms don't match
        # TODO: assignment conflict


if __name__ == "__main__":
    unittest.main()
