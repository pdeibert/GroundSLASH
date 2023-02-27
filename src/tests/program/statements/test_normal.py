import unittest

import aspy
from aspy.program.substitution import Substitution
from aspy.program.terms import Number, Variable, String
from aspy.program.literals import Naf, Neg, PredicateLiteral, LiteralTuple, AggregateLiteral, AggregateCount, Guard
from aspy.program.operators import RelOp

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
        # hashing
        self.assertEqual(hash(ground_rule), hash(NormalFact(PredicateLiteral('p', Number(0)))))
        self.assertEqual(hash(var_rule), hash(NormalFact(PredicateLiteral('p', Variable('X')))))
        # ground
        self.assertTrue(ground_rule.ground)
        self.assertFalse(var_rule.ground)
        # safety
        self.assertTrue(ground_rule.safe)
        self.assertFalse(var_rule.safe)
        # variables
        self.assertTrue(ground_rule.vars() == ground_rule.vars(True) == set())
        self.assertTrue(var_rule.vars() == var_rule.vars(True) == {Variable('X')})
        # TODO: replace arithmetic terms

        # substitution
        rule = NormalFact(PredicateLiteral('p', Variable('X'), Number(0)))
        self.assertEqual(rule.substitute(Substitution({Variable('X'): Number(1), Number(0): String('f')})), NormalFact(PredicateLiteral('p', Number(1), Number(0)))) # NOTE: substitution is invalid
        # match
        self.assertEqual(NormalFact(PredicateLiteral('p', Variable('X'), String('f'))).match(NormalFact(PredicateLiteral('p', Number(1), String('f')))), Substitution({Variable('X'): Number(1)}))
        self.assertEqual(NormalFact(PredicateLiteral('p', Variable('X'), String('f'))).match(NormalFact(PredicateLiteral('p', Number(1), String('g')))), None) # ground terms don't match
        self.assertEqual(NormalFact(PredicateLiteral('p', Variable('X'), Variable('X'))).match(NormalFact(PredicateLiteral('p', Number(1), String('f')))), None) # assignment conflict

        # TODO: rewrite aggregates
        # TODO: assemble
        # TODO: propagate

    def test_normal_rule(self):

        ground_rule = NormalRule(PredicateLiteral('p', Number(0)), PredicateLiteral('q'))
        unsafe_var_rule = NormalRule(PredicateLiteral('p', Variable('X')), PredicateLiteral('q'))
        safe_var_rule = NormalRule(PredicateLiteral('p', Variable('X')), PredicateLiteral('q', Variable('X')))

        # string representation
        self.assertEqual(str(ground_rule), "p(0) :- q.")
        self.assertEqual(str(unsafe_var_rule), "p(X) :- q.")
        self.assertEqual(str(safe_var_rule), "p(X) :- q(X).")
        # equality
        self.assertEqual(ground_rule.head, LiteralTuple(PredicateLiteral('p', Number(0))))
        self.assertEqual(ground_rule.body, LiteralTuple(PredicateLiteral('q')))
        self.assertEqual(unsafe_var_rule.head, LiteralTuple(PredicateLiteral('p', Variable('X'))))
        self.assertEqual(unsafe_var_rule.body, LiteralTuple(PredicateLiteral('q')))
        self.assertEqual(safe_var_rule.head, LiteralTuple(PredicateLiteral('p', Variable('X'))))
        self.assertEqual(safe_var_rule.body, LiteralTuple(PredicateLiteral('q', Variable('X'))))
        # TODO: hashing
        self.assertEqual(hash(ground_rule), hash(NormalRule(PredicateLiteral('p', Number(0)), PredicateLiteral('q'))))
        self.assertEqual(hash(unsafe_var_rule), hash(NormalRule(PredicateLiteral('p', Variable('X')), PredicateLiteral('q'))))
        self.assertEqual(hash(safe_var_rule), hash(NormalRule(PredicateLiteral('p', Variable('X')), PredicateLiteral('q', Variable('X')))))
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
        self.assertTrue(NormalRule(PredicateLiteral('p', Variable('X')), AggregateLiteral(AggregateCount(), tuple(), Guard(RelOp.EQUAL, Number(1), False))).contains_aggregates)
        # variables
        self.assertTrue(ground_rule.vars() == ground_rule.vars(True) == set())
        self.assertTrue(unsafe_var_rule.vars() == unsafe_var_rule.vars(True) == {Variable('X')})
        self.assertTrue(safe_var_rule.vars() == safe_var_rule.vars(True) == {Variable('X')})
        # TODO: replace arithmetic terms

        # substitution
        rule = NormalRule(PredicateLiteral('p', Variable('X'), Number(0)), PredicateLiteral('q', Variable('X')))
        self.assertEqual(rule.substitute(Substitution({Variable('X'): Number(1), Number(0): String('f')})), NormalRule(PredicateLiteral('p', Number(1), Number(0)), PredicateLiteral('q', Number(1)))) # NOTE: substitution is invalid
        # match
        self.assertEqual(NormalRule(PredicateLiteral('p', Variable('X'), String('f')), PredicateLiteral('q', Variable('X'))).match(NormalRule(PredicateLiteral('p', Number(1), String('f')), PredicateLiteral('q', Number(1)))), Substitution({Variable('X'): Number(1)}))
        self.assertEqual(NormalRule(PredicateLiteral('p', Variable('X'), String('f')), PredicateLiteral('q', Variable('X'))).match(NormalRule(PredicateLiteral('p', Number(1), String('g')), PredicateLiteral('q', Number(1)))), None) # ground terms don't match
        self.assertEqual(NormalRule(PredicateLiteral('p', Variable('X'), String('f')), PredicateLiteral('q', Variable('X'))).match(NormalRule(PredicateLiteral('p', Number(1), String('f')), PredicateLiteral('q', Number(0)))), None) # assignment conflict
        self.assertEqual(NormalRule(PredicateLiteral('p', Number(0), String('f')), PredicateLiteral('q', Number(1)), PredicateLiteral('u', Number(0))).match(NormalRule(PredicateLiteral('p', Number(0), String('f')), PredicateLiteral('u', Number(0)), PredicateLiteral('q', Number(1)))), None) # different order of body literals

        # TODO: rewrite aggregates
        # TODO: assemble
        # TODO: propagate


if __name__ == "__main__":
    unittest.main()