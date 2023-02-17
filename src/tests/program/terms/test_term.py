import unittest

import aspy
from aspy.program.variable_table import VariableTable
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.substitution import Substitution
from aspy.program.terms import Infimum, Supremum, Variable, AnonVariable, Number, SymbolicConstant, String, TermTuple


class TestTerm(unittest.TestCase):
    def test_infimum(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        term = Infimum()
        self.assertEqual(str(term), "#inf")
        self.assertEqual(term, Infimum())
        self.assertEqual(hash(term), hash(Infimum()))
        self.assertTrue(term.precedes(Number(0)))
        self.assertTrue(term.vars() == term.vars(global_only=True) == set())
        self.assertEqual(term.replace_arith(VariableTable()), term)
        self.assertEqual(term.safety(), SafetyTriplet())
        self.assertTrue(term.ground)

        # substitute
        self.assertEqual(Infimum().substitute(Substitution({Infimum(): Supremum()})), Infimum()) # NOTE: substitution is invalid
        # TODO: match

    def test_supremum(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        term = Supremum()
        self.assertEqual(str(term), "#sup")
        self.assertEqual(term, Supremum())
        self.assertEqual(hash(term), hash(Supremum()))
        self.assertTrue(term.precedes(Supremum()))
        self.assertTrue(term.vars() == term.vars(global_only=True) == set())
        self.assertEqual(term.replace_arith(VariableTable()), term)
        self.assertEqual(term.safety(), SafetyTriplet())
        self.assertTrue(term.ground)

        # substitute
        self.assertEqual(Supremum().substitute(Substitution({Supremum(): Infimum()})), Supremum()) # NOTE: substitution is invalid
        # TODO: match
        
    def test_variable(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        self.assertRaises(ValueError, Variable, 'x')
        term = Variable('X')
        self.assertEqual(str(term), "X")
        self.assertEqual(term, Variable('X'))
        self.assertEqual(hash(term), hash(Variable('X')))
        self.assertRaises(Exception, term.precedes, term)
        self.assertTrue(term.vars() == term.vars(global_only=True) == {term})
        self.assertEqual(term.replace_arith(VariableTable()), term)
        self.assertEqual(term.safety(), SafetyTriplet({term}))
        self.assertFalse(term.ground)

        self.assertEqual(term.simplify(), term)
        # substitute
        self.assertEqual(Variable('X').substitute(Substitution({Variable('Y'): Number(0)})), Variable('X'))
        self.assertEqual(Variable('X').substitute(Substitution({Variable('X'): Number(0)})), Number(0))
        # TODO: match

    def test_anon_variable(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        self.assertRaises(ValueError, AnonVariable, -1)
        term = AnonVariable(0)
        self.assertEqual(str(term), "_0")
        self.assertEqual(term, AnonVariable(0))
        self.assertEqual(hash(term), hash(AnonVariable(0)))
        self.assertRaises(Exception, term.precedes, term)
        self.assertTrue(term.vars() == term.vars(global_only=True) == {term})
        self.assertEqual(term.replace_arith(VariableTable()), term)
        self.assertEqual(term.safety(), SafetyTriplet({term}))
        self.assertFalse(term.ground)

        self.assertEqual(term.simplify(), term)
        # substitute
        self.assertEqual(AnonVariable(0).substitute(Substitution({AnonVariable(1): Number(0)})), AnonVariable(0))
        self.assertEqual(AnonVariable(0).substitute(Substitution({AnonVariable(0): Number(0)})), Number(0))
        # TODO: match

    def test_number(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        term = Number(5)
        self.assertEqual(str(term), "5")
        self.assertEqual(term, Number(5))
        self.assertEqual(hash(term), hash(Number(5)))
        self.assertFalse(term.precedes(Number(4)))
        self.assertTrue(term.precedes(Number(5)))
        self.assertTrue(term.vars() == term.vars(global_only=True) == set())
        self.assertEqual(term.replace_arith(VariableTable()), term)
        self.assertEqual(term.safety(), SafetyTriplet())
        self.assertTrue(term.ground)

        self.assertEqual(term  + Number(2), Number(7))
        self.assertEqual(term  - Number(2), Number(3))
        self.assertEqual(term  * Number(2), Number(10))
        self.assertEqual(term // Number(2), Number(2))

        self.assertEqual(term.simplify(), term)
        self.assertEqual(term.eval(), 5)
        # substitute
        self.assertEqual(Number(0).substitute(Substitution({Number(0): Number(1)})), Number(0)) # NOTE: substitution is invalid
        # TODO: match

    def test_symbolic_constant(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        term = SymbolicConstant('b')
        self.assertEqual(str(term), 'b')
        self.assertEqual(term, SymbolicConstant('b'))
        self.assertEqual(hash(term), hash(SymbolicConstant('b')))
        self.assertFalse(term.precedes(SymbolicConstant('a')))
        self.assertTrue(term.precedes(SymbolicConstant('b')))
        self.assertTrue(term.vars() == term.vars(global_only=True) == set())
        self.assertEqual(term.replace_arith(VariableTable()), term)
        self.assertEqual(term.safety(), SafetyTriplet())
        self.assertTrue(term.ground)
        
        # substitute
        self.assertEqual(SymbolicConstant('f').substitute(Substitution({SymbolicConstant('f'): Number(0)})), SymbolicConstant('f')) # NOTE: substitution is invalid
        # TODO: match

    def test_string(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        term = String('!?$#b')
        self.assertEqual(str(term), '"!?$#b"')
        self.assertEqual(term, String('!?$#b'))
        self.assertEqual(hash(term), hash(String('!?$#b')))
        self.assertFalse(term.precedes(String('!?$#a')))
        self.assertTrue(term.precedes(String('!?$#b')))
        self.assertTrue(term.vars() == term.vars(global_only=True) == set())
        self.assertEqual(term.replace_arith(VariableTable()), term)
        self.assertEqual(term.safety(), SafetyTriplet())
        self.assertTrue(term.ground)

        # substitute
        self.assertEqual(String('f').substitute(Substitution({String('f'): Number(0)})), String('f')) # NOTE: substitution is invalid
        # TODO: match

    def test_term_tuple(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        terms = TermTuple(Number(0), Variable('X'))
        self.assertEqual(len(terms), 2)
        self.assertEqual(terms[0], Number(0))
        self.assertEqual(terms[1], Variable('X'))
        self.assertTrue(terms == TermTuple(Number(0), Variable('X')))
        self.assertEqual(hash(terms), hash(TermTuple(Number(0), Variable('X'))))
        self.assertTrue(terms.vars() == terms.vars(global_only=True) == {Variable('X')})
        self.assertEqual(terms.replace_arith(VariableTable()), terms)
        self.assertEqual(terms.safety(), (terms[0].safety(), terms[1].safety()))
        self.assertFalse(terms.ground)

        # substitute
        self.assertEqual(TermTuple(String('f'), Variable('X')).substitute(Substitution({String('f'): Number(0), Variable('X'): Number(1)})), TermTuple(String('f'), Number(1))) # NOTE: substitution is invalid
        # TODO: match

        self.assertEqual(terms + TermTuple(String("")), TermTuple(Number(0), Variable('X'), String("")))
        # TODO: iter


if __name__ == "__main__":
    unittest.main()