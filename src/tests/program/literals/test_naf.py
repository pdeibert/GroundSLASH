try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

import pytest  # type: ignore

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


class TestNaf:
    def test_naf(self: Self):
        # make sure debug mode is enabled
        assert ground_slash.debug()

        # predicate literal
        literal = PredLiteral("p", Number(0), Variable("Y"))
        assert not literal.naf
        literal_ = Naf(PredLiteral("p", Number(0), Variable("Y")))
        assert literal_.naf
        assert literal.name == literal_.name and literal.terms == literal_.terms
        assert not Naf(PredLiteral("p", Number(0), Variable("Y")), False).naf
        assert Naf(PredLiteral("p", Number(0), Variable("Y")), True).naf

        # aggregate literal
        literal = AggrLiteral(AggrCount(), tuple(), Guard(RelOp.LESS, Number(3), False))
        assert not literal.naf
        literal_ = Naf(
            AggrLiteral(AggrCount(), tuple(), Guard(RelOp.LESS, Number(3), False))
        )
        assert literal_.naf
        assert literal.func == literal_.func and literal.guards == literal_.guards
        assert not Naf(
            AggrLiteral(AggrCount(), tuple(), Guard(RelOp.LESS, Number(3), False)),
            False,
        ).naf
        assert Naf(
            AggrLiteral(AggrCount(), tuple(), Guard(RelOp.LESS, Number(3), False)),
            True,
        ).naf

        # builtin literal
        with pytest.raises(NotImplementedError):
            Naf(Equal(Number(0), Variable("Y")))
