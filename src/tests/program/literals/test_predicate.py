import unittest

import aspy
from aspy.program.literals import Naf, Neg, PredicateLiteral
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.substitution import Substitution
from aspy.program.terms import ArithVariable, Minus, Number, String, Variable
from aspy.program.variable_table import VariableTable


class TestPredicate(unittest.TestCase):
    def test_predicate(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        literal = PredicateLiteral("p", Number(0), String("x"))
        naf_literal = Naf(PredicateLiteral("p", Number(0), String("x")))
        var_literal = PredicateLiteral("p", Number(0), Variable("X"))

        # string representation
        self.assertEqual(str(literal), 'p(0,"x")')
        self.assertEqual(str(Neg(PredicateLiteral("p", Number(0), String("x")))), '-p(0,"x")')
        self.assertEqual(str(naf_literal), 'not p(0,"x")')
        self.assertEqual(str(Naf(Neg(PredicateLiteral("p", Number(0), String("x"))))), 'not -p(0,"x")')
        # equality
        self.assertEqual(literal, PredicateLiteral("p", Number(0), String("x")))
        # hashing
        self.assertEqual(hash(literal), hash(PredicateLiteral("p", Number(0), String("x"))))
        # arity
        self.assertEqual(literal.arity, 2)
        # predicate tuple
        self.assertEqual(literal.pred(), ("p", 2))
        # ground
        self.assertTrue(literal.ground)
        self.assertFalse(var_literal.ground)
        # variables
        self.assertTrue(literal.vars() == literal.vars(True) == set())
        self.assertTrue(var_literal.vars() == var_literal.vars(True) == {Variable("X")})
        # replace arithmetic terms
        self.assertEqual(literal.replace_arith(VariableTable()), literal)
        self.assertEqual(var_literal.replace_arith(VariableTable()), var_literal)
        self.assertEqual(
            PredicateLiteral("p", Number(0), Minus(Number(1))).replace_arith(VariableTable()),
            PredicateLiteral("p", Number(0), Number(-1)),
        )  # ground arithmetic term should not be replaced (only gets simplified)
        self.assertEqual(
            PredicateLiteral("p", Number(0), Minus(Variable("X"))).replace_arith(VariableTable()),
            PredicateLiteral("p", Number(0), ArithVariable(0, Minus(Variable("X")))),
        )  # non-ground arithmetic term should be replaced
        # positive/negative literal occurrences
        self.assertEqual(literal.pos_occ(), {PredicateLiteral("p", Number(0), String("x"))})
        self.assertEqual(literal.neg_occ(), set())
        self.assertEqual(naf_literal.pos_occ(), set())
        self.assertEqual(naf_literal.neg_occ(), {PredicateLiteral("p", Number(0), String("x"))})
        # safety characterization
        self.assertEqual(literal.safety(), SafetyTriplet())
        self.assertEqual(var_literal.safety(), SafetyTriplet({Variable("X")}))

        # classical negation and negation-as-failure
        self.assertTrue(literal.naf == literal.neg == False)
        literal.set_neg(True)
        self.assertTrue(literal.neg == True)
        literal.set_naf(True)

        # substitute
        self.assertEqual(
            PredicateLiteral("p", Variable("X"), Number(0)).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            PredicateLiteral("p", Number(1), Number(0)),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            PredicateLiteral("p", Variable("X"), String("f")).match(PredicateLiteral("p", Number(1), String("f"))),
            Substitution({Variable("X"): Number(1)}),
        )
        self.assertEqual(
            Naf(PredicateLiteral("p", Variable("X"), String("f"))).match(
                Naf(PredicateLiteral("p", Number(1), String("g")))
            ),
            None,
        )  # ground terms don't match
        self.assertEqual(
            Neg(PredicateLiteral("p", Variable("X"), Variable("X"))).match(
                Neg(PredicateLiteral("p", Number(1), String("f")))
            ),
            None,
        )  # assignment conflict


if __name__ == "__main__":
    unittest.main()
