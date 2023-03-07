import unittest

import aspy
from aspy.program.literals import (
    AggregateCount,
    AggregateLiteral,
    Equal,
    Guard,
    Naf,
    PredicateLiteral,
)
from aspy.program.operators import RelOp
from aspy.program.terms import Number, Variable


class TestNaf(unittest.TestCase):
    def test_naf(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        # predicate literal
        literal = PredicateLiteral("p", Number(0), Variable("Y"))
        self.assertFalse(literal.naf)
        literal_ = Naf(PredicateLiteral("p", Number(0), Variable("Y")))
        self.assertTrue(literal_.naf)
        self.assertTrue(
            literal.name == literal_.name and literal.terms == literal_.terms
        )
        self.assertFalse(
            Naf(PredicateLiteral("p", Number(0), Variable("Y")), False).naf
        )
        self.assertTrue(Naf(PredicateLiteral("p", Number(0), Variable("Y")), True).naf)

        # aggregate literal
        literal = AggregateLiteral(
            AggregateCount(), tuple(), Guard(RelOp.LESS, Number(3), False)
        )
        self.assertFalse(literal.naf)
        literal_ = Naf(
            AggregateLiteral(
                AggregateCount(), tuple(), Guard(RelOp.LESS, Number(3), False)
            )
        )
        self.assertTrue(literal_.naf)
        self.assertTrue(
            literal.func == literal_.func and literal.guards == literal_.guards
        )
        self.assertFalse(
            Naf(
                AggregateLiteral(
                    AggregateCount(), tuple(), Guard(RelOp.LESS, Number(3), False)
                ),
                False,
            ).naf
        )
        self.assertTrue(
            Naf(
                AggregateLiteral(
                    AggregateCount(), tuple(), Guard(RelOp.LESS, Number(3), False)
                ),
                True,
            ).naf
        )

        # builtin literal
        self.assertRaises(ValueError, Naf, Equal(Number(0), Variable("Y")))


if __name__ == "__main__":
    unittest.main()
