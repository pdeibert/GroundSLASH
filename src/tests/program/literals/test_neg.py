import unittest

import aspy
from aspy.program.variable_table import VariableTable
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.terms import Number, Variable, ArithVariable, Minus, String
from aspy.program.literals import Neg, PredicateLiteral, Equal, AggregateLiteral, AggregateCount, Guard
from aspy.program.operators import RelOp


class TestNaf(unittest.TestCase):
    def test_naf(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        # predicate literal
        literal = PredicateLiteral('p', Number(0), Variable('Y'))
        self.assertFalse(literal.neg)
        literal_ = Neg(PredicateLiteral('p', Number(0), Variable('Y')))
        self.assertTrue(literal_.neg)
        self.assertTrue(literal.name == literal_.name and literal.terms == literal_.terms)
        self.assertFalse(Neg(PredicateLiteral('p', Number(0), Variable('Y')), False).neg)
        self.assertTrue(Neg(PredicateLiteral('p', Number(0), Variable('Y')), True).neg)

        # aggregate literal
        self.assertRaises(ValueError, Neg, AggregateLiteral(AggregateCount(), tuple(), Guard(RelOp.LESS, Number(3), False)))

        # builtin literal
        self.assertRaises(ValueError, Neg, Equal(Number(0), Variable('Y')))


if __name__ == "__main__":
    unittest.main()