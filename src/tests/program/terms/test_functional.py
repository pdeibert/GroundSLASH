import unittest

import aspy
from aspy.program.substitution import Substitution
from aspy.program.variable_table import VariableTable
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.terms import Functional, Number, Variable, String


class TestFunctional(unittest.TestCase):
    def test_functional(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        # invalid initialization
        self.assertRaises(ValueError, Functional, 'F')
        # valid initialization
        ground_term = Functional('f', Number(1), String('x'))
        var_term = Functional('f', Variable('X'))
        # string representation
        self.assertEqual(str(ground_term), 'f(1,"x")')
        # equality
        self.assertEqual(ground_term, Functional('f', Number(1), String('x')))
        # hashing
        self.assertEqual(hash(ground_term), hash(Functional('f', Number(1), String('x'))))
        # arity
        self.assertEqual(ground_term.arity, 2)
        # total order for terms
        self.assertFalse(ground_term.precedes(Functional('e', Number(1), String('x'))))
        self.assertFalse(ground_term.precedes(Functional('f', Number(0), String('x'))))
        self.assertFalse(ground_term.precedes(Functional('f', Number(0), String('y'))))
        self.assertTrue(ground_term.precedes(Functional('f', Number(1), String('x'))))
        # ground
        self.assertTrue(ground_term.ground)
        self.assertFalse(var_term.ground)
        # variables
        self.assertTrue(ground_term.vars() == ground_term.vars(global_only=True) == set())
        self.assertTrue(var_term.vars() == var_term.vars(global_only=True) == {Variable('X')})
        # replace arithmetic terms
        self.assertEqual(ground_term.replace_arith(VariableTable()), ground_term)
        self.assertEqual(var_term.replace_arith(VariableTable()), var_term)
        # safety characterizatin
        self.assertEqual(ground_term.safety(), SafetyTriplet())
        self.assertEqual(var_term.safety(), SafetyTriplet({Variable('X')}))

        # substitute
        self.assertEqual(Functional('f', String('f'), Variable('X')).substitute(Substitution({String('f'): Number(0), Variable('X'): Number(1)})), Functional('f', String('f'), Number(1))) # NOTE: substitution is invalid
        # match
        self.assertEqual(Functional('f', Variable('X'), String('f')).match(Functional('f', Number(1), String('f'))), Substitution({Variable('X'): Number(1)}))
        self.assertEqual(Functional('f', Variable('X'), String('f')).match(Functional('f', Number(1), String('g'))), None) # ground terms don't match
        self.assertEqual(Functional('f', Variable('X'), Variable('X')).match(Functional('f', Number(1), String('f'))), None) # assignment conflict


if __name__ == "__main__":
    unittest.main()