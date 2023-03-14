import unittest

import aspy
from aspy.program.literals import LiteralTuple, PredLiteral
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.substitution import Substitution
from aspy.program.terms import ArithVariable, Minus, Number, String, Variable
from aspy.program.variable_table import VariableTable


class TestLiteral(unittest.TestCase):
    def test_literal_tuple(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        literals = LiteralTuple(
            PredLiteral("p", Number(0), Variable("X")),
            PredLiteral("q", Minus(Variable("Y"))),
        )
        # length
        self.assertEqual(len(literals), 2)
        # string representation
        self.assertEqual(str(literals), "p(0,X),q(-Y)")
        # equality
        self.assertEqual(literals[0], PredLiteral("p", Number(0), Variable("X")))
        self.assertEqual(literals[1], PredLiteral("q", Minus(Variable("Y"))))
        self.assertTrue(
            literals
            == LiteralTuple(
                PredLiteral("p", Number(0), Variable("X")),
                PredLiteral("q", Minus(Variable("Y"))),
            )
        )
        # hashing
        self.assertEqual(
            hash(literals),
            hash(
                LiteralTuple(
                    PredLiteral("p", Number(0), Variable("X")),
                    PredLiteral("q", Minus(Variable("Y"))),
                )
            ),
        )
        # ground
        self.assertFalse(literals.ground)
        # variables
        self.assertTrue(
            literals.vars() == literals.global_vars() == {Variable("X"), Variable("Y")}
        )
        # replace arithmetic terms
        self.assertEqual(
            literals.replace_arith(VariableTable()),
            LiteralTuple(
                PredLiteral("p", Number(0), Variable("X")),
                PredLiteral("q", ArithVariable(0, Minus(Variable("Y")))),
            ),
        )
        self.assertEqual(
            literals.safety(),
            SafetyTriplet.closure(literals[0].safety(), literals[1].safety()),
        )
        # safety characterization
        self.assertEqual(
            literals.safety(),
            SafetyTriplet.closure(literals[0].safety(), literals[1].safety()),
        )

        # substitute
        self.assertEqual(
            LiteralTuple(PredLiteral("p", String("f"), Variable("X"))).substitute(
                Substitution({String("f"): Number(0), Variable("X"): Number(1)})
            ),
            LiteralTuple(PredLiteral("p", String("f"), Number(1))),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            LiteralTuple(
                PredLiteral("p", Variable("X"), String("f")),
                PredLiteral("q", Variable("X")),
            ).match(
                LiteralTuple(
                    PredLiteral("p", Number(1), String("f")),
                    PredLiteral("q", Number(1)),
                )
            ),
            Substitution({Variable("X"): Number(1)}),
        )
        self.assertEqual(
            LiteralTuple(
                PredLiteral("p", Variable("X"), String("f")),
                PredLiteral("q", Variable("X")),
            ).match(
                LiteralTuple(
                    PredLiteral("p", Number(1), String("g")),
                    PredLiteral("q", Number(1)),
                )
            ),
            None,
        )  # ground terms don't match
        self.assertEqual(
            LiteralTuple(
                PredLiteral("p", Variable("X"), String("f")),
                PredLiteral("q", Variable("X")),
            ).match(PredLiteral("p")),
            None,
        )  # wrong type
        self.assertEqual(
            LiteralTuple(
                PredLiteral("p", Variable("X"), String("f")),
                PredLiteral("q", Variable("X")),
            ).match(
                LiteralTuple(
                    PredLiteral("p", Number(1), String("f")),
                    PredLiteral("q", Number(0)),
                )
            ),
            None,
        )  # assignment conflict
        self.assertEqual(
            LiteralTuple(
                PredLiteral("p", Number(0), String("f")),
                PredLiteral("q", Number(1)),
                PredLiteral("u", Number(0)),
            ).match(
                LiteralTuple(
                    PredLiteral("p", Number(0), String("f")),
                    PredLiteral("u", Number(0)),
                    PredLiteral("q", Number(1)),
                )
            ),
            Substitution(),
        )  # different order of literals

        # combining literal tuples
        self.assertEqual(
            literals + LiteralTuple(PredLiteral("u")),
            LiteralTuple(
                PredLiteral("p", Number(0), Variable("X")),
                PredLiteral("q", Minus(Variable("Y"))),
                PredLiteral("u"),
            ),
        )
        # without
        self.assertEqual(
            literals.without(PredLiteral("p", Number(0), Variable("X"))),
            LiteralTuple(PredLiteral("q", Minus(Variable("Y")))),
        )
        self.assertEqual(
            literals.without(PredLiteral("p", Number(1), Variable("X"))), literals
        )  # not part of original literal tuple
        # TODO: iter


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
