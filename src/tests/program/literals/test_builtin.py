import unittest

import ground_slash
from ground_slash.program.literals import (
    Equal,
    Greater,
    GreaterEqual,
    Less,
    LessEqual,
    LiteralCollection,
    PredLiteral,
    Unequal,
)
from ground_slash.program.safety_characterization import SafetyTriplet
from ground_slash.program.substitution import Substitution
from ground_slash.program.terms import ArithVariable, Minus, Number, String, Variable
from ground_slash.program.variable_table import VariableTable


class TestBuiltin(unittest.TestCase):
    def test_equal(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        ground_literal = Equal(Number(0), String("x"))
        var_literal = Equal(Number(0), Variable("X"))

        # string representation
        self.assertEqual(str(ground_literal), '0="x"')
        # equality
        self.assertEqual(ground_literal, Equal(Number(0), String("x")))
        # hashing
        self.assertEqual(hash(ground_literal), hash(Equal(Number(0), String("x"))))
        # ground
        self.assertTrue(ground_literal.ground)
        self.assertFalse(var_literal.ground)
        # variables
        self.assertTrue(ground_literal.vars() == ground_literal.global_vars() == set())
        self.assertTrue(
            var_literal.vars() == var_literal.global_vars() == {Variable("X")}
        )
        # positive/negative literal occurrences
        self.assertTrue(
            ground_literal.pos_occ() == ground_literal.neg_occ() == LiteralCollection()
        )
        # operands
        self.assertEqual(ground_literal.operands, (Number(0), String("x")))
        # safety characterization
        self.assertEqual(ground_literal.safety(), SafetyTriplet())
        safety = var_literal.safety()
        self.assertEqual(safety.safe, {Variable("X")})
        self.assertEqual(safety.unsafe, set())
        self.assertEqual(safety.rules, set())
        # replace arithmetic terms
        self.assertEqual(
            var_literal.replace_arith(VariableTable()), Equal(Number(0), Variable("X"))
        )
        self.assertEqual(
            Equal(Variable("X"), Number(0)).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            Equal(Number(1), Number(0)),
        )  # NOTE: substitution is invalid
        self.assertEqual(
            Equal(Number(0), Minus(Variable(("X")))).replace_arith(VariableTable()),
            Equal(Number(0), ArithVariable(0, Minus(Variable("X")))),
        )
        # evaluation
        self.assertEqual(Equal(Number(0), String("x")).eval(), False)
        self.assertEqual(Equal(Number(0), Number(0)).eval(), True)
        self.assertRaises(ValueError, Equal(Number(0), Variable("X")).eval)
        self.assertRaises(ValueError, Equal(Number(0), Minus(Variable("X"))).eval)

        # substitute
        self.assertEqual(
            Equal(Variable("X"), Number(0)).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            Equal(Number(1), Number(0)),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            Equal(Variable("X"), String("f")).match(Equal(Number(1), String("f"))),
            Substitution({Variable("X"): Number(1)}),
        )
        self.assertEqual(
            Equal(Variable("X"), String("f")).match(Equal(Number(1), String("g"))), None
        )  # ground terms don't match
        self.assertEqual(
            Equal(Variable("X"), String("f")).match(PredLiteral("p")), None
        )  # different type
        self.assertEqual(
            Equal(Variable("X"), Variable("X")).match(Equal(Number(1), String("f"))),
            None,
        )  # assignment conflict

    def test_unequal(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        ground_literal = Unequal(Number(0), String("x"))
        var_literal = Unequal(Number(0), Variable("X"))

        # string representation
        self.assertEqual(str(ground_literal), '0!="x"')
        # equality
        self.assertEqual(ground_literal, Unequal(Number(0), String("x")))
        # hashing
        self.assertEqual(hash(ground_literal), hash(Unequal(Number(0), String("x"))))
        # ground
        self.assertTrue(ground_literal.ground)
        self.assertFalse(var_literal.ground)
        # variables
        self.assertTrue(ground_literal.vars() == ground_literal.global_vars() == set())
        self.assertTrue(
            var_literal.vars() == var_literal.global_vars() == {Variable("X")}
        )
        # positive/negative literal occurrences
        self.assertTrue(
            ground_literal.pos_occ() == ground_literal.neg_occ() == LiteralCollection()
        )
        # operands
        self.assertEqual(ground_literal.operands, (Number(0), String("x")))
        # safety characterization
        self.assertEqual(ground_literal.safety(), SafetyTriplet())
        self.assertEqual(var_literal.safety(), SafetyTriplet(unsafe={Variable("X")}))
        self.assertEqual(
            Unequal(Variable("Y"), Variable("X")).safety(),
            SafetyTriplet(unsafe={Variable("X"), Variable("Y")}),
        )
        # replace arithmetic terms
        self.assertEqual(
            var_literal.replace_arith(VariableTable()),
            Unequal(Number(0), Variable("X")),
        )
        self.assertEqual(
            Unequal(Variable("X"), Number(0)).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            Unequal(Number(1), Number(0)),
        )  # NOTE: substitution is invalid
        self.assertEqual(
            Unequal(Number(0), Minus(Variable(("X")))).replace_arith(VariableTable()),
            Unequal(Number(0), ArithVariable(0, Minus(Variable("X")))),
        )
        # evaluation
        self.assertEqual(Unequal(Number(0), String("x")).eval(), True)
        self.assertEqual(Unequal(Number(0), Number(0)).eval(), False)
        self.assertRaises(ValueError, Unequal(Number(0), Variable("X")).eval)
        self.assertRaises(ValueError, Unequal(Number(0), Minus(Variable("X"))).eval)

        # substitute
        self.assertEqual(
            Unequal(Variable("X"), Number(0)).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            Unequal(Number(1), Number(0)),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            Unequal(Variable("X"), String("f")).match(Unequal(Number(1), String("f"))),
            Substitution({Variable("X"): Number(1)}),
        )
        self.assertEqual(
            Unequal(Variable("X"), String("f")).match(Unequal(Number(1), String("g"))),
            None,
        )  # ground terms don't match
        self.assertEqual(
            Unequal(Variable("X"), String("f")).match(PredLiteral("p")), None
        )  # different type
        self.assertEqual(
            Unequal(Variable("X"), Variable("X")).match(
                Unequal(Number(1), String("f"))
            ),
            None,
        )  # assignment conflict

    def test_less(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        ground_literal = Less(Number(0), String("x"))
        var_literal = Less(Number(0), Variable("X"))

        # string representation
        self.assertEqual(str(ground_literal), '0<"x"')
        # equality
        self.assertEqual(ground_literal, Less(Number(0), String("x")))
        # hashing
        self.assertEqual(hash(ground_literal), hash(Less(Number(0), String("x"))))
        # ground
        self.assertTrue(ground_literal.ground)
        self.assertFalse(var_literal.ground)
        # variables
        self.assertTrue(ground_literal.vars() == ground_literal.global_vars() == set())
        self.assertTrue(
            var_literal.vars() == var_literal.global_vars() == {Variable("X")}
        )
        # positive/negative literal occurrences
        self.assertTrue(
            ground_literal.pos_occ() == ground_literal.neg_occ() == LiteralCollection()
        )
        # operands
        self.assertEqual(ground_literal.operands, (Number(0), String("x")))
        # safety characterization
        self.assertEqual(ground_literal.safety(), SafetyTriplet())
        self.assertEqual(var_literal.safety(), SafetyTriplet(unsafe={Variable("X")}))
        self.assertEqual(
            Less(Variable("Y"), Variable("X")).safety(),
            SafetyTriplet(unsafe={Variable("X"), Variable("Y")}),
        )
        # replace arithmetic terms
        self.assertEqual(
            var_literal.replace_arith(VariableTable()), Less(Number(0), Variable("X"))
        )
        self.assertEqual(
            Less(Variable("X"), Number(0)).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            Less(Number(1), Number(0)),
        )  # NOTE: substitution is invalid
        self.assertEqual(
            Less(Number(0), Minus(Variable(("X")))).replace_arith(VariableTable()),
            Less(Number(0), ArithVariable(0, Minus(Variable("X")))),
        )
        # evaluation
        self.assertEqual(Less(Number(0), String("x")).eval(), True)
        self.assertEqual(Less(Number(0), Number(1)).eval(), True)
        self.assertEqual(Less(Number(0), Number(0)).eval(), False)
        self.assertRaises(ValueError, Less(Number(0), Variable("X")).eval)
        self.assertRaises(ValueError, Less(Number(0), Minus(Variable("X"))).eval)

        # substitute
        self.assertEqual(
            Less(Variable("X"), Number(0)).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            Less(Number(1), Number(0)),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            Less(Variable("X"), String("f")).match(Less(Number(1), String("f"))),
            Substitution({Variable("X"): Number(1)}),
        )
        self.assertEqual(
            Less(Variable("X"), String("f")).match(Less(Number(1), String("g"))), None
        )  # ground terms don't match
        self.assertEqual(
            Less(Variable("X"), String("f")).match(PredLiteral("p")), None
        )  # different type
        self.assertEqual(
            Less(Variable("X"), Variable("X")).match(Less(Number(1), String("f"))), None
        )  # assignment conflict

    def test_greater(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        ground_literal = Greater(Number(0), String("x"))
        var_literal = Greater(Number(0), Variable("X"))

        # string representation
        self.assertEqual(str(ground_literal), '0>"x"')
        # equality
        self.assertEqual(ground_literal, Greater(Number(0), String("x")))
        # hashing
        self.assertEqual(hash(ground_literal), hash(Greater(Number(0), String("x"))))
        # ground
        self.assertTrue(ground_literal.ground)
        self.assertFalse(var_literal.ground)
        # variables
        self.assertTrue(ground_literal.vars() == ground_literal.global_vars() == set())
        self.assertTrue(
            var_literal.vars() == var_literal.global_vars() == {Variable("X")}
        )
        # positive/negative literal occurrences
        self.assertTrue(
            ground_literal.pos_occ() == ground_literal.neg_occ() == LiteralCollection()
        )
        # operands
        self.assertEqual(ground_literal.operands, (Number(0), String("x")))
        # safety characterization
        self.assertEqual(ground_literal.safety(), SafetyTriplet())
        self.assertEqual(var_literal.safety(), SafetyTriplet(unsafe={Variable("X")}))
        self.assertEqual(
            Greater(Variable("Y"), Variable("X")).safety(),
            SafetyTriplet(unsafe={Variable("X"), Variable("Y")}),
        )
        # replace arithmetic terms
        self.assertEqual(
            var_literal.replace_arith(VariableTable()),
            Greater(Number(0), Variable("X")),
        )
        self.assertEqual(
            Greater(Variable("X"), Number(0)).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            Greater(Number(1), Number(0)),
        )  # NOTE: substitution is invalid
        self.assertEqual(
            Greater(Number(0), Minus(Variable(("X")))).replace_arith(VariableTable()),
            Greater(Number(0), ArithVariable(0, Minus(Variable("X")))),
        )
        # evaluation
        self.assertEqual(Greater(Number(0), String("x")).eval(), False)
        self.assertEqual(Greater(Number(0), Number(1)).eval(), False)
        self.assertEqual(Greater(Number(0), Number(0)).eval(), False)
        self.assertEqual(Greater(Number(0), Number(-1)).eval(), True)
        self.assertRaises(ValueError, Greater(Number(0), Variable("X")).eval)
        self.assertRaises(ValueError, Greater(Number(0), Minus(Variable("X"))).eval)

        # substitute
        self.assertEqual(
            Greater(Variable("X"), Number(0)).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            Greater(Number(1), Number(0)),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            Greater(Variable("X"), String("f")).match(Greater(Number(1), String("f"))),
            Substitution({Variable("X"): Number(1)}),
        )
        self.assertEqual(
            Greater(Variable("X"), String("f")).match(Greater(Number(1), String("g"))),
            None,
        )  # ground terms don't match
        self.assertEqual(
            Greater(Variable("X"), String("f")).match(PredLiteral("p")), None
        )  # different type
        self.assertEqual(
            Greater(Variable("X"), Variable("X")).match(
                Greater(Number(1), String("f"))
            ),
            None,
        )  # assignment conflict

    def test_less_equal(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        ground_literal = LessEqual(Number(0), String("x"))
        var_literal = LessEqual(Number(0), Variable("X"))

        # string representation
        self.assertEqual(str(ground_literal), '0<="x"')
        # equality
        self.assertEqual(ground_literal, LessEqual(Number(0), String("x")))
        # hashing
        self.assertEqual(hash(ground_literal), hash(LessEqual(Number(0), String("x"))))
        # ground
        self.assertTrue(ground_literal.ground)
        self.assertFalse(var_literal.ground)
        # variables
        self.assertTrue(ground_literal.vars() == ground_literal.global_vars() == set())
        self.assertTrue(
            var_literal.vars() == var_literal.global_vars() == {Variable("X")}
        )
        # positive/negative literals occurrences
        self.assertTrue(
            ground_literal.pos_occ() == ground_literal.neg_occ() == LiteralCollection()
        )
        # operands
        self.assertEqual(ground_literal.operands, (Number(0), String("x")))
        # replace arithmetic terms
        self.assertEqual(
            var_literal.replace_arith(VariableTable()),
            LessEqual(Number(0), Variable("X")),
        )
        self.assertEqual(
            LessEqual(Variable("X"), Number(0)).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            LessEqual(Number(1), Number(0)),
        )  # NOTE: substitution is invalid
        self.assertEqual(
            LessEqual(Number(0), Minus(Variable(("X")))).replace_arith(VariableTable()),
            LessEqual(Number(0), ArithVariable(0, Minus(Variable("X")))),
        )
        # safety characterization
        self.assertEqual(ground_literal.safety(), SafetyTriplet())
        self.assertEqual(var_literal.safety(), SafetyTriplet(unsafe={Variable("X")}))
        self.assertEqual(
            LessEqual(Variable("Y"), Variable("X")).safety(),
            SafetyTriplet(unsafe={Variable("X"), Variable("Y")}),
        )
        # evaluation
        self.assertEqual(LessEqual(Number(0), String("x")).eval(), True)
        self.assertEqual(LessEqual(Number(0), Number(1)).eval(), True)
        self.assertEqual(LessEqual(Number(0), Number(0)).eval(), True)
        self.assertEqual(LessEqual(Number(0), Number(-1)).eval(), False)
        self.assertRaises(ValueError, LessEqual(Number(0), Variable("X")).eval)
        self.assertRaises(ValueError, LessEqual(Number(0), Minus(Variable("X"))).eval)

        # substitute
        self.assertEqual(
            LessEqual(Variable("X"), Number(0)).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            LessEqual(Number(1), Number(0)),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            LessEqual(Variable("X"), String("f")).match(
                LessEqual(Number(1), String("f"))
            ),
            Substitution({Variable("X"): Number(1)}),
        )
        self.assertEqual(
            LessEqual(Variable("X"), String("f")).match(
                LessEqual(Number(1), String("g"))
            ),
            None,
        )  # ground terms don't match
        self.assertEqual(
            LessEqual(Variable("X"), String("f")).match(PredLiteral("p")), None
        )  # different type
        self.assertEqual(
            LessEqual(Variable("X"), Variable("X")).match(
                LessEqual(Number(1), String("f"))
            ),
            None,
        )  # assignment conflict

    def test_greater_equal(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        ground_literal = GreaterEqual(Number(0), String("x"))
        var_literal = GreaterEqual(Number(0), Variable("X"))

        # string representation
        self.assertEqual(str(ground_literal), '0>="x"')
        # equality
        self.assertEqual(ground_literal, GreaterEqual(Number(0), String("x")))
        # hashing
        self.assertEqual(
            hash(ground_literal), hash(GreaterEqual(Number(0), String("x")))
        )
        # ground
        self.assertTrue(ground_literal.ground)
        self.assertFalse(var_literal.ground)
        # variables
        self.assertTrue(ground_literal.vars() == ground_literal.global_vars() == set())
        self.assertTrue(
            var_literal.vars() == var_literal.global_vars() == {Variable("X")}
        )
        # positive/negative literal occurrences
        self.assertTrue(
            ground_literal.pos_occ() == ground_literal.neg_occ() == LiteralCollection()
        )
        # operands
        self.assertEqual(ground_literal.operands, (Number(0), String("x")))
        # replace arithmetic variables
        self.assertEqual(
            var_literal.replace_arith(VariableTable()),
            GreaterEqual(Number(0), Variable("X")),
        )
        self.assertEqual(
            GreaterEqual(Variable("X"), Number(0)).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            GreaterEqual(Number(1), Number(0)),
        )  # NOTE: substitution is invalid
        self.assertEqual(
            GreaterEqual(Number(0), Minus(Variable(("X")))).replace_arith(
                VariableTable()
            ),
            GreaterEqual(Number(0), ArithVariable(0, Minus(Variable("X")))),
        )
        # safety characterization
        self.assertEqual(ground_literal.safety(), SafetyTriplet())
        self.assertEqual(var_literal.safety(), SafetyTriplet(unsafe={Variable("X")}))
        self.assertEqual(
            GreaterEqual(Variable("Y"), Variable("X")).safety(),
            SafetyTriplet(unsafe={Variable("X"), Variable("Y")}),
        )
        # evaluation
        self.assertEqual(GreaterEqual(Number(0), String("x")).eval(), False)
        self.assertEqual(GreaterEqual(Number(0), Number(1)).eval(), False)
        self.assertEqual(GreaterEqual(Number(0), Number(0)).eval(), True)
        self.assertRaises(ValueError, GreaterEqual(Number(0), Variable("X")).eval)
        self.assertRaises(
            ValueError, GreaterEqual(Number(0), Minus(Variable("X"))).eval
        )

        # substitute
        self.assertEqual(
            GreaterEqual(Variable("X"), Number(0)).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            GreaterEqual(Number(1), Number(0)),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            GreaterEqual(Variable("X"), String("f")).match(
                GreaterEqual(Number(1), String("f"))
            ),
            Substitution({Variable("X"): Number(1)}),
        )
        self.assertEqual(
            GreaterEqual(Variable("X"), String("f")).match(
                GreaterEqual(Number(1), String("g"))
            ),
            None,
        )  # ground terms don't match
        self.assertEqual(
            GreaterEqual(Variable("X"), String("f")).match(PredLiteral("p")), None
        )  # different type
        self.assertEqual(
            GreaterEqual(Variable("X"), Variable("X")).match(
                GreaterEqual(Number(1), String("f"))
            ),
            None,
        )  # assignment conflict


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
