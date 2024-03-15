import unittest
from typing import Self

import ground_slash
from ground_slash.program.safety_characterization import SafetyTriplet
from ground_slash.program.substitution import Substitution
from ground_slash.program.terms import (
    Add,
    ArithVariable,
    Div,
    Minus,
    Mult,
    Number,
    Sub,
    Variable,
)
from ground_slash.program.variable_table import VariableTable


class TestArithmetic(unittest.TestCase):
    def test_minus(self: Self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        ground_term = Minus(Number(1))
        var_term = Minus(Variable("X"))

        # string representation
        self.assertEqual(str(ground_term), "-1")
        self.assertEqual(
            str(Minus(Add(Number(3), Variable("X")))), "-(3+X)"
        )  # parentheses around nested term
        # equality
        self.assertEqual(ground_term, Minus(Number(1)))
        # hashing
        self.assertEqual(hash(ground_term), hash(Minus(Number(1))))
        # evaluation
        self.assertEqual(ground_term.eval(), -1)
        self.assertRaises(Exception, var_term.eval)
        # total order for terms
        self.assertFalse(ground_term.precedes(Number(-2)))
        self.assertTrue(ground_term.precedes(Number(-1)))
        self.assertRaises(Exception, var_term.precedes, Number(3))
        # ground
        self.assertTrue(ground_term.ground)
        self.assertFalse(var_term.ground)
        # variables
        self.assertTrue(ground_term.vars() == ground_term.global_vars() == set())
        self.assertTrue(var_term.vars() == var_term.global_vars() == {Variable("X")})
        # safety charachterization
        self.assertEqual(ground_term.safety(), SafetyTriplet())
        self.assertEqual(var_term.safety(), SafetyTriplet(unsafe={Variable("X")}))
        # simplify
        self.assertEqual(ground_term.simplify(), Number(-1))
        self.assertEqual(var_term.simplify(), var_term)

        # substitute
        self.assertEqual(
            var_term.substitute(Substitution({Variable("X"): Number(1)})),
            Number(-1),
        )
        self.assertEqual(
            ground_term.substitute(Substitution({Variable("X"): Number(1)})),
            ground_term,
        )
        # match
        self.assertRaises(ValueError, var_term.match, Number(3))
        self.assertRaises(ValueError, Minus(Number(3)).match, var_term)
        self.assertEqual(Minus(Number(3)).match(Minus(Number(1))), None)
        self.assertEqual(Minus(Number(3)).match(Minus(Number(3))), Substitution())

        self.assertEqual(Minus(Number(1)).simplify(), Number(-1))
        # double negation
        self.assertEqual(Minus(Minus(Variable("X"))).simplify(), Variable("X"))

    def test_add(self: Self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        ground_term = Add(Number(1), Number(2))
        var_term = Add(Number(1), Variable("X"))

        # string representation
        self.assertEqual(str(ground_term), "1+2")
        self.assertEqual(
            str(Add(Number(1), Add(Number(2), Number(3)))), "1+(2+3)"
        )  # parentheses around nested term
        # equality
        self.assertEqual(ground_term, Add(Number(1), Number(2)))
        # hashing
        self.assertEqual(hash(ground_term), hash(Add(Number(1), Number(2))))
        # evaluation
        self.assertEqual(ground_term.eval(), 3)
        self.assertRaises(Exception, var_term.eval)
        # total order for terms
        self.assertFalse(ground_term.precedes(Number(2)))
        self.assertTrue(ground_term.precedes(Number(3)))
        self.assertRaises(Exception, var_term.precedes, Number(3))
        # ground
        self.assertTrue(ground_term.ground)
        self.assertFalse(var_term.ground)
        # variables
        self.assertTrue(ground_term.vars() == ground_term.global_vars() == set())
        self.assertTrue(var_term.vars() == var_term.global_vars() == {Variable("X")})
        # replace arithmetic variable
        self.assertTrue(
            ground_term.replace_arith(VariableTable())
            == ground_term.simplify()
            == Number(3)
        )
        self.assertEqual(
            var_term.replace_arith(VariableTable()), ArithVariable(0, var_term)
        )
        # safety characterization
        self.assertEqual(ground_term.safety(), SafetyTriplet())
        self.assertEqual(var_term.safety(), SafetyTriplet(unsafe={Variable("X")}))
        # simplify
        self.assertEqual(ground_term.simplify(), Number(3))
        self.assertEqual(var_term.simplify(), var_term)

        # substitute
        self.assertEqual(
            Add(Variable("X"), Number(0)).substitute(
                Substitution({Variable("X"): Number(1)})
            ),
            Number(1),
        )
        self.assertEqual(
            ground_term.substitute(Substitution({Variable("X"): Number(1)})),
            ground_term,
        )
        # match
        self.assertRaises(ValueError, Add(Variable("X"), Number(2)).match, Number(3))
        self.assertRaises(
            ValueError, Add(Number(1), Number(2)).match, Minus(Variable("X"))
        )
        self.assertEqual(
            Add(Number(1), Number(2)).match(Add(Number(3), Number(1))), None
        )
        self.assertEqual(
            Add(Number(1), Number(2)).match(Add(Number(3), Number(0))), Substitution()
        )

        # addition of numbers
        self.assertEqual(Add(Number(1), Number(2)).simplify(), Number(3))
        # right operand zero
        self.assertEqual(Add(Variable("X"), Number(0)).simplify(), Variable("X"))
        # left operand zero
        self.assertEqual(Add(Number(0), Variable("X")).simplify(), Variable("X"))

    def test_sub(self: Self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        ground_term = Sub(Number(1), Number(2))
        var_term = Sub(Number(1), Variable("X"))

        # string representation
        self.assertEqual(str(ground_term), "1-2")
        self.assertEqual(
            str(Sub(Number(1), Sub(Number(3), Number(2)))), "1-(3-2)"
        )  # parentheses around nested term
        # equality
        self.assertEqual(ground_term, Sub(Number(1), Number(2)))
        # hashing
        self.assertEqual(hash(ground_term), hash(Sub(Number(1), Number(2))))
        # evaluation
        self.assertEqual(ground_term.eval(), -1)
        self.assertRaises(Exception, var_term.eval)
        # total order for terms
        self.assertFalse(ground_term.precedes(Number(-2)))
        self.assertRaises(Exception, var_term.precedes, Number(-1))
        # ground
        self.assertTrue(ground_term.ground)
        self.assertFalse(var_term.ground)
        # variables
        self.assertTrue(ground_term.vars() == ground_term.global_vars() == set())
        self.assertTrue(var_term.vars() == var_term.global_vars() == {Variable("X")})
        # replace arithmetic variable
        self.assertTrue(
            ground_term.replace_arith(VariableTable())
            == ground_term.simplify()
            == Number(-1)
        )
        self.assertEqual(
            var_term.replace_arith(VariableTable()), ArithVariable(0, var_term)
        )
        # safety characterization
        self.assertEqual(ground_term.safety(), SafetyTriplet())
        self.assertEqual(var_term.safety(), SafetyTriplet(unsafe={Variable("X")}))
        # simplify
        self.assertEqual(ground_term.simplify(), Number(-1))
        self.assertEqual(var_term.simplify(), var_term)

        # substitute
        self.assertEqual(
            Sub(Variable("X"), Number(0)).substitute(
                Substitution({Variable("X"): Number(1)})
            ),
            Number(1),
        )
        self.assertEqual(
            ground_term.substitute(Substitution({Variable("X"): Number(1)})),
            ground_term,
        )
        # match
        self.assertRaises(ValueError, Sub(Variable("X"), Number(2)).match, Number(1))
        self.assertRaises(
            ValueError, Sub(Number(3), Number(2)).match, Minus(Variable("X"))
        )
        self.assertEqual(
            Sub(Number(3), Number(2)).match(Sub(Number(3), Number(1))), None
        )
        self.assertEqual(
            Sub(Number(3), Number(2)).match(Sub(Number(3), Number(2))), Substitution()
        )

        # subtraction of numbers
        self.assertEqual(Sub(Number(1), Number(2)).simplify(), Number(-1))
        # right operand zero
        self.assertEqual(Sub(Variable("X"), Number(0)).simplify(), Variable("X"))
        # left operand zero
        self.assertEqual(Sub(Number(0), Variable("X")).simplify(), Minus(Variable("X")))

    def test_mult(self: Self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        ground_term = Mult(Number(3), Number(2))
        var_term = Mult(Number(3), Variable("X"))

        # string representation
        self.assertEqual(str(ground_term), "3*2")
        self.assertEqual(
            str(Mult(Number(3), Mult(Number(2), Number(1)))), "3*(2*1)"
        )  # parentheses around nested term
        # equality
        self.assertEqual(ground_term, Mult(Number(3), Number(2)))
        # hashing
        self.assertEqual(hash(ground_term), hash(Mult(Number(3), Number(2))))
        # evaluation
        self.assertEqual(ground_term.eval(), 6)
        self.assertRaises(Exception, var_term.eval)
        # total order for terms
        self.assertFalse(ground_term.precedes(Number(5)))
        self.assertTrue(ground_term.precedes(Number(6)))
        self.assertRaises(Exception, var_term.precedes, Number(3))
        # ground
        self.assertTrue(ground_term.ground)
        self.assertFalse(var_term.ground)
        # variables
        self.assertTrue(ground_term.vars() == ground_term.global_vars() == set())
        self.assertTrue(var_term.vars() == var_term.global_vars() == {Variable("X")})
        # replace arithmetic variable
        self.assertTrue(
            ground_term.replace_arith(VariableTable())
            == ground_term.simplify()
            == Number(6)
        )
        self.assertEqual(
            var_term.replace_arith(VariableTable()), ArithVariable(0, var_term)
        )
        # safety characterization
        self.assertEqual(var_term.safety(), SafetyTriplet())
        self.assertEqual(ground_term.safety(), SafetyTriplet(unsafe={Variable("X")}))
        # simplify
        self.assertEqual(ground_term.simplify(), Number(6))
        self.assertEqual(var_term.simplify(), var_term)

        # substitute
        self.assertEqual(
            Mult(Variable("X"), Number(0)).substitute(
                Substitution({Variable("X"): Number(1)})
            ),
            Number(0),
        )
        self.assertEqual(
            ground_term.substitute(Substitution({Variable("X"): Number(1)})),
            ground_term,
        )
        # match
        self.assertRaises(ValueError, Mult(Variable("X"), Number(2)).match, Number(6))
        self.assertRaises(
            ValueError, Mult(Number(3), Number(2)).match, Minus(Variable("X"))
        )
        self.assertEqual(
            Mult(Number(3), Number(2)).match(Mult(Number(3), Number(1))), None
        )
        self.assertEqual(
            Mult(Number(3), Number(2)).match(Mult(Number(2), Number(3))), Substitution()
        )

        # multiplication of numbers
        self.assertEqual(Mult(Number(2), Number(3)).simplify(), Number(6))
        # right operand zero
        self.assertEqual(Mult(Number(10), Number(0)).simplify(), Number(0))
        self.assertEqual(
            Mult(Variable("X"), Number(0)).simplify(), Mult(Variable("X"), Number(0))
        )
        # left operand zero
        self.assertEqual(Mult(Number(0), Number(10)).simplify(), Number(0))
        self.assertEqual(
            Mult(Number(0), Variable("X")).simplify(), Mult(Number(0), Variable("X"))
        )
        # right operand one
        self.assertEqual(Mult(Variable("X"), Number(1)).simplify(), Variable("X"))
        # left operand one
        self.assertEqual(Mult(Number(1), Variable("X")).simplify(), Variable("X"))
        # right operand negative one
        self.assertEqual(
            Mult(Variable("X"), Number(-1)).simplify(), Minus(Variable("X"))
        )
        self.assertEqual(
            Mult(Minus(Variable("X")), Number(-1)).simplify(), Variable("X")
        )
        # left operand negative one
        self.assertEqual(
            Mult(Number(-1), Variable("X")).simplify(), Minus(Variable("X"))
        )
        self.assertEqual(
            Mult(Number(-1), Minus(Variable("X"))).simplify(), Variable("X")
        )

    def test_div(self: Self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        ground_term = Div(Number(1), Number(2))
        var_term = Div(Number(1), Variable("X"))

        # string representation
        self.assertEqual(str(ground_term), "1/2")
        self.assertEqual(
            str(Div(Number(3), Div(Number(2), Number(1)))), "3/(2/1)"
        )  # parentheses around nested term
        # equality
        self.assertEqual(ground_term, Div(Number(1), Number(2)))
        # hashing
        self.assertEqual(hash(ground_term), hash(Div(Number(1), Number(2))))
        # evaluation
        self.assertEqual(ground_term.eval(), 0)
        self.assertRaises(Exception, var_term.eval)
        # total order for terms
        self.assertFalse(ground_term.precedes(Number(-1)))
        self.assertTrue(ground_term.precedes(Number(0)))
        self.assertRaises(Exception, var_term.precedes, Number(0))
        # ground
        self.assertTrue(ground_term.ground)
        self.assertFalse(var_term.ground)
        # variables
        self.assertTrue(ground_term.vars() == ground_term.global_vars() == set())
        self.assertTrue(var_term.vars() == var_term.global_vars() == {Variable("X")})
        # replace arithmetic variable
        self.assertTrue(
            ground_term.replace_arith(VariableTable())
            == ground_term.simplify()
            == Number(0)
        )
        self.assertEqual(
            var_term.replace_arith(VariableTable()), ArithVariable(0, var_term)
        )
        # safety characterization
        self.assertEqual(ground_term.safety(), SafetyTriplet())
        self.assertEqual(var_term.safety(), SafetyTriplet(unsafe={Variable("X")}))
        # simplify
        self.assertEqual(ground_term.simplify(), Number(0))
        self.assertEqual(var_term.simplify(), var_term)

        # substitute
        self.assertEqual(
            Div(Variable("X"), Number(1)).substitute(
                Substitution({Variable("X"): Number(2)})
            ),
            Number(2),
        )
        self.assertEqual(
            ground_term.substitute(Substitution({Variable("X"): Number(1)})),
            ground_term,
        )
        # match
        self.assertRaises(ValueError, Div(Variable("X"), Number(2)).match, Number(3))
        self.assertRaises(
            ValueError, Div(Number(1), Number(2)).match, Minus(Variable("X"))
        )
        self.assertEqual(
            Div(Number(1), Number(2)).match(Div(Number(1), Number(1))), None
        )
        self.assertEqual(
            Div(Number(1), Number(2)).match(Div(Number(0), Number(3))), Substitution()
        )

        # division of (valid) numbers
        self.assertEqual(
            Div(Number(3), Number(2)).simplify(), Number(1)
        )  # integer division
        self.assertEqual(
            Div(Number(3), Number(-2)).simplify(), Number(-2)
        )  # integer division
        # right operand zero
        self.assertRaises(ArithmeticError, Div(Variable("X"), Number(0)).simplify)
        self.assertRaises(ArithmeticError, Div(Number(1), Number(0)).simplify)
        # left operand zero
        self.assertEqual(Div(Number(0), Number(10)).simplify(), Number(0))
        self.assertEqual(
            Div(Number(0), Variable("X")).simplify(), Div(Number(0), Variable("X"))
        )
        # right operand one
        self.assertTrue(Div(Variable("X"), Number(1)).simplify(), Variable("X"))
        # right operand negative one
        self.assertTrue(Div(Variable("X"), Number(-1)).simplify(), Minus(Variable("X")))
        self.assertTrue(Div(Minus(Variable("X")), Number(-1)).simplify(), Variable("X"))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
