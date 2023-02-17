import unittest

import aspy
from aspy.program.variable_table import VariableTable
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.terms import Functional, Number, Variable, String


class TestArithmetic(unittest.TestCase):
    def test_functional(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        term = Functional('f', Number(1), String('x'))
        self.assertEqual(str(term), 'f(1,"x")')
        self.assertEqual(term, Functional('f', Number(1), String('x')))
        self.assertEqual(hash(term), hash(Functional('f', Number(1), String('x'))))
        self.assertFalse(term.precedes(Functional('e', Number(1), String('x'))))
        self.assertFalse(term.precedes(Functional('f', Number(0), String('x'))))
        self.assertFalse(term.precedes(Functional('f', Number(0), String('y'))))
        self.assertTrue(term.precedes(Functional('f', Number(1), String('x'))))
        self.assertEqual(term.replace_arith(VariableTable()), term)
        self.assertTrue(term.vars() == term.vars(global_only=True) == set())
        self.assertEqual(term.safety(), SafetyTriplet())
        self.assertTrue(term.ground)

        term = Functional('f', Variable('X'))
        self.assertTrue(term.vars() == term.vars(global_only=True) == {Variable('X')})
        self.assertEqual(term.replace_arith(VariableTable()), term)
        self.assertEqual(term.safety(), SafetyTriplet({Variable('X')}))
        self.assertFalse(term.ground)
        # TODO: match
        # TODO: substitute


if __name__ == "__main__":
    unittest.main()