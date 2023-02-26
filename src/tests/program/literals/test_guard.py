import unittest

import aspy
from aspy.program.substitution import Substitution
from aspy.program.variable_table import VariableTable
from aspy.program.terms import Variable, Minus, ArithVariable
from aspy.program.literals import Guard
from aspy.program.operators import RelOp


class TestGuard(unittest.TestCase):
    def test_guard(self):
        # TODO
        self.assertEqual(Guard(RelOp.EQUAL, Minus(Variable('X')), True).replace_arith(VariableTable()), Guard(RelOp.EQUAL, ArithVariable(0, Minus(Variable('X'))), True))


if __name__ == "__main__":
    unittest.main()