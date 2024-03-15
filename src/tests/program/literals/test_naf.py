import unittest
from typing import Self

import ground_slash
from ground_slash.program.literals import (
    AggrCount,
    AggrLiteral,
    Equal,
    Guard,
    Naf,
    PredLiteral,
)
from ground_slash.program.operators import RelOp
from ground_slash.program.terms import Number, Variable


class TestNaf(unittest.TestCase):
    def test_naf(self: Self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        # predicate literal
        literal = PredLiteral("p", Number(0), Variable("Y"))
        self.assertFalse(literal.naf)
        literal_ = Naf(PredLiteral("p", Number(0), Variable("Y")))
        self.assertTrue(literal_.naf)
        self.assertTrue(
            literal.name == literal_.name and literal.terms == literal_.terms
        )
        self.assertFalse(Naf(PredLiteral("p", Number(0), Variable("Y")), False).naf)
        self.assertTrue(Naf(PredLiteral("p", Number(0), Variable("Y")), True).naf)

        # aggregate literal
        literal = AggrLiteral(AggrCount(), tuple(), Guard(RelOp.LESS, Number(3), False))
        self.assertFalse(literal.naf)
        literal_ = Naf(
            AggrLiteral(AggrCount(), tuple(), Guard(RelOp.LESS, Number(3), False))
        )
        self.assertTrue(literal_.naf)
        self.assertTrue(
            literal.func == literal_.func and literal.guards == literal_.guards
        )
        self.assertFalse(
            Naf(
                AggrLiteral(AggrCount(), tuple(), Guard(RelOp.LESS, Number(3), False)),
                False,
            ).naf
        )
        self.assertTrue(
            Naf(
                AggrLiteral(AggrCount(), tuple(), Guard(RelOp.LESS, Number(3), False)),
                True,
            ).naf
        )

        # builtin literal
        self.assertRaises(NotImplementedError, Naf, Equal(Number(0), Variable("Y")))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
