import unittest

import aspy
from aspy.program.literals import Guard
from aspy.program.operators import RelOp
from aspy.program.terms import ArithVariable, Minus, Variable
from aspy.program.variable_table import VariableTable


class TestGuard(unittest.TestCase):
    def test_guard(self):
        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        # TODO
        self.assertEqual(
            Guard(RelOp.EQUAL, Minus(Variable("X")), True).replace_arith(VariableTable()),
            Guard(RelOp.EQUAL, ArithVariable(0, Minus(Variable("X"))), True),
        )


if __name__ == "__main__":
    unittest.main()
