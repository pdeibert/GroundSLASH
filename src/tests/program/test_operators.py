import unittest

import aspy
from aspy.program.operators import AggrOp, ArithOp, RelOp


class TestSubstitution(unittest.TestCase):
    def test_relop(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        # string representation
        self.assertEqual(str(RelOp.EQUAL), "=")
        self.assertEqual(str(RelOp.UNEQUAL), "!=")
        self.assertEqual(str(RelOp.LESS), "<")
        self.assertEqual(str(RelOp.GREATER), ">")
        self.assertEqual(str(RelOp.LESS_OR_EQ), "<=")
        self.assertEqual(str(RelOp.GREATER_OR_EQ), ">=")

        # switching operand sides
        self.assertEqual(-RelOp.EQUAL, RelOp.EQUAL)  # x  = y <=> y  = x
        self.assertEqual(-RelOp.UNEQUAL, RelOp.UNEQUAL)  # x != y <-> y != x
        self.assertEqual(-RelOp.LESS, RelOp.GREATER)  # x  < y <=> y  > x
        self.assertEqual(-RelOp.GREATER, RelOp.LESS)  # x  > y <=> y  < x
        self.assertEqual(-RelOp.LESS_OR_EQ, RelOp.GREATER_OR_EQ)  # x <= y <=> y >= x
        self.assertEqual(-RelOp.GREATER_OR_EQ, RelOp.LESS_OR_EQ)  # x >= y <=> y <= x

        # equivalent negated operator
        self.assertEqual(~RelOp.EQUAL, RelOp.UNEQUAL)  # not x  = y <=> x != y
        self.assertEqual(~RelOp.UNEQUAL, RelOp.EQUAL)  # not x != y <=> x  = y
        self.assertEqual(~RelOp.LESS, RelOp.GREATER_OR_EQ)  # not x  < y <=> x >= y
        self.assertEqual(~RelOp.GREATER, RelOp.LESS_OR_EQ)  # not x  > y <=> x <= y
        self.assertEqual(~RelOp.LESS_OR_EQ, RelOp.GREATER)  # not x <= y <=> x  > y
        self.assertEqual(~RelOp.GREATER_OR_EQ, RelOp.LESS)  # not x >= y <=> x  < y

        # TODO: eval

    def test_arithop(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        # string representation
        self.assertEqual(str(ArithOp.PLUS), "+")
        self.assertEqual(str(ArithOp.MINUS), "-")
        self.assertEqual(str(ArithOp.TIMES), "*")
        self.assertEqual(str(ArithOp.DIV), "/")

    def test_aggrop(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        # string representation
        self.assertEqual(str(AggrOp.COUNT), "#count")
        self.assertEqual(str(AggrOp.SUM), "#sum")
        self.assertEqual(str(AggrOp.MAX), "#max")
        self.assertEqual(str(AggrOp.MIN), "#min")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
