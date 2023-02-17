import unittest

import aspy
from aspy.program.terms import Number, Variable
from aspy.program.literals import PredicateLiteral, LiteralTuple

from aspy.program.statements import DisjunctiveFact, DisjunctiveRule


class TestDisjunctive(unittest.TestCase):
    def test_disjunctive_fact(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        # note enough literals
        self.assertRaises(ValueError, DisjunctiveFact, PredicateLiteral('p', Number(0)))

        rule = DisjunctiveFact(PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1)))
        self.assertEqual(str(rule), "p(0)|p(1).")
        self.assertEqual(rule.head, LiteralTuple(PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))))
        self.assertEqual(rule.body, LiteralTuple())
        self.assertTrue(rule.vars() == rule.vars(True) == set())
        self.assertTrue(rule.safe)
        self.assertTrue(rule.ground)
        rule = DisjunctiveFact(PredicateLiteral('p', Variable('X')), PredicateLiteral('p', Number(1)))
        self.assertEqual(str(rule), "p(X)|p(1).")
        self.assertEqual(rule.head, LiteralTuple(PredicateLiteral('p', Variable('X')), PredicateLiteral('p', Number(1))))
        self.assertEqual(rule.body, LiteralTuple())
        self.assertTrue(rule.vars() == rule.vars(True) == {Variable('X')})
        self.assertFalse(rule.safe)
        self.assertFalse(rule.ground)
        # TODO: match
        # TODO: substitution

    def test_disjunctive_rule(self):

        rule = DisjunctiveRule( (PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))), PredicateLiteral('q'))
        self.assertEqual(str(rule), "p(0)|p(1) :- q.")
        self.assertEqual(rule.head, LiteralTuple(PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))))
        self.assertEqual(rule.body, LiteralTuple(PredicateLiteral('q')))
        self.assertTrue(rule.vars() == rule.vars(True) == set())
        self.assertTrue(rule.safe)
        self.assertTrue(rule.ground)
        rule = DisjunctiveRule( (PredicateLiteral('p', Variable('X')), PredicateLiteral('p', Number(1))), PredicateLiteral('q'))
        self.assertEqual(str(rule), "p(X)|p(1) :- q.")
        self.assertEqual(rule.head, LiteralTuple(PredicateLiteral('p', Variable('X')), PredicateLiteral('p', Number(1))))
        self.assertEqual(rule.body, LiteralTuple(PredicateLiteral('q')))
        self.assertTrue(rule.vars() == rule.vars(True) == {Variable('X')})
        self.assertFalse(rule.safe)
        self.assertFalse(rule.ground)
        rule = DisjunctiveRule( (PredicateLiteral('p', Variable('X')), PredicateLiteral('p', Number(1))), PredicateLiteral('q', Variable('X')))
        self.assertEqual(str(rule), "p(X)|p(1) :- q(X).")
        self.assertEqual(rule.head, LiteralTuple(PredicateLiteral('p', Variable('X')), PredicateLiteral('p', Number(1))))
        self.assertEqual(rule.body, LiteralTuple(PredicateLiteral('q', Variable('X'))))
        self.assertTrue(rule.vars() == rule.vars(True) == {Variable('X')})
        self.assertTrue(rule.safe)
        self.assertFalse(rule.ground)
        # TODO: match
        # TODO: substitution


if __name__ == "__main__":
    unittest.main()