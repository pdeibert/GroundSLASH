import unittest

import aspy
from aspy.program.substitution import Substitution
from aspy.program.variable_table import VariableTable
from aspy.program.terms import Number, Variable, ArithVariable, Minus, String
from aspy.program.literals import LiteralTuple, PredicateLiteral


class TestLiteral(unittest.TestCase):
    def test_literal_tuple(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        literals = LiteralTuple(PredicateLiteral('p', Number(0), Variable('X')), PredicateLiteral('q', Minus(Variable('Y'))))
        # length
        self.assertEqual(len(literals), 2)
        # equality
        self.assertEqual(literals[0], PredicateLiteral('p', Number(0), Variable('X')))
        self.assertEqual(literals[1], PredicateLiteral('q', Minus(Variable('Y'))))
        self.assertTrue(literals == LiteralTuple(PredicateLiteral('p', Number(0), Variable('X')), PredicateLiteral('q', Minus(Variable('Y')))))
        # hashing
        self.assertEqual(hash(literals), hash(LiteralTuple(PredicateLiteral('p', Number(0), Variable('X')), PredicateLiteral('q', Minus(Variable('Y'))))))
        # ground
        self.assertFalse(literals.ground)
        # variables
        self.assertTrue(literals.vars() == literals.vars(global_only=True) == {Variable('X'), Variable('Y')})
        # replace arithmetic terms
        self.assertEqual(literals.replace_arith(VariableTable()), LiteralTuple(PredicateLiteral('p', Number(0), Variable('X')), PredicateLiteral('q', ArithVariable(0, Minus(Variable('Y'))))))
        self.assertEqual(literals.safety(), (literals[0].safety(), literals[1].safety()))

        # substitute
        self.assertEqual(LiteralTuple(PredicateLiteral('p', String('f'), Variable('X'))).substitute(Substitution({String('f'): Number(0), Variable('X'): Number(1)})), LiteralTuple(PredicateLiteral('p', String('f'), Number(1)))) # NOTE: substitution is invalid

        # combining literal tuples
        self.assertEqual(literals + LiteralTuple(PredicateLiteral('u')), LiteralTuple(PredicateLiteral('p', Number(0), Variable('X')), PredicateLiteral('q', Minus(Variable('Y'))), PredicateLiteral('u')))
        # TODO: iter


if __name__ == "__main__":
    unittest.main()