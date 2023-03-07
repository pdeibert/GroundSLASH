import unittest

import aspy
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.substitution import Substitution
from aspy.program.terms import (
    AnonVariable,
    ArithVariable,
    Infimum,
    Minus,
    Number,
    String,
    Supremum,
    SymbolicConstant,
    TermTuple,
    Variable,
)
from aspy.program.variable_table import VariableTable


class TestTerm(unittest.TestCase):
    def test_infimum(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        term = Infimum()
        # string representation
        self.assertEqual(str(term), "#inf")
        # equality
        self.assertEqual(term, Infimum())
        # hashing
        self.assertEqual(hash(term), hash(Infimum()))
        # total order for terms
        self.assertTrue(term.precedes(Number(0)))
        # ground
        self.assertTrue(term.ground)
        # variables
        self.assertTrue(term.vars() == term.global_vars() == set())
        # replace arithmetic terms
        self.assertEqual(term.replace_arith(VariableTable()), term)
        # safety characterization
        self.assertEqual(term.safety(), SafetyTriplet())

        # substitute
        self.assertEqual(
            Infimum().substitute(Substitution({Infimum(): Supremum()})), Infimum()
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(Infimum().match(Supremum()), None)
        self.assertEqual(Infimum().match(Infimum()), Substitution())

    def test_supremum(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        term = Supremum()
        # string representation
        self.assertEqual(str(term), "#sup")
        # equality
        self.assertEqual(term, Supremum())
        # hashing
        self.assertEqual(hash(term), hash(Supremum()))
        # total order for terms
        self.assertTrue(term.precedes(Supremum()))
        # ground
        self.assertTrue(term.ground)
        # variables
        self.assertTrue(term.vars() == term.global_vars() == set())
        # replace arithmetic terms
        self.assertEqual(term.replace_arith(VariableTable()), term)
        # safety characterization
        self.assertEqual(term.safety(), SafetyTriplet())

        # substitute
        self.assertEqual(
            Supremum().substitute(Substitution({Supremum(): Infimum()})), Supremum()
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(Supremum().match(Infimum()), None)
        self.assertEqual(Supremum().match(Supremum()), Substitution())

    def test_variable(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        # invalid initialization
        self.assertRaises(ValueError, Variable, "x")
        # valid initialization
        term = Variable("X")
        # string representation
        self.assertEqual(str(term), "X")
        # equality
        self.assertEqual(term, Variable("X"))
        # hashing
        self.assertEqual(hash(term), hash(Variable("X")))
        # total order for terms
        self.assertRaises(Exception, term.precedes, term)
        # ground
        self.assertFalse(term.ground)
        # variables
        self.assertTrue(term.vars() == term.global_vars() == {term})
        # replace arithmetic terms
        self.assertEqual(term.replace_arith(VariableTable()), term)
        # safety characterization
        self.assertEqual(term.safety(), SafetyTriplet({term}))
        # simplify
        self.assertEqual(term.simplify(), term)

        # substitute
        self.assertEqual(
            Variable("X").substitute(Substitution({Variable("Y"): Number(0)})),
            Variable("X"),
        )
        self.assertEqual(
            Variable("X").substitute(Substitution({Variable("X"): Number(0)})),
            Number(0),
        )
        # match
        self.assertEqual(Variable("X").match(Variable("X")), Substitution())
        self.assertEqual(
            Variable("X").match(Number(1)), Substitution({Variable("X"): Number(1)})
        )

    def test_anon_variable(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        # invalid initialization
        self.assertRaises(ValueError, AnonVariable, -1)
        # valid initialization
        term = AnonVariable(0)
        # string representation
        self.assertEqual(str(term), "_0")
        # equality
        self.assertEqual(term, AnonVariable(0))
        # hashing
        self.assertEqual(hash(term), hash(AnonVariable(0)))
        # total order for terms
        self.assertRaises(Exception, term.precedes, term)
        # ground
        self.assertFalse(term.ground)
        # variables
        self.assertTrue(term.vars() == term.global_vars() == {term})
        # replace arithmetic terms
        self.assertEqual(term.replace_arith(VariableTable()), term)
        # safety characterization
        self.assertEqual(term.safety(), SafetyTriplet())
        # simplify
        self.assertEqual(term.simplify(), term)

        # substitute
        self.assertEqual(
            AnonVariable(0).substitute(Substitution({AnonVariable(1): Number(0)})),
            AnonVariable(0),
        )
        self.assertEqual(
            AnonVariable(0).substitute(Substitution({AnonVariable(0): Number(0)})),
            Number(0),
        )
        # match
        self.assertEqual(AnonVariable(0).match(AnonVariable(0)), Substitution())
        self.assertEqual(
            AnonVariable(0).match(Number(1)), Substitution({AnonVariable(0): Number(1)})
        )

    def test_number(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        term = Number(5)
        # string representation
        self.assertEqual(str(term), "5")
        # equality
        self.assertEqual(term, Number(5))
        # hashing
        self.assertEqual(hash(term), hash(Number(5)))
        # evaluation
        self.assertEqual(term.eval(), 5)
        # total order for terms
        self.assertFalse(term.precedes(Number(4)))
        self.assertTrue(term.precedes(Number(5)))
        # ground
        self.assertTrue(term.ground)
        # variables
        self.assertTrue(term.vars() == term.global_vars() == set())
        # replace arithmetic terms
        self.assertEqual(term.replace_arith(VariableTable()), term)
        # safety characterization
        self.assertEqual(term.safety(), SafetyTriplet())
        # simplify
        self.assertEqual(term.simplify(), term)

        # operators
        self.assertEqual(term + Number(2), Number(7))
        self.assertEqual(term - Number(2), Number(3))
        self.assertEqual(term * Number(2), Number(10))
        self.assertEqual(term // Number(2), Number(2))

        # substitute
        self.assertEqual(
            Number(0).substitute(Substitution({Number(0): Number(1)})), Number(0)
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(Number(0).match(Number(1)), None)
        self.assertEqual(Number(0).match(Number(0)), Substitution())

    def test_symbolic_constant(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        term = SymbolicConstant("b")
        # string representation
        self.assertEqual(str(term), "b")
        # equality
        self.assertEqual(term, SymbolicConstant("b"))
        # hashing
        self.assertEqual(hash(term), hash(SymbolicConstant("b")))
        # total order for terms
        self.assertFalse(term.precedes(SymbolicConstant("a")))
        self.assertTrue(term.precedes(SymbolicConstant("b")))
        # ground
        self.assertTrue(term.ground)
        # variables
        self.assertTrue(term.vars() == term.global_vars() == set())
        # replace arithmetic terms
        self.assertEqual(term.replace_arith(VariableTable()), term)
        # safety characterization
        self.assertEqual(term.safety(), SafetyTriplet())

        # substitute
        self.assertEqual(
            SymbolicConstant("f").substitute(
                Substitution({SymbolicConstant("f"): Number(0)})
            ),
            SymbolicConstant("f"),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(SymbolicConstant("a").match(SymbolicConstant("b")), None)
        self.assertEqual(
            SymbolicConstant("a").match(SymbolicConstant("a")), Substitution()
        )

    def test_string(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        term = String("!?$#b")
        # string representation
        self.assertEqual(str(term), '"!?$#b"')
        # equality
        self.assertEqual(term, String("!?$#b"))
        # hashing
        self.assertEqual(hash(term), hash(String("!?$#b")))
        # total order for terms
        self.assertFalse(term.precedes(String("!?$#a")))
        self.assertTrue(term.precedes(String("!?$#b")))
        # ground
        self.assertTrue(term.ground)
        # variables
        self.assertTrue(term.vars() == term.global_vars() == set())
        # replace arithmetic terms
        self.assertEqual(term.replace_arith(VariableTable()), term)
        # safety characterization
        self.assertEqual(term.safety(), SafetyTriplet())

        # substitute
        self.assertEqual(
            String("f").substitute(Substitution({String("f"): Number(0)})), String("f")
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(String("a").match(String("b")), None)
        self.assertEqual(String("a").match(String("a")), Substitution())

    def test_term_tuple(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        terms = TermTuple(Number(0), Variable("X"))
        # length
        self.assertEqual(len(terms), 2)
        # equality
        self.assertEqual(terms[0], Number(0))
        self.assertEqual(terms[1], Variable("X"))
        self.assertTrue(terms == TermTuple(Number(0), Variable("X")))
        # hashing
        self.assertEqual(hash(terms), hash(TermTuple(Number(0), Variable("X"))))
        # ground
        self.assertFalse(terms.ground)
        # variables
        self.assertTrue(terms.vars() == terms.global_vars() == {Variable("X")})
        # replace arithmetic terms
        self.assertEqual(
            TermTuple(Number(0), Minus(Variable("X"))).replace_arith(VariableTable()),
            TermTuple(Number(0), ArithVariable(0, Minus(Variable("X")))),
        )
        # safety characterization
        self.assertEqual(terms.safety(), (terms[0].safety(), terms[1].safety()))

        # substitute
        self.assertEqual(
            TermTuple(String("f"), Variable("X")).substitute(
                Substitution({String("f"): Number(0), Variable("X"): Number(1)})
            ),
            TermTuple(String("f"), Number(1)),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            TermTuple(Variable("X"), String("f")).match(
                TermTuple(Number(1), String("f"))
            ),
            Substitution({Variable("X"): Number(1)}),
        )
        self.assertEqual(
            TermTuple(Variable("X"), String("f")).match(
                TermTuple(Number(1), String("g"))
            ),
            None,
        )  # ground terms don't match
        self.assertEqual(
            TermTuple(Variable("X"), Variable("X")).match(
                TermTuple(Number(1), String("f"))
            ),
            None,
        )  # assignment conflict

        # combining terms
        self.assertEqual(
            terms + TermTuple(String("")),
            TermTuple(Number(0), Variable("X"), String("")),
        )
        # TODO: iter


if __name__ == "__main__":
    unittest.main()
