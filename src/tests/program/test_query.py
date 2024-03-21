from typing import Self

import ground_slash
from ground_slash.program.literals import LiteralCollection, PredLiteral
from ground_slash.program.query import Query
from ground_slash.program.safety_characterization import SafetyTriplet
from ground_slash.program.substitution import Substitution
from ground_slash.program.terms import Number, String, Variable


class TestQuery:
    def test_query(self: Self):
        # make sure debug mode is enabled
        assert ground_slash.debug()

        ground_query = Query(PredLiteral("p", Number(0)))
        var_query = Query(PredLiteral("p", Variable("X")))

        # string representation
        assert str(ground_query) == "p(0) ?"
        # equality
        assert ground_query == Query(PredLiteral("p", Number(0)))
        # head
        assert ground_query.head == LiteralCollection(PredLiteral("p", Number(0)))
        # body
        assert ground_query.body == LiteralCollection()
        # hashing
        assert hash(ground_query) == hash(Query(PredLiteral("p", Number(0))))
        # ground
        assert ground_query.ground
        assert not var_query.ground
        # variables
        assert ground_query.vars() == ground_query.global_vars() == set()
        assert var_query.vars() == var_query.global_vars() == {Variable("X")}
        # safety characterization
        assert ground_query.safety() == SafetyTriplet()
        assert var_query.safety() == SafetyTriplet(safe={Variable("X")})

        # substitute
        assert var_query.substitute(
            Substitution({Variable("X"): Number(1), Number(0): String("f")})
        ) == Query(
            PredLiteral("p", Number(1))
        )  # NOTE: substitution is invalid
