import unittest

import aspy
from aspy.program.variable_table import VariableTable
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.terms import Number, Variable, ArithVariable, Minus, String
from aspy.program.literals import Naf, PredicateLiteral, Equal, AggregateLiteral, AggregateCount
from aspy.program.operators import RelOp


class TestNaf(unittest.TestCase):
    def test_naf(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        # predicate literal
        literal = PredicateLiteral('p', Number(0), Variable('Y'))
        self.assertFalse(literal.naf)
        literal_ = Naf(PredicateLiteral('p', Number(0), Variable('Y')))
        self.assertTrue(literal_.naf)
        self.assertTrue(literal.name == literal_.name and literal.terms == literal_.terms)
        self.assertFalse(Naf(PredicateLiteral('p', Number(0), Variable('Y')), False).naf)
        self.assertTrue(Naf(PredicateLiteral('p', Number(0), Variable('Y')), True).naf)

        # aggregate literal
        literal = AggregateLiteral(AggregateCount(), (RelOp.LESS, Number(3)))
        self.assertFalse(literal.naf)
        literal_ = Naf(AggregateLiteral(AggregateCount(), (RelOp.LESS, Number(3))))
        self.assertTrue(literal_.naf)
        self.assertTrue(literal.func == literal_.func and literal.lcomp == literal_.lcomp and literal.rcomp == literal_.rcomp)
        self.assertFalse(Naf(AggregateLiteral(AggregateCount(), (RelOp.LESS, Number(3))), False).naf)
        self.assertTrue(Naf(AggregateLiteral(AggregateCount(), (RelOp.LESS, Number(3))), True).naf)

        # builtin literal
        self.assertRaises(ValueError, Naf, Equal(Number(0), Variable('Y')))


if __name__ == "__main__":
    unittest.main()