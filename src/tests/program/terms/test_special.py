import unittest

import ground_slash
from ground_slash.program.substitution import Substitution
from ground_slash.program.symbols import SpecialChar
from ground_slash.program.terms import Add, ArithVariable, Minus, Number, Variable


class TestSpecial(unittest.TestCase):
    def test_arith_variable(self):

        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        # invalid initialization
        self.assertRaises(ValueError, ArithVariable, -1, Add(Variable("X"), Number(1)))

        # valid initialization
        var = ArithVariable(0, Add(Variable("X"), Number(1)))
        # equality
        self.assertEqual(var, ArithVariable(0, Add(Variable("X"), Number(1))))
        # hashing
        self.assertEqual(
            hash(var), hash(ArithVariable(0, Add(Variable("X"), Number(1))))
        )
        # string representation
        self.assertEqual(str(var), f"{SpecialChar.TAU.value}0")
        # total order for terms
        self.assertRaises(Exception, var.precedes, Number(1))
        # ground
        self.assertFalse(var.ground)

        # substitute
        self.assertEqual(
            ArithVariable(0, Add(Variable("X"), Number(1))).substitute(
                Substitution(
                    {
                        ArithVariable(0, Add(Variable("X"), Number(1))): Number(0),
                        Variable("X"): Number(1),
                    }
                )
            ),
            Number(0),
            Number(1),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            ArithVariable(0, Minus(Variable("X"))).match(
                ArithVariable(0, Minus(Variable("X")))
            ),
            Substitution(),
        )
        self.assertEqual(
            ArithVariable(0, Minus(Variable("X"))).match(Number(1)),
            Substitution({ArithVariable(0, Minus(Variable("X"))): Number(1)}),
        )

    """
    def test_replace_arith(self):

        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        # ----- terms -----
        for expr in (Infimum(), Supremum(), Variable('X'), AnonVariable(0), Number(10), SymbolicConstant('f'), String('!?$#b'), TermTuple(Number(0), Variable('X'))):
            self.assertEqual(replace_arith(expr, VariableTable()), expr)

        # minus
        self.assertTrue(replace_arith(Minus(Number(1)), VariableTable()) == Minus(Number(1)).simplify() == Number(-1))
        self.assertEqual(replace_arith(Minus(Variable('X')), VariableTable()), ArithVariable(0, Minus(Variable('X'))))
        # add
        self.assertTrue(replace_arith(Add(Number(1), Number(2)), VariableTable()) == Add(Number(1), Number(2)).simplify() == Number(3))
        self.assertEqual(replace_arith(Add(Number(1), Variable('X')), VariableTable()), ArithVariable(0, Add(Number(1), Variable('X'))))
        # sub
        self.assertTrue(replace_arith(Sub(Number(1), Number(2)), VariableTable()) == Sub(Number(1), Number(2)).simplify() == Number(-1))
        self.assertEqual(replace_arith(Sub(Number(1), Variable('X')), VariableTable()), ArithVariable(0, Sub(Number(1), Variable('X'))))
        # mult
        self.assertTrue(replace_arith(Mult(Number(3), Number(2)), VariableTable()) == Mult(Number(3), Number(2)).simplify() == Number(6))
        self.assertEqual(replace_arith(Mult(Number(3), Variable('X')), VariableTable()), ArithVariable(0, Mult(Number(3), Variable('X'))))
        # div
        self.assertTrue(replace_arith(Div(Number(1), Number(2)), VariableTable()) == Div(Number(1), Number(2)).simplify() == Number(0))
        self.assertEqual(replace_arith(Div(Number(1), Variable('X')), VariableTable()), ArithVariable(0, Div(Number(1), Variable('X'))))

        # functional
        self.assertEqual(replace_arith(Functional('f', Minus(Number(1)), String('x'), VariableTable())), Functional('f', ArithVariable(0, Minus(Number(1))), String('x')))

        # ----- literals -----

        # predicate literals
        self.assertEqual(replace_arith(Naf(Neg(PredLiteral('p', Number(0), Minus(Variable('X'))))), VariableTable()), Naf(Neg(PredLiteral('p', Number(0), ArithVariable(0, Minus(Variable('X')))))))

        # equal
        self.assertEqual(Equal(Number(0), Minus(Variable(('X')))).replace_arith(VariableTable()), Equal(Number(0), ArithVariable(0, Minus(Variable('X')))))
        # unequal
        self.assertEqual(Unequal(Number(0), Minus(Variable(('X')))).replace_arith(VariableTable()), Unequal(Number(0), ArithVariable(0, Minus(Variable('X')))))
        # less
        self.assertEqual(Less(Number(0), Minus(Variable(('X')))).replace_arith(VariableTable()), Less(Number(0), ArithVariable(0, Minus(Variable('X')))))        
        # greater
        self.assertEqual(Greater(Number(0), Minus(Variable(('X')))).replace_arith(VariableTable()), Greater(Number(0), ArithVariable(0, Minus(Variable('X')))))
        # less than or equal
        self.assertEqual(LessEqual(Number(0), Minus(Variable(('X')))).replace_arith(VariableTable()), LessEqual(Number(0), ArithVariable(0, Minus(Variable('X')))))       
        # greater than or equal
        self.assertEqual(GreaterEqual(Number(0), Minus(Variable(('X')))).replace_arith(VariableTable()), GreaterEqual(Number(0), ArithVariable(0, Minus(Variable('X')))))

        # aggregate element
        element = AggrElement(
            TermTuple(Number(5), Minus(Variable('X'))),
            LiteralCollection(PredLiteral('p', String('str')), Naf(PredLiteral('q', Variable('Y'))))
        )
        self.assertEqual(replace_arith(element, VariableTable()),
            AggrElement(
                TermTuple(Number(5), ArithVariable(0, Minus(Variable('X')))),
                LiteralCollection(PredLiteral('p', String('str')), Naf(PredLiteral('q', Variable('Y'))))
            )
        )
        # count
        aggregate = AggrCount(AggrElement(TermTuple(Number(5)), LiteralCollection(PredLiteral('p', Minus(Variable('X'))), Naf(PredLiteral('q')))))
        self.assertEqual(replace_arith(aggregate, VariableTable()),
            AggrCount(
                AggrElement(
                    TermTuple(Number(5)),
                    LiteralCollection(
                        PredLiteral('p', ArithVariable(0, Minus(Variable('X')))),
                        Naf(PredLiteral('q'))
                    )
                )
            )
        )
        # sum
        aggregate = AggrSum(AggrElement(TermTuple(Number(5)), LiteralCollection(PredLiteral('p', Minus(Variable('X'))), Naf(PredLiteral('q')))))
        self.assertEqual(replace_arith(aggregate, VariableTable()),
            AggrSum(
                AggrElement(
                    TermTuple(Number(5)),
                    LiteralCollection(
                        PredLiteral('p', ArithVariable(0, Minus(Variable('X')))),
                        Naf(PredLiteral('q'))
                    )
                )
            )
        )
        # min
        aggregate = AggrMax(AggrElement(TermTuple(Number(5)), LiteralCollection(PredLiteral('p', Minus(Variable('X'))), Naf(PredLiteral('q')))))
        self.assertEqual(replace_arith(aggregate, VariableTable()),
            AggrMax(
                AggrElement(
                    TermTuple(Number(5)),
                    LiteralCollection(
                        PredLiteral('p', ArithVariable(0, Minus(Variable('X')))),
                        Naf(PredLiteral('q'))
                    )
                )
            )
        )
        # max
        aggregate = AggrMin(AggrElement(TermTuple(Number(5)), LiteralCollection(PredLiteral('p', Minus(Variable('X'))), Naf(PredLiteral('q')))))
        self.assertEqual(replace_arith(aggregate, VariableTable()),
            AggrMin(
                AggrElement(
                    TermTuple(Number(5)),
                    LiteralCollection(
                        PredLiteral('p', ArithVariable(0, Minus(Variable('X')))),
                        Naf(PredLiteral('q'))
                    )
                )
            )
        )
        # guard
        self.assertEqual(replace_arith(Guard(RelOp.EQUAL, Minus(Variable('X')), True), ), Guard(RelOp.EQUAL, ArithVariable(0, Variable('X')), True))
        # aggregate literal
        aggregate = AggrCount(AggrElement(TermTuple(Number(5)), LiteralCollection(PredLiteral('p', Minus(Variable('X'))), Naf(PredLiteral('q')))))
        literal = Naf(AggrLiteral(aggregate, Guard(RelOp.EQUAL, Minus(Variable('X')), True)))
        self.assertEqual(replace_arith(literal, VariableTable()),
            Naf(AggrLiteral(
                    AggrCount(
                    AggrElement(
                        TermTuple(Number(5)),
                        LiteralCollection(
                            PredLiteral('p', ArithVariable(0, Minus(Variable('X')))),
                            Naf(PredLiteral('q'))
                        )
                    ),
                    Guard(RelOp.EQUAL, ArithVariable(0, Variable('X')), True)
                )
            ))
        )

        # literal collection
        self.assertEqual(replace_arith(LiteralCollection(PredLiteral('p', Number(0), Variable('X')), PredLiteral('q', Minus(Variable('X')))), VariableTable()), LiteralCollection(PredLiteral('p', Number(0), Variable('X')), PredLiteral('q', ArithVariable(0, Minus(Variable('Y'))))))

        # ----- statements -----
    """


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
