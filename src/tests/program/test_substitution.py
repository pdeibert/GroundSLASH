import unittest

import aspy
from aspy.program.substitution import Substitution, AssignmentError
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.substitution import Substitution
from aspy.program.terms import Infimum, Supremum, Variable, AnonVariable, Number, SymbolicConstant, String, TermTuple


class TestSubstitution(unittest.TestCase):
    def test_substitution(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        # empty substitution
        subst = Substitution()
        self.assertEqual(subst, Substitution())
        self.assertEqual(hash(subst), hash(Substitution()))
        self.assertEqual(subst[Variable('X')], Variable('X')) # map non-specified variables to themselves

        # non-empty substitution
        subst = Substitution({Variable('X'): Number(0), Variable('Y'): String('str')})
        self.assertEqual(subst, Substitution({Variable('X'): Number(0), Variable('Y'): String('str')}))
        self.assertEqual(hash(subst), hash(Substitution({Variable('X'): Number(0), Variable('Y'): String('str')})))
        self.assertTrue(subst[Variable('X')], Number(0))
        self.assertTrue(subst[Variable('Y')], String('str'))
        self.assertEqual(subst[Variable('X')], Number(0))
        self.assertEqual(subst[Variable('Z')], Variable('Z')) # map non-specified variables to themselves

        # adding substitutions
        subst = Substitution({Variable('X'): Number(0), Variable('Y'): String('str')}) + Substitution({Variable('Y'): String('str'), Variable('Z'): Number(3)})
        self.assertEqual(subst, Substitution({Variable('X'): Number(0), Variable('Y'): String('str'), Variable('Z'): Number(3)}))
        with self.assertRaises(AssignmentError):
            Substitution({Variable('X'): Number(0), Variable('Y'): String('str')}) + Substitution({Variable('Y'): Number(3), Variable('Z'): Number(3)})


if __name__ == "__main__":
    unittest.main()