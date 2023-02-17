import unittest

import aspy
from aspy.program.substitution import Substitution
from aspy.program.terms import Number, Variable, String
from aspy.program.literals import PredicateLiteral, LiteralTuple

from aspy.program.statements import NormalFact, NormalRule


class TestNormal(unittest.TestCase):
    def test_normal_fact(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        rule = NormalFact(PredicateLiteral('p', Number(0)))
        self.assertEqual(str(rule), "p(0).")
        self.assertEqual(rule.head, LiteralTuple(PredicateLiteral('p', Number(0))))
        self.assertEqual(rule.body, LiteralTuple())
        self.assertTrue(rule.vars() == rule.vars(True) == set())
        self.assertTrue(rule.safe)
        self.assertTrue(rule.ground)

        rule = NormalFact(PredicateLiteral('p', Variable('X')))
        self.assertEqual(str(rule), "p(X).")
        self.assertEqual(rule.head, LiteralTuple(PredicateLiteral('p', Variable('X'))))
        self.assertEqual(rule.body, LiteralTuple())
        self.assertTrue(rule.vars() == rule.vars(True) == {Variable('X')})
        self.assertFalse(rule.safe)
        self.assertFalse(rule.ground)

        # substitution
        rule = NormalFact(PredicateLiteral('p', Variable('X'), Number(0)))
        self.assertEqual(rule.substitute(Substitution({Variable('X'): Number(1), Number(0): String('f')})), NormalFact(PredicateLiteral('p', Number(1), Number(0)))) # NOTE: substitution is invalid
        # TODO: match

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
        # TODO: match


if __name__ == "__main__":
    unittest.main()