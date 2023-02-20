import unittest

import aspy
from aspy.program.substitution import Substitution
from aspy.program.terms import Number, Variable, String
from aspy.program.literals import Naf, Neg, PredicateLiteral, LiteralTuple, BuiltinLiteral

from aspy.program.statements import NormalFact, NormalRule


class TestNormal(unittest.TestCase):
    def test_normal_fact(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        ground_rule = NormalFact(PredicateLiteral('p', Number(0)))
        var_rule = NormalFact(PredicateLiteral('p', Variable('X')))

        # string representation
        self.assertEqual(str(ground_rule), "p(0).")
        self.assertEqual(str(var_rule), "p(X).")
        # equality
        self.assertEqual(ground_rule.head, LiteralTuple(PredicateLiteral('p', Number(0))))
        self.assertEqual(ground_rule.body, LiteralTuple())
        self.assertEqual(var_rule.head, LiteralTuple(PredicateLiteral('p', Variable('X'))))
        self.assertEqual(var_rule.body, LiteralTuple())
        # ground
        self.assertTrue(ground_rule.ground)
        self.assertFalse(var_rule.ground)
        # safety
        self.assertTrue(ground_rule.safe)
        self.assertFalse(var_rule.safe)
        # variables
        self.assertTrue(ground_rule.vars() == ground_rule.vars(True) == set())
        self.assertTrue(var_rule.vars() == var_rule.vars(True) == {Variable('X')})

        # substitution
        rule = NormalFact(PredicateLiteral('p', Variable('X'), Number(0)))
        self.assertEqual(rule.substitute(Substitution({Variable('X'): Number(1), Number(0): String('f')})), NormalFact(PredicateLiteral('p', Number(1), Number(0)))) # NOTE: substitution is invalid
        # match
        self.assertEqual(NormalFact(PredicateLiteral('p', Variable('X'), String('f'))).match(NormalFact(PredicateLiteral('p', Number(1), String('f')))), Substitution({Variable('X'): Number(1)}))
        self.assertEqual(NormalFact(PredicateLiteral('p', Variable('X'), String('f'))).match(NormalFact(PredicateLiteral('p', Number(1), String('g')))), None) # ground terms don't match
        self.assertEqual(NormalFact(PredicateLiteral('p', Variable('X'), Variable('X'))).match(NormalFact(PredicateLiteral('p', Number(1), String('f')))), None) # assignment conflict

    def test_normal_rule(self):

        rule = NormalRule(PredicateLiteral('p', Number(0)), PredicateLiteral('q'))
        self.assertEqual(str(rule), "p(0) :- q.")
        self.assertEqual(rule.head, LiteralTuple(PredicateLiteral('p', Number(0))))
        self.assertEqual(rule.body, LiteralTuple(PredicateLiteral('q')))
        self.assertTrue(rule.vars() == rule.vars(True) == set())
        self.assertTrue(rule.safe)
        self.assertTrue(rule.ground)

        rule = NormalRule(PredicateLiteral('p', Variable('X')), PredicateLiteral('q'))
        self.assertEqual(str(rule), "p(X) :- q.")
        self.assertEqual(rule.head, LiteralTuple(PredicateLiteral('p', Variable('X'))))
        self.assertEqual(rule.body, LiteralTuple(PredicateLiteral('q')))
        self.assertTrue(rule.vars() == rule.vars(True) == {Variable('X')})
        self.assertFalse(rule.safe)
        self.assertFalse(rule.ground)

        rule = NormalRule(PredicateLiteral('p', Variable('X')), PredicateLiteral('q', Variable('X')))
        self.assertEqual(str(rule), "p(X) :- q(X).")
        self.assertEqual(rule.head, LiteralTuple(PredicateLiteral('p', Variable('X'))))
        self.assertEqual(rule.body, LiteralTuple(PredicateLiteral('q', Variable('X'))))
        self.assertTrue(rule.vars() == rule.vars(True) == {Variable('X')})
        self.assertTrue(rule.safe)
        self.assertFalse(rule.ground)

        # substitution
        rule = NormalRule(PredicateLiteral('p', Variable('X'), Number(0)), PredicateLiteral('q', Variable('X')))
        self.assertEqual(rule.substitute(Substitution({Variable('X'): Number(1), Number(0): String('f')})), NormalRule(PredicateLiteral('p', Number(1), Number(0)), PredicateLiteral('q', Number(1)))) # NOTE: substitution is invalid
        # match
        self.assertEqual(NormalRule(PredicateLiteral('p', Variable('X'), String('f')), PredicateLiteral('q', Variable('X'))).match(NormalRule(PredicateLiteral('p', Number(1), String('f')), PredicateLiteral('q', Number(1)))), Substitution({Variable('X'): Number(1)}))
        self.assertEqual(NormalRule(PredicateLiteral('p', Variable('X'), String('f')), PredicateLiteral('q', Variable('X'))).match(NormalRule(PredicateLiteral('p', Number(1), String('g')), PredicateLiteral('q', Number(1)))), None) # ground terms don't match
        self.assertEqual(NormalRule(PredicateLiteral('p', Variable('X'), String('f')), PredicateLiteral('q', Variable('X'))).match(NormalRule(PredicateLiteral('p', Number(1), String('f')), PredicateLiteral('q', Number(0)))), None) # assignment conflict
        self.assertEqual(NormalRule(PredicateLiteral('p', Number(0), String('f')), PredicateLiteral('q', Number(1)), PredicateLiteral('u', Number(0))).match(NormalRule(PredicateLiteral('p', Number(0), String('f')), PredicateLiteral('u', Number(0)), PredicateLiteral('q', Number(1)))), None) # different order of body literals


if __name__ == "__main__":
    unittest.main()