import unittest

import ground_slash
from ground_slash.program.literals import (
    AggrCount,
    AggrLiteral,
    Equal,
    Guard,
    Neg,
    PredLiteral,
)
from ground_slash.program.operators import RelOp
from ground_slash.program.terms import Number, Variable


class TestNaf(unittest.TestCase):
    def test_naf(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        # predicate literal
        literal = PredLiteral("p", Number(0), Variable("Y"))
        self.assertFalse(literal.neg)
        literal_ = Neg(PredLiteral("p", Number(0), Variable("Y")))
        self.assertTrue(literal_.neg)
        self.assertTrue(
            literal.name == literal_.name and literal.terms == literal_.terms
        )
        self.assertFalse(Neg(PredLiteral("p", Number(0), Variable("Y")), False).neg)
        self.assertTrue(Neg(PredLiteral("p", Number(0), Variable("Y")), True).neg)

        # aggregate literal
        self.assertRaises(
            NotImplementedError,
            Neg,
            AggrLiteral(AggrCount(), tuple(), Guard(RelOp.LESS, Number(3), False)),
        )

        # builtin literal
        self.assertRaises(NotImplementedError, Neg, Equal(Number(0), Variable("Y")))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
