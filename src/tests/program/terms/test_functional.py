import unittest

import aspy
from aspy.program.substitution import Substitution
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

        # substitute
        self.assertEqual(Functional('f', String('f'), Variable('X')).substitute(Substitution({String('f'): Number(0), Variable('X'): Number(1)})), Functional('f', String('f'), Number(1))) # NOTE: substitution is invalid
        # match
        self.assertEqual(Functional('f', Variable('X'), String('f')).match(Functional('f', Number(1), String('f'))), Substitution({Variable('X'): Number(1)}))
        self.assertEqual(Functional('f', Variable('X'), String('f')).match(Functional('f', Number(1), String('g'))), None) # ground terms don't match
        self.assertEqual(Functional('f', Variable('X'), Variable('X')).match(Functional('f', Number(1), String('f'))), None) # assignment conflict


if __name__ == "__main__":
    unittest.main()