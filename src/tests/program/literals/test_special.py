import unittest

import aspy
from aspy.program.literals import (
    AggrBaseLiteral,
    AggrElemLiteral,
    AggrPlaceholder,
    ChoiceBaseLiteral,
    ChoiceElemLiteral,
    ChoicePlaceholder,
    LiteralCollection,
    Naf,
)
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.substitution import Substitution
from aspy.program.symbols import SpecialChar
from aspy.program.terms import Number, String, TermTuple, Variable
from aspy.program.variable_table import VariableTable


class TestSpecial(unittest.TestCase):
    def test_aggr_placeholder(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        vars = TermTuple(Variable("X"), Variable("Y"))
        literal = AggrPlaceholder(1, vars, TermTuple(Number(1), Variable("Y")))
        naf_literal = Naf(AggrPlaceholder(1, vars, TermTuple(Number(1), Variable("Y"))))

        # check initialization
        self.assertTrue(literal.ref_id == naf_literal.ref_id == 1)
        self.assertTrue(literal.glob_vars == naf_literal.glob_vars == vars)
        self.assertTrue(
            literal.terms == naf_literal.terms == TermTuple(Number(1), Variable("Y"))
        )
        # string representation
        self.assertEqual(str(literal), f"{SpecialChar.ALPHA.value}{1}(1,Y)")
        self.assertEqual(str(naf_literal), f"not {SpecialChar.ALPHA.value}{1}(1,Y)")
        # equality
        self.assertEqual(
            literal, AggrPlaceholder(1, vars, TermTuple(Number(1), Variable("Y")))
        )
        # hashing
        self.assertEqual(
            hash(literal),
            hash(AggrPlaceholder(1, vars, TermTuple(Number(1), Variable("Y")))),
        )
        # arity
        self.assertEqual(literal.arity, 2)
        # predicate tuple
        self.assertEqual(literal.pred(), (f"{SpecialChar.ALPHA.value}{1}", 2))
        # ground
        self.assertTrue(literal.ground == naf_literal.ground == False)  # noqa
        # TODO: variables
        # replace arithmetic terms
        self.assertEqual(literal.replace_arith(VariableTable()), literal)
        # positive/negative literal occurrences
        self.assertEqual(
            literal.pos_occ(),
            LiteralCollection(
                AggrPlaceholder(1, vars, TermTuple(Number(1), Variable("Y")))
            ),
        )
        self.assertEqual(literal.neg_occ(), LiteralCollection())
        self.assertEqual(naf_literal.pos_occ(), LiteralCollection())
        self.assertEqual(
            naf_literal.neg_occ(),
            LiteralCollection(
                AggrPlaceholder(1, vars, TermTuple(Number(1), Variable("Y")))
            ),
        )
        # safety characterization
        self.assertEqual(literal.safety(), SafetyTriplet({Variable("Y")}))

        # classical negation and negation-as-failure
        self.assertTrue(
            literal.naf == (not naf_literal.naf) == literal.neg == False  # noqa
        )
        self.assertRaises(Exception, literal.set_neg)
        literal.set_naf(True)
        self.assertTrue(literal.naf is True)

        # substitute
        self.assertEqual(
            AggrPlaceholder(1, vars, TermTuple(Number(1), Variable("Y"))).substitute(
                Substitution({Variable("Y"): Number(0), Number(1): String("f")})
            ),
            AggrPlaceholder(1, vars, TermTuple(Number(1), Number(0))),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            AggrPlaceholder(1, vars, TermTuple(Variable("X"), Variable("Y"))).match(
                AggrPlaceholder(1, vars, TermTuple(Number(1), Variable("Y")))
            ),
            Substitution({Variable("X"): Number(1)}),
        )
        self.assertEqual(
            Naf(AggrPlaceholder(1, vars, TermTuple(Variable("X"), String("f")))).match(
                Naf(AggrPlaceholder(1, vars, TermTuple(Number(1), String("g"))))
            ),
            None,
        )  # ground terms don't match

        # gather variable assignment
        self.assertEqual(
            AggrPlaceholder(
                1, vars, TermTuple(Number(1), Variable("Y"))
            ).gather_var_assignment(),
            Substitution({Variable("X"): Number(1)}),
        )

    def test_aggr_base_literal(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        vars = TermTuple(Variable("X"), Variable("Y"))
        literal = AggrBaseLiteral(1, vars, TermTuple(Number(1), Variable("Y")))

        # check initialization
        self.assertEqual(literal.ref_id, 1)
        self.assertEqual(literal.glob_vars, vars)
        self.assertEqual(literal.terms, TermTuple(Number(1), Variable("Y")))
        # string representation
        self.assertEqual(
            str(literal), f"{SpecialChar.EPS.value}{SpecialChar.ALPHA.value}{1}(1,Y)"
        )
        # equality
        self.assertEqual(
            literal, AggrBaseLiteral(1, vars, TermTuple(Number(1), Variable("Y")))
        )
        # hashing
        self.assertEqual(
            hash(literal),
            hash(AggrBaseLiteral(1, vars, TermTuple(Number(1), Variable("Y")))),
        )
        # arity
        self.assertEqual(literal.arity, 2)
        # predicate tuple
        self.assertEqual(
            literal.pred(), (f"{SpecialChar.EPS.value}{SpecialChar.ALPHA.value}{1}", 2)
        )
        # ground
        self.assertFalse(literal.ground)
        # TODO: variables
        # replace arithmetic terms
        self.assertEqual(literal.replace_arith(VariableTable()), literal)
        # positive/negative literal occurrences
        self.assertEqual(
            literal.pos_occ(),
            LiteralCollection(
                AggrBaseLiteral(1, vars, TermTuple(Number(1), Variable("Y")))
            ),
        )
        self.assertEqual(literal.neg_occ(), LiteralCollection())
        # safety characterization
        self.assertEqual(literal.safety(), SafetyTriplet({Variable("Y")}))

        # classical negation and negation-as-failure
        self.assertTrue(literal.naf == literal.neg == False)  # noqa
        self.assertRaises(Exception, literal.set_neg)
        self.assertRaises(Exception, literal.set_naf)

        # substitute
        self.assertEqual(
            AggrBaseLiteral(1, vars, TermTuple(Number(1), Variable("Y"))).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            AggrBaseLiteral(1, vars, TermTuple(Number(1), Variable("Y"))),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            AggrBaseLiteral(1, vars, TermTuple(Variable("X"), Variable("Y"))).match(
                AggrBaseLiteral(1, vars, TermTuple(Number(1), Variable("Y")))
            ),
            Substitution({Variable("X"): Number(1)}),
        )
        self.assertEqual(
            AggrBaseLiteral(1, vars, TermTuple(Variable("X"), String("f"))).match(
                AggrBaseLiteral(1, vars, TermTuple(Number(1), String("g")))
            ),
            None,
        )  # ground terms don't match

        # gather variable assignment
        self.assertEqual(
            AggrBaseLiteral(
                1, vars, TermTuple(Number(1), Variable("Y"))
            ).gather_var_assignment(),
            Substitution({Variable("X"): Number(1)}),
        )

    def test_aggr_elem_literal(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        global_vars = TermTuple(Variable("L"))
        local_vars = TermTuple(Variable("X"), Variable("Y"))
        literal = AggrElemLiteral(
            1,
            3,
            local_vars,
            global_vars,
            TermTuple(Variable("L"), Number(1), Variable("Y")),
        )

        # check initialization
        self.assertEqual(literal.ref_id, 1)
        self.assertEqual(literal.element_id, 3)
        self.assertEqual(literal.local_vars, local_vars)
        self.assertEqual(literal.glob_vars, global_vars)
        self.assertEqual(
            literal.terms, TermTuple(Variable("L"), Number(1), Variable("Y"))
        )
        # string representation
        self.assertEqual(
            str(literal),
            f"{SpecialChar.ETA.value}{SpecialChar.ALPHA.value}{1}_{3}(L,1,Y)",
        )
        # equality
        self.assertEqual(
            literal,
            AggrElemLiteral(
                1,
                3,
                local_vars,
                global_vars,
                TermTuple(Variable("L"), Number(1), Variable("Y")),
            ),
        )
        # hashing
        self.assertEqual(
            hash(literal),
            hash(
                AggrElemLiteral(
                    1,
                    3,
                    local_vars,
                    global_vars,
                    TermTuple(Variable("L"), Number(1), Variable("Y")),
                )
            ),
        )
        # arity
        self.assertEqual(literal.arity, 3)
        # predicate tuple
        self.assertEqual(
            literal.pred(),
            (f"{SpecialChar.ETA.value}{SpecialChar.ALPHA.value}{1}_{3}", 3),
        )
        # ground
        self.assertFalse(literal.ground)
        # TODO: variables
        # replace arithmetic terms
        self.assertEqual(literal.replace_arith(VariableTable()), literal)
        # positive/negative literal occurrences
        self.assertEqual(
            literal.pos_occ(),
            LiteralCollection(
                AggrElemLiteral(
                    1,
                    3,
                    local_vars,
                    global_vars,
                    TermTuple(Variable("L"), Number(1), Variable("Y")),
                )
            ),
        )
        self.assertEqual(literal.neg_occ(), LiteralCollection())
        # safety characterization
        self.assertEqual(
            literal.safety(), SafetyTriplet({Variable("L"), Variable("Y")})
        )

        # classical negation and negation-as-failure
        self.assertTrue(literal.naf == literal.neg == False)  # noqa
        self.assertRaises(Exception, literal.set_neg)
        self.assertRaises(Exception, literal.set_naf)

        # substitute
        self.assertEqual(
            AggrElemLiteral(
                1,
                3,
                local_vars,
                global_vars,
                TermTuple(Variable("L"), Variable("X"), Variable("Y")),
            ).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            AggrElemLiteral(
                1,
                3,
                local_vars,
                global_vars,
                TermTuple(Variable("L"), Number(1), Variable("Y")),
            ),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            AggrElemLiteral(
                1,
                3,
                local_vars,
                global_vars,
                TermTuple(Variable("L"), Variable("X"), Variable("Y")),
            ).match(
                AggrElemLiteral(
                    1,
                    3,
                    local_vars,
                    global_vars,
                    TermTuple(Number(1), Variable("X"), String("f")),
                )
            ),
            Substitution({Variable("L"): Number(1), Variable("Y"): String("f")}),
        )
        self.assertEqual(
            AggrElemLiteral(
                1,
                3,
                local_vars,
                global_vars,
                TermTuple(Variable("L"), Variable("X"), String("f")),
            ).match(
                AggrElemLiteral(
                    1,
                    3,
                    local_vars,
                    global_vars,
                    TermTuple(Number(1), Number(0), String("g")),
                )
            ),
            None,
        )  # ground terms don't match

    def test_choice_placeholder(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        vars = TermTuple(Variable("X"), Variable("Y"))
        literal = ChoicePlaceholder(1, vars, TermTuple(Number(1), Variable("Y")))
        self.assertRaises(
            Exception,
            Naf,
            ChoicePlaceholder(1, vars, TermTuple(Number(1), Variable("Y"))),
        )

        # check initialization
        self.assertEqual(literal.ref_id, 1)
        self.assertEqual(literal.glob_vars, vars)
        self.assertEqual(literal.terms, TermTuple(Number(1), Variable("Y")))
        # string representation
        self.assertEqual(str(literal), f"{SpecialChar.CHI.value}{1}(1,Y)")
        # equality
        self.assertEqual(
            literal, ChoicePlaceholder(1, vars, TermTuple(Number(1), Variable("Y")))
        )
        # hashing
        self.assertEqual(
            hash(literal),
            hash(ChoicePlaceholder(1, vars, TermTuple(Number(1), Variable("Y")))),
        )
        # arity
        self.assertEqual(literal.arity, 2)
        # predicate tuple
        self.assertEqual(literal.pred(), (f"{SpecialChar.CHI.value}{1}", 2))
        # ground
        self.assertFalse(literal.ground)
        # TODO: variables

        # replace arithmetic terms
        self.assertEqual(literal.replace_arith(VariableTable()), literal)
        # positive/negative literal occurrences
        self.assertEqual(
            literal.pos_occ(),
            LiteralCollection(
                ChoicePlaceholder(1, vars, TermTuple(Number(1), Variable("Y")))
            ),
        )
        self.assertEqual(literal.neg_occ(), LiteralCollection())

        # safety characterization
        self.assertEqual(literal.safety(), SafetyTriplet({Variable("Y")}))

        # classical negation and negation-as-failure
        self.assertTrue(literal.naf == literal.neg == False)  # noqa
        self.assertRaises(Exception, literal.set_neg)
        self.assertRaises(Exception, literal.set_naf)

        # substitute
        self.assertEqual(
            ChoicePlaceholder(1, vars, TermTuple(Number(1), Variable("Y"))).substitute(
                Substitution({Variable("Y"): Number(0), Number(1): String("f")})
            ),
            ChoicePlaceholder(1, vars, TermTuple(Number(1), Number(0))),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            ChoicePlaceholder(1, vars, TermTuple(Variable("X"), Variable("Y"))).match(
                ChoicePlaceholder(1, vars, TermTuple(Number(1), Variable("Y")))
            ),
            Substitution({Variable("X"): Number(1)}),
        )
        self.assertEqual(
            ChoicePlaceholder(1, vars, TermTuple(Variable("X"), String("f"))).match(
                ChoicePlaceholder(1, vars, TermTuple(Number(1), String("g")))
            ),
            None,
        )  # ground terms don't match

        # gather variable assignment
        self.assertEqual(
            ChoicePlaceholder(
                1, vars, TermTuple(Number(1), Variable("Y"))
            ).gather_var_assignment(),
            Substitution({Variable("X"): Number(1)}),
        )

    def test_choice_base_literal(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        vars = TermTuple(Variable("X"), Variable("Y"))
        literal = ChoiceBaseLiteral(1, vars, TermTuple(Number(1), Variable("Y")))

        # check initialization
        self.assertEqual(literal.ref_id, 1)
        self.assertEqual(literal.glob_vars, vars)
        self.assertEqual(literal.terms, TermTuple(Number(1), Variable("Y")))
        # string representation
        self.assertEqual(
            str(literal), f"{SpecialChar.EPS.value}{SpecialChar.CHI.value}{1}(1,Y)"
        )
        # equality
        self.assertEqual(
            literal, ChoiceBaseLiteral(1, vars, TermTuple(Number(1), Variable("Y")))
        )
        # hashing
        self.assertEqual(
            hash(literal),
            hash(ChoiceBaseLiteral(1, vars, TermTuple(Number(1), Variable("Y")))),
        )
        # arity
        self.assertEqual(literal.arity, 2)
        # predicate tuple
        self.assertEqual(
            literal.pred(), (f"{SpecialChar.EPS.value}{SpecialChar.CHI.value}{1}", 2)
        )
        # ground
        self.assertFalse(literal.ground)
        # TODO: variables
        # replace arithmetic terms
        self.assertEqual(literal.replace_arith(VariableTable()), literal)
        # positive/negative literal occurrences
        self.assertEqual(
            literal.pos_occ(),
            LiteralCollection(
                ChoiceBaseLiteral(1, vars, TermTuple(Number(1), Variable("Y")))
            ),
        )
        self.assertEqual(literal.neg_occ(), LiteralCollection())
        # safety characterization
        self.assertEqual(literal.safety(), SafetyTriplet({Variable("Y")}))

        # classical negation and negation-as-failure
        self.assertTrue(literal.naf == literal.neg == False)  # noqa
        self.assertRaises(Exception, literal.set_neg)
        self.assertRaises(Exception, literal.set_naf)

        # substitute
        self.assertEqual(
            ChoiceBaseLiteral(1, vars, TermTuple(Number(1), Variable("Y"))).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            ChoiceBaseLiteral(1, vars, TermTuple(Number(1), Variable("Y"))),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            ChoiceBaseLiteral(1, vars, TermTuple(Variable("X"), Variable("Y"))).match(
                ChoiceBaseLiteral(1, vars, TermTuple(Number(1), Variable("Y")))
            ),
            Substitution({Variable("X"): Number(1)}),
        )
        self.assertEqual(
            ChoiceBaseLiteral(1, vars, TermTuple(Variable("X"), String("f"))).match(
                ChoiceBaseLiteral(1, vars, TermTuple(Number(1), String("g")))
            ),
            None,
        )  # ground terms don't match

        # gather variable assignment
        self.assertEqual(
            ChoiceBaseLiteral(
                1, vars, TermTuple(Number(1), Variable("Y"))
            ).gather_var_assignment(),
            Substitution({Variable("X"): Number(1)}),
        )

    def test_choice_elem_literal(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        global_vars = TermTuple(Variable("L"))
        local_vars = TermTuple(Variable("X"), Variable("Y"))
        literal = ChoiceElemLiteral(
            1,
            3,
            local_vars,
            global_vars,
            TermTuple(Variable("L"), Number(1), Variable("Y")),
        )

        # check initialization
        self.assertEqual(literal.ref_id, 1)
        self.assertEqual(literal.element_id, 3)
        self.assertEqual(literal.local_vars, local_vars)
        self.assertEqual(literal.glob_vars, global_vars)
        self.assertEqual(
            literal.terms, TermTuple(Variable("L"), Number(1), Variable("Y"))
        )
        # string representation
        self.assertEqual(
            str(literal),
            f"{SpecialChar.ETA.value}{SpecialChar.CHI.value}{1}_{3}(L,1,Y)",
        )
        # equality
        self.assertEqual(
            literal,
            ChoiceElemLiteral(
                1,
                3,
                local_vars,
                global_vars,
                TermTuple(Variable("L"), Number(1), Variable("Y")),
            ),
        )
        # hashing
        self.assertEqual(
            hash(literal),
            hash(
                ChoiceElemLiteral(
                    1,
                    3,
                    local_vars,
                    global_vars,
                    TermTuple(Variable("L"), Number(1), Variable("Y")),
                )
            ),
        )
        # arity
        self.assertEqual(literal.arity, 3)
        # predicate tuple
        self.assertEqual(
            literal.pred(),
            (f"{SpecialChar.ETA.value}{SpecialChar.CHI.value}{1}_{3}", 3),
        )
        # ground
        self.assertFalse(literal.ground)
        # TODO: variables
        # replace arithmetic terms
        self.assertEqual(literal.replace_arith(VariableTable()), literal)
        # positive/negative literal occurrences
        self.assertEqual(
            literal.pos_occ(),
            LiteralCollection(
                ChoiceElemLiteral(
                    1,
                    3,
                    local_vars,
                    global_vars,
                    TermTuple(Variable("L"), Number(1), Variable("Y")),
                )
            ),
        )
        self.assertEqual(literal.neg_occ(), LiteralCollection())
        # safety characterization
        self.assertEqual(
            literal.safety(), SafetyTriplet({Variable("L"), Variable("Y")})
        )

        # classical negation and negation-as-failure
        self.assertTrue(literal.naf == literal.neg == False)  # noqa
        self.assertRaises(Exception, literal.set_neg)
        self.assertRaises(Exception, literal.set_naf)

        # substitute
        self.assertEqual(
            ChoiceElemLiteral(
                1,
                3,
                local_vars,
                global_vars,
                TermTuple(Variable("L"), Variable("X"), Variable("Y")),
            ).substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            ChoiceElemLiteral(
                1,
                3,
                local_vars,
                global_vars,
                TermTuple(Variable("L"), Number(1), Variable("Y")),
            ),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            ChoiceElemLiteral(
                1,
                3,
                local_vars,
                global_vars,
                TermTuple(Variable("L"), Variable("X"), Variable("Y")),
            ).match(
                ChoiceElemLiteral(
                    1,
                    3,
                    local_vars,
                    global_vars,
                    TermTuple(Number(1), Variable("X"), String("f")),
                )
            ),
            Substitution({Variable("L"): Number(1), Variable("Y"): String("f")}),
        )
        self.assertEqual(
            ChoiceElemLiteral(
                1,
                3,
                local_vars,
                global_vars,
                TermTuple(Variable("L"), Variable("X"), String("f")),
            ).match(
                ChoiceElemLiteral(
                    1,
                    3,
                    local_vars,
                    global_vars,
                    TermTuple(Number(1), Number(0), String("g")),
                )
            ),
            None,
        )  # ground terms don't match


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
