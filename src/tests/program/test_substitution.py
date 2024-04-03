import unittest

import ground_slash
from ground_slash.program.substitution import AssignmentError, Substitution
from ground_slash.program.terms import Number, String, Variable


class TestSubstitution(unittest.TestCase):
    def test_substitution(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        # empty substitution
        subst = Substitution()
        # equality
        self.assertEqual(subst, Substitution())
        # hashing
        self.assertEqual(hash(subst), hash(Substitution()))
        # __getitem__
        self.assertEqual(
            subst[Variable("X")], Variable("X")
        )  # map non-specified variables to themselves
        # identity
        self.assertTrue(Substitution().is_identity())
        self.assertTrue(Substitution({Variable("X"): Variable("X")}).is_identity())
        self.assertFalse(Substitution({Variable("X"): Variable("Y")}).is_identity())

        # non-empty substitution
        subst = Substitution({Variable("X"): Number(0), Variable("Y"): String("str")})
        # equality
        self.assertEqual(
            subst,
            Substitution({Variable("X"): Number(0), Variable("Y"): String("str")}),
        )
        # hashing
        self.assertEqual(
            hash(subst),
            hash(
                Substitution({Variable("X"): Number(0), Variable("Y"): String("str")})
            ),
        )
        # __getitem__
        self.assertTrue(subst[Variable("X")], Number(0))
        self.assertTrue(subst[Variable("Y")], String("str"))
        self.assertEqual(subst[Variable("X")], Number(0))
        self.assertEqual(
            subst[Variable("Z")], Variable("Z")
        )  # map non-specified variables to themselves

        # adding substitutions
        subst = Substitution(
            {Variable("X"): Number(0), Variable("Y"): String("str")}
        ) + Substitution({Variable("Y"): String("str"), Variable("Z"): Number(3)})
        self.assertEqual(
            subst,
            Substitution(
                {
                    Variable("X"): Number(0),
                    Variable("Y"): String("str"),
                    Variable("Z"): Number(3),
                }
            ),
        )
        with self.assertRaises(AssignmentError):
            Substitution(
                {Variable("X"): Number(0), Variable("Y"): String("str")}
            ) + Substitution({Variable("Y"): Number(3), Variable("Z"): Number(3)})

        # composing substitutions
        subst1 = Substitution({Variable("X"): Variable("Y")})
        subst2 = Substitution(
            {
                Variable("X"): Number(1),
                Variable("Y"): Number(0),
                Variable("Z"): String("a"),
            }
        )
        self.assertEqual(
            subst1.compose(subst2),
            Substitution(
                {
                    Variable("X"): Number(0),
                    Variable("Y"): Number(0),
                    Variable("Z"): String("a"),
                }
            ),
        )
        subst3 = Substitution({Variable("A"): Variable("B")})
        subst4 = Substitution({Variable("B"): String("b")})
        self.assertEqual(
            subst1.compose(subst2).compose(subst3).compose(subst4),
            Substitution.composition(subst1, subst2, subst3, subst4),
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
