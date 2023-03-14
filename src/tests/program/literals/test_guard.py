import unittest

import aspy
from aspy.program.literals import Guard
from aspy.program.operators import RelOp
from aspy.program.terms import ArithVariable, Minus, Number, Variable
from aspy.program.variable_table import VariableTable


class TestGuard(unittest.TestCase):
    def test_guard(self):
        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        rguard = Guard(RelOp.GREATER, Number(3), True)
        lguard = Guard(RelOp.LESS, Number(3), False)

        var_guard = Guard(RelOp.EQUAL, Minus(Variable("X")), True)

        # string representation
        self.assertEqual(str(rguard), "> 3")
        self.assertEqual(str(lguard), "3 <")
        # equality
        self.assertEqual(rguard, Guard(RelOp.GREATER, Number(3), True))
        self.assertEqual(lguard, Guard(RelOp.LESS, Number(3), False))
        # hashing
        self.assertEqual(hash(rguard), hash(Guard(RelOp.GREATER, Number(3), True)))
        self.assertEqual(hash(lguard), hash(Guard(RelOp.LESS, Number(3), False)))
        # to left
        self.assertEqual(lguard.to_left(), lguard)
        self.assertEqual(rguard.to_left(), lguard)
        # to right
        self.assertEqual(rguard.to_right(), rguard)
        self.assertEqual(lguard.to_right(), rguard)
        # ground
        self.assertTrue(rguard.ground == lguard.ground == True)  # noqa
        self.assertFalse(var_guard.ground)
        # variables
        self.assertTrue(var_guard.vars() == var_guard.global_vars() == {Variable("X")})
        # replace arithmetic terms
        self.assertEqual(
            var_guard.replace_arith(VariableTable()),
            Guard(RelOp.EQUAL, ArithVariable(0, Minus(Variable("X"))), True),
        )
        # TODO: substitute (see aggregate tests)
        # TODO: match (see aggregate tests)
        # TODO: safety characterization (see aggregate tests)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
