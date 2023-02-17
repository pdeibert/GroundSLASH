import unittest

import aspy
from aspy.program.variable_table import VariableTable
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.literals import Neg, PredicateLiteral
from aspy.program.terms import Variable, Number, String, Minus, ArithVariable


class TestPredicate(unittest.TestCase):
    def test_predicate(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        literal = PredicateLiteral('p', Number(0), String('x'))
        self.assertEqual(str(literal), 'p(0,"x")')
        self.assertEqual(literal, PredicateLiteral('p', Number(0), String('x')))
        self.assertEqual(hash(literal), hash(PredicateLiteral('p', Number(0), String('x'))))
        self.assertEqual(literal.arity, 2)
        self.assertTrue(literal.naf == literal.neg == False)
        self.assertEqual(literal.pred(), ('p', 2))
        self.assertTrue(literal.ground)
        self.assertTrue(literal.vars() == literal.vars(True) == set())
        self.assertEqual(literal.safety(), SafetyTriplet())
        self.assertEqual(literal.replace_arith(VariableTable()), literal)

        literal.set_neg(True)
        self.assertEqual(str(literal), '-p(0,"x")')
        self.assertTrue(literal.neg == True)
        self.assertEqual(literal.pos_occ(), {Neg(PredicateLiteral('p', Number(0), String('x')))})
        self.assertEqual(literal.neg_occ(), set())
        literal.set_naf(True)
        self.assertEqual(str(literal), 'not -p(0,"x")')
        self.assertEqual(literal.pos_occ(), set())
        self.assertEqual(literal.neg_occ(), {Neg(PredicateLiteral('p', Number(0), String('x')))})
        # TODO: match
        # TODO: substitute

        literal = PredicateLiteral('p', Number(0), Variable('X'))
        self.assertFalse(literal.ground)
        self.assertTrue(literal.vars() == literal.vars(True) == {Variable('X')})
        self.assertEqual(literal.safety(), SafetyTriplet({Variable('X')}))
        self.assertEqual(literal.replace_arith(VariableTable()), literal)

        # ground arithmetic term should not be replaced
        literal = PredicateLiteral('p', Number(0), Minus(Number(1)))
        self.assertEqual(literal.replace_arith(VariableTable()), literal)

        # non-ground arithmetic term should be replaced
        literal = PredicateLiteral('p', Number(0), Minus(Variable('X')))
        self.assertEqual(literal.replace_arith(VariableTable()), PredicateLiteral('p', Number(0), ArithVariable(0, Minus(Variable('X')))))     


if __name__ == "__main__":
    unittest.main()