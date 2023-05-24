import unittest

import ground_slash
from ground_slash.program.literals import LiteralCollection, Naf, Neg, PredLiteral
from ground_slash.program.safety_characterization import SafetyTriplet
from ground_slash.program.substitution import Substitution
from ground_slash.program.terms import ArithVariable, Minus, Number, String, Variable
from ground_slash.program.variable_table import VariableTable


class TestPredicate(unittest.TestCase):
    def test_predicate(self):

        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        # invalid initialization
        self.assertRaises(ValueError, PredLiteral, "P")

        literal = PredLiteral("p", Number(0), String("x"))
        naf_literal = Naf(PredLiteral("p", Number(0), String("x")))
        var_literal = PredLiteral("p", Number(0), Variable("X"))

        # string representation
        self.assertEqual(str(literal), 'p(0,"x")')
        self.assertEqual(
            str(Neg(PredLiteral("p", Number(0), String("x")))), '-p(0,"x")'
        )
        self.assertEqual(str(naf_literal), 'not p(0,"x")')
        self.assertEqual(
            str(Naf(Neg(PredLiteral("p", Number(0), String("x"))))),
            'not -p(0,"x")',
        )
        # equality
        self.assertEqual(literal, PredLiteral("p", Number(0), String("x")))
        # hashing
        self.assertEqual(hash(literal), hash(PredLiteral("p", Number(0), String("x"))))
        # arity
        self.assertEqual(literal.arity, 2)
        # predicate tuple
        self.assertEqual(literal.pred(), ("p", 2))
        # ground
        self.assertTrue(literal.ground)
        self.assertFalse(var_literal.ground)
        # variables
        self.assertTrue(literal.vars() == literal.global_vars() == set())
        self.assertTrue(
            var_literal.vars() == var_literal.global_vars() == {Variable("X")}
        )
        # replace arithmetic terms
        self.assertEqual(literal.replace_arith(VariableTable()), literal)
        self.assertEqual(var_literal.replace_arith(VariableTable()), var_literal)
        self.assertEqual(
            PredLiteral("p", Number(0), Minus(Number(1))).replace_arith(
                VariableTable()
            ),
            PredLiteral("p", Number(0), Number(-1)),
        )  # ground arithmetic term should not be replaced (only gets simplified)
        self.assertEqual(
            PredLiteral("p", Number(0), Minus(Variable("X"))).replace_arith(
                VariableTable()
            ),
            PredLiteral("p", Number(0), ArithVariable(0, Minus(Variable("X")))),
        )  # non-ground arithmetic term should be replaced
        # positive/negative literal occurrences
        self.assertEqual(
            literal.pos_occ(),
            LiteralCollection(PredLiteral("p", Number(0), String("x"))),
        )
        self.assertEqual(literal.neg_occ(), LiteralCollection())
        self.assertEqual(naf_literal.pos_occ(), LiteralCollection())
        self.assertEqual(
            naf_literal.neg_occ(),
            LiteralCollection(PredLiteral("p", Number(0), String("x"))),
        )
        # safety characterization
        self.assertEqual(literal.safety(), SafetyTriplet())
        self.assertEqual(var_literal.safety(), SafetyTriplet({Variable("X")}))

        # classical negation and negation-as-failure
        self.assertTrue(literal.naf == literal.neg == False)  # noqa
        literal.set_neg(True)
        self.assertTrue(literal.neg == True)  # noqa
        literal.set_naf(True)

        # substitute
        self.assertEqual(
            PredLiteral("p", Variable("X"), Number(0)).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            PredLiteral("p", Number(1), Number(0)),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            PredLiteral("p", Variable("X"), String("f")).match(
                PredLiteral("p", Number(1), String("f"))
            ),
            Substitution({Variable("X"): Number(1)}),
        )
        self.assertEqual(
            Naf(PredLiteral("p", Variable("X"), String("f"))).match(
                Naf(PredLiteral("p", Number(1), String("g")))
            ),
            None,
        )  # ground terms don't match
        self.assertEqual(
            Neg(PredLiteral("p", Variable("X"), Variable("X"))).match(
                Neg(PredLiteral("p", Number(1), String("f")))
            ),
            None,
        )  # assignment conflict


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
