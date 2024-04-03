import unittest

import ground_slash
from ground_slash.program.safety_characterization import SafetyTriplet
from ground_slash.program.substitution import Substitution
from ground_slash.program.terms import (
    ArithVariable,
    Functional,
    Infimum,
    Minus,
    Number,
    String,
    Supremum,
    Variable,
)
from ground_slash.program.variable_table import VariableTable


class TestFunctional(unittest.TestCase):
    def test_functional(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        # invalid initialization
        self.assertRaises(ValueError, Functional, "F")
        # valid initialization
        ground_term = Functional("f", Number(1), String("x"))
        var_term = Functional("f", Variable("X"))
        # string representation
        self.assertEqual(str(ground_term), 'f(1,"x")')
        # equality
        self.assertEqual(ground_term, Functional("f", Number(1), String("x")))
        # hashing
        self.assertEqual(
            hash(ground_term), hash(Functional("f", Number(1), String("x")))
        )
        # arity
        self.assertEqual(ground_term.arity, 2)
        # total order for terms
        self.assertFalse(ground_term.precedes(Infimum()))
        self.assertFalse(ground_term.precedes(Functional("e", Number(1), String("x"))))
        self.assertFalse(ground_term.precedes(Functional("f", Number(0), String("x"))))
        self.assertFalse(ground_term.precedes(Functional("f", Number(0), String("y"))))
        self.assertTrue(ground_term.precedes(Functional("f", Number(1), String("x"))))
        self.assertTrue(ground_term.precedes(Functional("g", Infimum(), Infimum())))
        self.assertTrue(
            ground_term.precedes(Functional("f", Number(1), String("x"), Number(2)))
        )
        self.assertTrue(ground_term.precedes(Supremum()))
        # ground
        self.assertTrue(ground_term.ground)
        self.assertFalse(var_term.ground)
        # variables
        self.assertTrue(ground_term.vars() == ground_term.global_vars() == set())
        self.assertTrue(var_term.vars() == var_term.global_vars() == {Variable("X")})
        # replace arithmetic terms
        self.assertEqual(
            Functional("f", Minus(Variable("X")), String("x")).replace_arith(
                VariableTable()
            ),
            Functional("f", ArithVariable(0, Minus(Variable("X"))), String("x")),
        )
        # safety characterizatin
        self.assertEqual(ground_term.safety(), SafetyTriplet())
        self.assertEqual(var_term.safety(), SafetyTriplet({Variable("X")}))

        # substitute
        self.assertEqual(
            Functional("f", String("f"), Variable("X")).substitute(
                Substitution({String("f"): Number(0), Variable("X"): Number(1)})
            ),
            Functional("f", String("f"), Number(1)),
        )  # NOTE: substitution is invalid
        self.assertEqual(
            ground_term.substitute(
                Substitution({String("f"): Number(0), Variable("X"): Number(1)})
            ),
            ground_term,
        )
        # match
        self.assertEqual(
            Functional("f", Variable("X"), String("f")).match(
                Functional("f", Number(1), String("f"))
            ),
            Substitution({Variable("X"): Number(1)}),
        )
        self.assertEqual(
            Functional("f", Variable("X"), String("f")).match(
                Functional("f", Number(1), String("g"))
            ),
            None,
        )  # ground terms don't match
        self.assertEqual(
            Functional("f", Variable("X"), Variable("X")).match(
                Functional("f", Number(1), String("f"), Number(2))
            ),
            None,
        )  # different arity
        self.assertEqual(
            Functional("f", Variable("X"), Variable("X")).match(
                Functional("g", Variable("X"), Variable("X"))
            ),
            None,
        )  # different symbol
        self.assertEqual(
            Functional("f", Variable("X"), Variable("X")).match(
                Functional("f", Number(1), String("f"))
            ),
            None,
        )  # assignment conflict


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
