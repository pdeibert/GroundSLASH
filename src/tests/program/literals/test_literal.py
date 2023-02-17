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
        self.assertEqual(len(literals), 2)
        self.assertEqual(literals[0], PredicateLiteral('p', Number(0), Variable('X')))
        self.assertEqual(literals[1], PredicateLiteral('q', Minus(Variable('Y'))))
        self.assertTrue(literals == LiteralTuple(PredicateLiteral('p', Number(0), Variable('X')), PredicateLiteral('q', Minus(Variable('Y')))))
        self.assertEqual(hash(literals), hash(LiteralTuple(PredicateLiteral('p', Number(0), Variable('X')), PredicateLiteral('q', Minus(Variable('Y'))))))
        self.assertTrue(literals.vars() == literals.vars(global_only=True) == {Variable('X'), Variable('Y')})
        self.assertEqual(literals.replace_arith(VariableTable()), LiteralTuple(PredicateLiteral('p', Number(0), Variable('X')), PredicateLiteral('q', ArithVariable(0, Minus(Variable('Y'))))))
        self.assertEqual(literals.safety(), (literals[0].safety(), literals[1].safety()))
        self.assertFalse(literals.ground)

        # substitute
        self.assertEqual(LiteralTuple(String('f'), Variable('X')).substitute(Substitution({String('f'): Number(0), Variable('X'): Number(1)})), LiteralTuple(String('f'), Number(1))) # NOTE: substitution is invalid
        # TODO: match

        self.assertEqual(literals + LiteralTuple(PredicateLiteral('u')), LiteralTuple(PredicateLiteral('p', Number(0), Variable('X')), PredicateLiteral('q', Minus(Variable('Y'))), PredicateLiteral('u')))
        # TODO: iter


if __name__ == "__main__":
    unittest.main()