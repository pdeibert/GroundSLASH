import unittest

import aspy
from aspy.program.literals import LiteralTuple, PredicateLiteral
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.substitution import Substitution
from aspy.program.terms import ArithVariable, Minus, Number, String, Variable
from aspy.program.variable_table import VariableTable


class TestLiteral(unittest.TestCase):
    def test_literal_tuple(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        literals = LiteralTuple(
            PredicateLiteral("p", Number(0), Variable("X")),
            PredicateLiteral("q", Minus(Variable("Y"))),
        )
        # length
        self.assertEqual(len(literals), 2)
        # string representation
        self.assertEqual(str(literals), "p(0,X),q(-Y)")
        # equality
        self.assertEqual(literals[0], PredicateLiteral("p", Number(0), Variable("X")))
        self.assertEqual(literals[1], PredicateLiteral("q", Minus(Variable("Y"))))
        self.assertTrue(
            literals
            == LiteralTuple(
                PredicateLiteral("p", Number(0), Variable("X")),
                PredicateLiteral("q", Minus(Variable("Y"))),
            )
        )
        # hashing
        self.assertEqual(
            hash(literals),
            hash(
                LiteralTuple(
                    PredicateLiteral("p", Number(0), Variable("X")),
                    PredicateLiteral("q", Minus(Variable("Y"))),
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
                PredicateLiteral("p", Number(0), Variable("X")),
                PredicateLiteral("q", ArithVariable(0, Minus(Variable("Y")))),
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
            LiteralTuple(PredicateLiteral("p", String("f"), Variable("X"))).substitute(
                Substitution({String("f"): Number(0), Variable("X"): Number(1)})
            ),
            LiteralTuple(PredicateLiteral("p", String("f"), Number(1))),
        )  # NOTE: substitution is invalid
        # match
        self.assertEqual(
            LiteralTuple(
                PredicateLiteral("p", Variable("X"), String("f")),
                PredicateLiteral("q", Variable("X")),
            ).match(
                LiteralTuple(
                    PredicateLiteral("p", Number(1), String("f")),
                    PredicateLiteral("q", Number(1)),
                )
            ),
            Substitution({Variable("X"): Number(1)}),
        )
        self.assertEqual(
            LiteralTuple(
                PredicateLiteral("p", Variable("X"), String("f")),
                PredicateLiteral("q", Variable("X")),
            ).match(
                LiteralTuple(
                    PredicateLiteral("p", Number(1), String("g")),
                    PredicateLiteral("q", Number(1)),
                )
            ),
            None,
        )  # ground terms don't match
        self.assertEqual(
            LiteralTuple(
                PredicateLiteral("p", Variable("X"), String("f")),
                PredicateLiteral("q", Variable("X")),
            ).match(PredicateLiteral("p")),
            None,
        )  # wrong type
        self.assertEqual(
            LiteralTuple(
                PredicateLiteral("p", Variable("X"), String("f")),
                PredicateLiteral("q", Variable("X")),
            ).match(
                LiteralTuple(
                    PredicateLiteral("p", Number(1), String("f")),
                    PredicateLiteral("q", Number(0)),
                )
            ),
            None,
        )  # assignment conflict
        self.assertEqual(
            LiteralTuple(
                PredicateLiteral("p", Number(0), String("f")),
                PredicateLiteral("q", Number(1)),
                PredicateLiteral("u", Number(0)),
            ).match(
                LiteralTuple(
                    PredicateLiteral("p", Number(0), String("f")),
                    PredicateLiteral("u", Number(0)),
                    PredicateLiteral("q", Number(1)),
                )
            ),
            None,
        )  # different order of literals

        # combining literal tuples
        self.assertEqual(
            literals + LiteralTuple(PredicateLiteral("u")),
            LiteralTuple(
                PredicateLiteral("p", Number(0), Variable("X")),
                PredicateLiteral("q", Minus(Variable("Y"))),
                PredicateLiteral("u"),
            ),
        )
        # without
        self.assertEqual(
            literals.without(PredicateLiteral("p", Number(0), Variable("X"))),
            LiteralTuple(PredicateLiteral("q", Minus(Variable("Y")))),
        )
        self.assertEqual(
            literals.without(PredicateLiteral("p", Number(1), Variable("X"))), literals
        )  # not part of original literal tuple
        # TODO: iter


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
