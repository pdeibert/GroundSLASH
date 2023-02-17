import unittest

import aspy
from aspy.program.symbol_table import SpecialChar
from aspy.program.variable_table import VariableTable
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.terms import ArithVariable, Number, Variable, Minus, Add, Sub, Mult, Div


class TestArithmetic(unittest.TestCase):
    def test_arith_variable(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        var = ArithVariable(0, Add(Variable('X'), Number(1)))
        self.assertEqual(str(var), f"{SpecialChar.TAU}0")
        self.assertRaises(Exception, var.precedes, Number(1))
        self.assertEqual(var, ArithVariable(0, Add(Variable('X'), Number(1))))
        self.assertEqual(hash(var), hash(ArithVariable(0, Add(Variable('X'), Number(1)))))
        # TODO: match
        # TODO: substitute
        self.assertRaises(ValueError, ArithVariable, -1, Add(Variable('X'), Number(1)))
        self.assertFalse(var.ground)

    def test_minus(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        term = Minus(Number(1))
        self.assertEqual(str(term), "-1")
        self.assertEqual(term, Minus(Number(1)))
        self.assertEqual(hash(term), hash(Minus(Number(1))))
        self.assertEqual(term.eval(), -1)
        self.assertFalse(term.precedes(Number(-2)))
        self.assertTrue(term.precedes(Number(-1)))
        self.assertTrue(term.vars() == term.vars(global_only=True) == set())
        self.assertEqual(term.replace_arith(VariableTable()), term)
        self.assertEqual(term.safety(), SafetyTriplet())
        self.assertTrue(term.ground)

        term = Minus(Variable('X'))
        self.assertEqual(term.replace_arith(VariableTable()), ArithVariable(0, term))
        self.assertRaises(Exception, term.eval)
        self.assertFalse(term.ground)
        # TODO: match
        # TODO: substitute

        # negation of a number
        self.assertEqual(Minus(Number(1)).simplify(), Number(-1))
        # double negation
        self.assertEqual(Minus(Minus(Variable('X'))).simplify(), Variable('X'))

    def test_add(self):
    
        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        term = Add(Number(1), Number(2))
        self.assertEqual(str(term), "1+2")
        self.assertEqual(term, Add(Number(1), Number(2)))
        self.assertEqual(hash(term), hash(Add(Number(1), Number(2))))
        self.assertEqual(term.eval(), 3)
        self.assertFalse(term.precedes(Number(2)))
        self.assertTrue(term.precedes(Number(3)))
        self.assertTrue(term.vars() == term.vars(global_only=True) == set())
        self.assertEqual(term.replace_arith(VariableTable()), term)
        self.assertEqual(term.safety(), SafetyTriplet())
        self.assertTrue(term.ground)

        term = Add(Number(1), Variable('X'))
        self.assertEqual(term.replace_arith(VariableTable()), ArithVariable(0, term))
        self.assertRaises(Exception, term.eval)
        self.assertFalse(term.ground)
        # TODO: match
        # TODO: substitute

        # addition of numbers
        self.assertEqual(Add(Number(1), Number(2)).simplify(), Number(3))
        # right operand zero
        self.assertEqual(Add(Variable('X'), Number(0)).simplify(), Variable('X'))
        # left operand zero
        self.assertEqual(Add(Number(0), Variable('X')).simplify(), Variable('X'))

    def test_sub(self):
    
        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        term = Sub(Number(1), Number(2))
        self.assertEqual(str(term), "1-2")
        self.assertEqual(term, Sub(Number(1), Number(2)))
        self.assertEqual(hash(term), hash(Sub(Number(1), Number(2))))
        self.assertEqual(term.eval(), -1)
        self.assertFalse(term.precedes(Number(-2)))
        self.assertTrue(term.precedes(Number(-1)))
        self.assertTrue(term.vars() == term.vars(global_only=True) == set())
        self.assertEqual(term.replace_arith(VariableTable()), term)
        self.assertEqual(term.safety(), SafetyTriplet())
        self.assertTrue(term.ground)

        term = Sub(Number(1), Variable('X'))
        self.assertEqual(term.replace_arith(VariableTable()), ArithVariable(0, term))
        self.assertRaises(Exception, term.eval)
        self.assertFalse(term.ground)
        # TODO: match
        # TODO: substitute

        # subtraction of numbers
        self.assertEqual(Sub(Number(1), Number(2)).simplify(), Number(-1))
        # right operand zero
        self.assertEqual(Sub(Variable('X'), Number(0)).simplify(), Variable('X'))
        # left operand zero
        self.assertEqual(Sub(Number(0), Variable('X')).simplify(), Minus(Variable('X')))

    def test_mult(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        term = Mult(Number(1), Number(2))
        self.assertEqual(str(term), "1*2")
        self.assertEqual(term, Mult(Number(1), Number(2)))
        self.assertEqual(hash(term), hash(Mult(Number(1), Number(2))))
        self.assertEqual(term.eval(), 2)
        self.assertFalse(term.precedes(Number(1)))
        self.assertTrue(term.precedes(Number(2)))
        self.assertTrue(term.vars() == term.vars(global_only=True) == set())
        self.assertEqual(term.replace_arith(VariableTable()), term)
        self.assertEqual(term.safety(), SafetyTriplet())
        self.assertTrue(term.ground)

        term = Mult(Number(1), Variable('X'))
        self.assertEqual(term.replace_arith(VariableTable()), ArithVariable(0, term))
        self.assertRaises(Exception, term.eval)
        self.assertFalse(term.ground)
        # TODO: match
        # TODO: substitute
    
        # multiplication of numbers
        self.assertEqual(Mult(Number(2), Number(3)).simplify(), Number(6))
        # right operand zero 
        self.assertEqual(Mult(Number(10), Number(0)).simplify(), Number(0))
        self.assertEqual(Mult(Variable('X'), Number(0)).simplify(), Mult(Variable('X'), Number(0)))
        # left operand zero
        self.assertEqual(Mult(Number(0), Number(10)).simplify(), Number(0))
        self.assertEqual(Mult(Number(0), Variable('X')).simplify(), Mult(Number(0), Variable('X')))
        # right operand one
        self.assertEqual(Mult(Variable('X'), Number(1)).simplify(), Variable('X'))
        # left operand one
        self.assertEqual(Mult(Number(1), Variable('X')).simplify(), Variable('X'))
        # right operand negative one
        self.assertEqual(Mult(Variable('X'), Number(-1)).simplify(), Minus(Variable('X')))
        self.assertEqual(Mult(Minus(Variable('X')), Number(-1)).simplify(), Variable('X'))
        # left operand negative one
        self.assertEqual(Mult(Number(-1), Variable('X')).simplify(), Minus(Variable('X')))
        self.assertEqual(Mult(Number(-1), Minus(Variable('X'))).simplify(), Variable('X'))

    def test_div(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        term = Div(Number(1), Number(2))
        self.assertEqual(str(term), "1/2")
        self.assertEqual(term, Div(Number(1), Number(2)))
        self.assertEqual(hash(term), hash(Div(Number(1), Number(2))))
        self.assertEqual(term.eval(), 0)
        self.assertFalse(term.precedes(Number(-1)))
        self.assertTrue(term.precedes(Number(0)))
        self.assertTrue(term.vars() == term.vars(global_only=True) == set())
        self.assertEqual(term.replace_arith(VariableTable()), term)
        self.assertEqual(term.safety(), SafetyTriplet())
        self.assertTrue(term.ground)

        term = Div(Number(1), Variable('X'))
        self.assertEqual(term.replace_arith(VariableTable()), ArithVariable(0, term))
        self.assertRaises(Exception, term.eval)
        self.assertFalse(term.ground)
        # TODO: match
        # TODO: substitute
    
        # division of (valid) numbers
        self.assertEqual(Div(Number(3), Number(2)).simplify(), Number(1)) # integer division
        self.assertEqual(Div(Number(3), Number(-2)).simplify(), Number(-2)) # integer division
        # right operand zero 
        self.assertRaises(ArithmeticError, Div(Variable('X'), Number(0)).simplify)
        self.assertRaises(ArithmeticError, Div(Number(1), Number(0)).simplify)
        # left operand zero
        self.assertEqual(Div(Number(0), Number(10)).simplify(), Number(0))
        self.assertEqual(Div(Number(0), Variable('X')).simplify(), Div(Number(0), Variable('X')))
        # right operand one
        self.assertTrue(Div(Variable('X'), Number(1)).simplify(), Variable('X'))
        # right operand negative one
        self.assertTrue(Mult(Variable('X'), Number(-1)).simplify(), Minus(Variable('X')))
        self.assertTrue(Mult(Minus(Variable('X')), Number(-1)).simplify(), Variable('X'))


if __name__ == "__main__":
    unittest.main()