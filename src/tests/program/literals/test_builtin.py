import unittest

import aspy
from aspy.program.variable_table import VariableTable
from aspy.program.safety_characterization import SafetyTriplet, SafetyRule
from aspy.program.literals import Naf, BuiltinLiteral, Equal, Unequal, Less, Greater, LessEqual, GreaterEqual
from aspy.program.terms import Variable, Number, String, Minus, ArithVariable


class TestBuiltin(unittest.TestCase):
    def test_equal(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        literal = Equal(Number(0), String('x'))
        self.assertEqual(str(literal), '0="x"')
        self.assertEqual(literal, Equal(Number(0), String('x')))
        self.assertEqual(hash(literal), hash(Equal(Number(0), String('x'))))
        self.assertTrue(literal.ground)
        self.assertTrue(literal.pos_occ() == literal.neg_occ() == set())
        self.assertTrue(literal.vars() == literal.vars(True) == set())
        self.assertEqual(literal.safety(), SafetyTriplet())
        self.assertEqual(literal.operands, (Number(0), String('x')))

        self.assertEqual(Equal(Number(0), String('x')).eval(), False)
        self.assertEqual(Equal(Number(0), Number(0)).eval(), True)
        self.assertRaises(ValueError, Equal(Number(0), Variable('X')).eval)
        self.assertRaises(ValueError, Equal(Number(0), Minus(Variable('X'))).eval)

        literal = Equal(Number(0), Variable('X'))        
        self.assertTrue(literal.vars() == literal.vars(True) == {Variable('X')})
        safety = literal.safety()
        self.assertFalse(literal.ground)
        self.assertEqual(safety.safe, {Variable('X')})
        self.assertEqual(safety.unsafe, set())
        self.assertEqual(safety.rules, set())
        self.assertEqual(literal.replace_arith(VariableTable()), Equal(Number(0), Variable('X')))
        literal = Equal(Variable('Y'), Variable('X'))
        safety = literal.safety()
        self.assertEqual(safety.safe, set())
        self.assertEqual(safety.unsafe, {Variable('X'), Variable('Y')})
        self.assertEqual(safety.rules, {SafetyRule(Variable('X'),{Variable('Y')}), SafetyRule(Variable('Y'),{Variable('X')})})
        literal = Equal(Number(0), Minus(Variable(('X'))))
        self.assertEqual(literal.replace_arith(VariableTable()), Equal(Number(0), ArithVariable(0, Minus(Variable('X')))))
        # TODO: match
        # TODO: substitute

    def test_unequal(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        literal = Unequal(Number(0), String('x'))
        self.assertEqual(str(literal), '0!="x"')
        self.assertEqual(literal, Unequal(Number(0), String('x')))
        self.assertEqual(hash(literal), hash(Unequal(Number(0), String('x'))))
        self.assertTrue(literal.ground)
        self.assertTrue(literal.pos_occ() == literal.neg_occ() == set())
        self.assertTrue(literal.vars() == literal.vars(True) == set())
        self.assertEqual(literal.safety(), SafetyTriplet())
        self.assertEqual(literal.operands, (Number(0), String('x')))

        self.assertEqual(Unequal(Number(0), String('x')).eval(), True)
        self.assertEqual(Unequal(Number(0), Number(0)).eval(), False)
        self.assertRaises(ValueError, Unequal(Number(0), Variable('X')).eval)
        self.assertRaises(ValueError, Unequal(Number(0), Minus(Variable('X'))).eval)

        literal = Unequal(Number(0), Variable('X'))        
        self.assertTrue(literal.vars() == literal.vars(True) == {Variable('X')})
        self.assertFalse(literal.ground)
        self.assertEqual(literal.safety(), SafetyTriplet(unsafe={Variable('X')}))
        self.assertEqual(literal.replace_arith(VariableTable()), Unequal(Number(0), Variable('X')))
        literal = Unequal(Variable('Y'), Variable('X'))
        self.assertEqual(literal.safety(), SafetyTriplet(unsafe={Variable('X'), Variable('Y')}))
        literal = Unequal(Number(0), Minus(Variable(('X'))))
        self.assertEqual(literal.replace_arith(VariableTable()), Unequal(Number(0), ArithVariable(0, Minus(Variable('X')))))
        # TODO: match
        # TODO: substitute

    def test_less(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        literal = Less(Number(0), String('x'))
        self.assertEqual(str(literal), '0<"x"')
        self.assertEqual(literal, Less(Number(0), String('x')))
        self.assertEqual(hash(literal), hash(Less(Number(0), String('x'))))
        self.assertTrue(literal.ground)
        self.assertTrue(literal.pos_occ() == literal.neg_occ() == set())
        self.assertTrue(literal.vars() == literal.vars(True) == set())
        self.assertEqual(literal.safety(), SafetyTriplet())
        self.assertEqual(literal.operands, (Number(0), String('x')))

        self.assertEqual(Less(Number(0), String('x')).eval(), True)
        self.assertEqual(Less(Number(0), Number(1)).eval(), True)
        self.assertEqual(Less(Number(0), Number(0)).eval(), False)
        self.assertRaises(ValueError, Less(Number(0), Variable('X')).eval)
        self.assertRaises(ValueError, Less(Number(0), Minus(Variable('X'))).eval)

        literal = Less(Number(0), Variable('X'))        
        self.assertTrue(literal.vars() == literal.vars(True) == {Variable('X')})
        self.assertFalse(literal.ground)
        self.assertEqual(literal.safety(), SafetyTriplet(unsafe={Variable('X')}))
        self.assertEqual(literal.replace_arith(VariableTable()), Less(Number(0), Variable('X')))
        literal = Less(Variable('Y'), Variable('X'))
        self.assertEqual(literal.safety(), SafetyTriplet(unsafe={Variable('X'), Variable('Y')}))
        literal = Less(Number(0), Minus(Variable(('X'))))
        self.assertEqual(literal.replace_arith(VariableTable()), Less(Number(0), ArithVariable(0, Minus(Variable('X')))))
        # TODO: match
        # TODO: substitute

    def test_greater(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        literal = Greater(Number(0), String('x'))
        self.assertEqual(str(literal), '0>"x"')
        self.assertEqual(literal, Greater(Number(0), String('x')))
        self.assertEqual(hash(literal), hash(Greater(Number(0), String('x'))))
        self.assertTrue(literal.ground)
        self.assertTrue(literal.pos_occ() == literal.neg_occ() == set())
        self.assertTrue(literal.vars() == literal.vars(True) == set())
        self.assertEqual(literal.safety(), SafetyTriplet())
        self.assertEqual(literal.operands, (Number(0), String('x')))

        self.assertEqual(Greater(Number(0), String('x')).eval(), False)
        self.assertEqual(Greater(Number(0), Number(1)).eval(), False)
        self.assertEqual(Greater(Number(0), Number(0)).eval(), False)
        self.assertEqual(Greater(Number(0), Number(-1)).eval(), True)
        self.assertRaises(ValueError, Greater(Number(0), Variable('X')).eval)
        self.assertRaises(ValueError, Greater(Number(0), Minus(Variable('X'))).eval)

        literal = Greater(Number(0), Variable('X'))        
        self.assertTrue(literal.vars() == literal.vars(True) == {Variable('X')})
        self.assertFalse(literal.ground)
        self.assertEqual(literal.safety(), SafetyTriplet(unsafe={Variable('X')}))
        self.assertEqual(literal.replace_arith(VariableTable()), Greater(Number(0), Variable('X')))
        literal = Greater(Variable('Y'), Variable('X'))
        self.assertEqual(literal.safety(), SafetyTriplet(unsafe={Variable('X'), Variable('Y')}))
        literal = Greater(Number(0), Minus(Variable(('X'))))
        self.assertEqual(literal.replace_arith(VariableTable()), Greater(Number(0), ArithVariable(0, Minus(Variable('X')))))
        # TODO: match
        # TODO: substitute

    def test_less_equal(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        literal = LessEqual(Number(0), String('x'))
        self.assertEqual(str(literal), '0<="x"')
        self.assertEqual(literal, LessEqual(Number(0), String('x')))
        self.assertEqual(hash(literal), hash(LessEqual(Number(0), String('x'))))
        self.assertTrue(literal.ground)
        self.assertTrue(literal.pos_occ() == literal.neg_occ() == set())
        self.assertTrue(literal.vars() == literal.vars(True) == set())
        self.assertEqual(literal.safety(), SafetyTriplet())
        self.assertEqual(literal.operands, (Number(0), String('x')))

        self.assertEqual(LessEqual(Number(0), String('x')).eval(), True)
        self.assertEqual(LessEqual(Number(0), Number(1)).eval(), True)
        self.assertEqual(LessEqual(Number(0), Number(0)).eval(), True)
        self.assertEqual(LessEqual(Number(0), Number(-1)).eval(), False)
        self.assertRaises(ValueError, LessEqual(Number(0), Variable('X')).eval)
        self.assertRaises(ValueError, LessEqual(Number(0), Minus(Variable('X'))).eval)

        literal = LessEqual(Number(0), Variable('X'))        
        self.assertTrue(literal.vars() == literal.vars(True) == {Variable('X')})
        self.assertFalse(literal.ground)
        self.assertEqual(literal.safety(), SafetyTriplet(unsafe={Variable('X')}))
        self.assertEqual(literal.replace_arith(VariableTable()), LessEqual(Number(0), Variable('X')))
        literal = LessEqual(Variable('Y'), Variable('X'))
        self.assertEqual(literal.safety(), SafetyTriplet(unsafe={Variable('X'), Variable('Y')}))
        literal = LessEqual(Number(0), Minus(Variable(('X'))))
        self.assertEqual(literal.replace_arith(VariableTable()), LessEqual(Number(0), ArithVariable(0, Minus(Variable('X')))))
        # TODO: match
        # TODO: substitute

    def test_greater_equal(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        literal = GreaterEqual(Number(0), String('x'))
        self.assertEqual(str(literal), '0>="x"')
        self.assertEqual(literal, GreaterEqual(Number(0), String('x')))
        self.assertEqual(hash(literal), hash(GreaterEqual(Number(0), String('x'))))
        self.assertTrue(literal.ground)
        self.assertTrue(literal.pos_occ() == literal.neg_occ() == set())
        self.assertTrue(literal.vars() == literal.vars(True) == set())
        self.assertEqual(literal.safety(), SafetyTriplet())
        self.assertEqual(literal.operands, (Number(0), String('x')))

        self.assertEqual(GreaterEqual(Number(0), String('x')).eval(), False)
        self.assertEqual(GreaterEqual(Number(0), Number(1)).eval(), False)
        self.assertEqual(GreaterEqual(Number(0), Number(0)).eval(), True)
        self.assertRaises(ValueError, GreaterEqual(Number(0), Variable('X')).eval)
        self.assertRaises(ValueError, GreaterEqual(Number(0), Minus(Variable('X'))).eval)

        literal = GreaterEqual(Number(0), Variable('X'))        
        self.assertTrue(literal.vars() == literal.vars(True) == {Variable('X')})
        self.assertFalse(literal.ground)
        self.assertEqual(literal.safety(), SafetyTriplet(unsafe={Variable('X')}))
        self.assertEqual(literal.replace_arith(VariableTable()), GreaterEqual(Number(0), Variable('X')))
        literal = GreaterEqual(Variable('Y'), Variable('X'))
        self.assertEqual(literal.safety(), SafetyTriplet(unsafe={Variable('X'), Variable('Y')}))
        literal = GreaterEqual(Number(0), Minus(Variable(('X'))))
        self.assertEqual(literal.replace_arith(VariableTable()), GreaterEqual(Number(0), ArithVariable(0, Minus(Variable('X')))))
        # TODO: match
        # TODO: substitute


if __name__ == "__main__":
    unittest.main()