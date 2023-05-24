import unittest

import ground_slash
from ground_slash.program.literals import LiteralCollection, PredLiteral
from ground_slash.program.safety_characterization import SafetyTriplet
from ground_slash.program.substitution import Substitution
from ground_slash.program.terms import ArithVariable, Minus, Number, String, Variable
from ground_slash.program.variable_table import VariableTable


class TestLiteral(unittest.TestCase):
    def test_literal_collection(self):

        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        literals = LiteralCollection(
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
            == LiteralCollection(
                PredLiteral("p", Number(0), Variable("X")),
                PredLiteral("q", Minus(Variable("Y"))),
            )
        )
        # hashing
        self.assertEqual(
            hash(literals),
            hash(
                LiteralCollection(
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
            LiteralCollection(
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
            LiteralCollection(PredLiteral("p", String("f"), Variable("X"))).substitute(
                Substitution({String("f"): Number(0), Variable("X"): Number(1)})
            ),
            LiteralCollection(PredLiteral("p", String("f"), Number(1))),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            LiteralCollection(
                PredLiteral("p", Variable("X"), String("f")),
                PredLiteral("q", Variable("X")),
            ).match(
                LiteralCollection(
                    PredLiteral("p", Number(1), String("f")),
                    PredLiteral("q", Number(1)),
                )
            ),
            Substitution({Variable("X"): Number(1)}),
        )
        self.assertEqual(
            LiteralCollection(
                PredLiteral("p", Variable("X"), String("f")),
                PredLiteral("q", Variable("X")),
            ).match(
                LiteralCollection(
                    PredLiteral("p", Number(1), String("g")),
                    PredLiteral("q", Number(1)),
                )
            ),
            None,
        )  # ground terms don't match
        self.assertEqual(
            LiteralCollection(
                PredLiteral("p", Variable("X"), String("f")),
                PredLiteral("q", Variable("X")),
            ).match(PredLiteral("p")),
            None,
        )  # wrong type
        self.assertEqual(
            LiteralCollection(
                PredLiteral("p", Variable("X"), String("f")),
                PredLiteral("q", Variable("X")),
            ).match(
                LiteralCollection(
                    PredLiteral("p", Number(1), String("f")),
                    PredLiteral("q", Number(0)),
                )
            ),
            None,
        )  # assignment conflict
        self.assertEqual(
            LiteralCollection(
                PredLiteral("p", Number(0), String("f")),
                PredLiteral("q", Number(1)),
                PredLiteral("u", Number(0)),
            ).match(
                LiteralCollection(
                    PredLiteral("p", Number(0), String("f")),
                    PredLiteral("u", Number(0)),
                    PredLiteral("q", Number(1)),
                )
            ),
            Substitution(),
        )  # different order of literals

        # combining literal collections
        self.assertEqual(
            literals + LiteralCollection(PredLiteral("u")),
            LiteralCollection(
                PredLiteral("p", Number(0), Variable("X")),
                PredLiteral("q", Minus(Variable("Y"))),
                PredLiteral("u"),
            ),
        )
        # without
        self.assertEqual(
            literals.without(PredLiteral("p", Number(0), Variable("X"))),
            LiteralCollection(PredLiteral("q", Minus(Variable("Y")))),
        )
        self.assertEqual(
            literals.without(PredLiteral("p", Number(1), Variable("X"))), literals
        )  # not part of original literal collection
        # TODO: iter


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
