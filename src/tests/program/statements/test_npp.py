from typing import Self, Set

import pytest  # type: ignore

import ground_slash
from ground_slash.program.literals import (
    AggrCount,
    AggrLiteral,
    Guard,
    LiteralCollection,
    PredLiteral,
)
from ground_slash.program.operators import RelOp
from ground_slash.program.statements import NPP, NPPRule
from ground_slash.program.substitution import Substitution
from ground_slash.program.terms import (
    Add,
    ArithVariable,
    Minus,
    Number,
    String,
    TermTuple,
    Variable,
)
from ground_slash.program.variable_table import VariableTable


class DummyBody:  # pragma: no cover
    def __init__(self: Self, vars: Set["Variable"]) -> None:
        self.vars = vars

    def global_vars(self: Self) -> Set["Variable"]:
        return self.vars


class DummyRule:  # pragma: no cover
    def __init__(self: Self, vars: Set["Variable"]) -> None:
        self.body = DummyBody(vars)


class TestNPP:
    def test_npp(self: Self):
        # make sure debug mode is enabled
        assert ground_slash.debug()

        ground_terms = TermTuple(
            String("term"),
            Number(0),
            String("1"),
        )
        ground_outcomes = TermTuple(Number(0), String("1"))
        ground_atoms = LiteralCollection(
            PredLiteral("my_npp", *ground_terms, Number(0)),
            PredLiteral("my_npp", *ground_terms, String("1")),
        )
        ground_npp = NPP("my_npp", ground_terms, ground_outcomes)

        var_terms = TermTuple(
            Variable("X"),
            Number(0),
            Variable("Y"),
        )
        var_outcomes = TermTuple(
            Number(0),
            Variable("Y"),
        )
        var_atoms = LiteralCollection(
            PredLiteral("my_npp", *var_terms, Number(0)),
            PredLiteral("my_npp", *var_terms, Variable("Y")),
        )
        var_npp = NPP("my_npp", var_terms, var_outcomes)

        # initialization
        assert ground_npp.terms == ground_terms
        assert ground_npp.outcomes == ground_outcomes
        assert ground_npp.atoms == ground_atoms
        assert str(ground_npp) == '#npp(my_npp("term",0,"1"),[0,"1"])'
        # equality
        assert ground_npp == NPP(
            "my_npp",
            ground_terms,
            ground_outcomes,
        )
        # hashing
        assert hash(ground_npp) == hash(
            NPP(
                "my_npp",
                ground_terms,
                ground_outcomes,
            )
        )
        # ground
        assert ground_npp.ground
        assert not var_npp.ground
        # variables
        assert (
            ground_npp.vars()
            == ground_npp.global_vars(DummyRule({Variable("Y")}))
            == set()
        )
        assert (
            var_npp.vars()
            == var_npp.global_vars(DummyRule({Variable("Y")}))
            == {Variable("X"), Variable("Y")}
        )
        # positive/negative literal occurrences
        assert var_npp.pos_occ() == var_atoms
        assert var_npp.neg_occ() == LiteralCollection()

        # safety characterization
        with pytest.raises(Exception):
            var_npp.safety()
        # replace arithmetic terms
        arith_terms = TermTuple(
            String("term"),
            Minus(Variable("X")),
            String("1"),
        )
        arith_outcomes = TermTuple(Add(Number(-1), Number(1)), String("1"))
        npp = NPP(
            "my_npp",
            arith_terms,
            arith_outcomes,
        )
        assert npp.replace_arith(VariableTable()) == NPP(
            "my_npp",
            TermTuple(
                String("term"),
                ArithVariable(0, Minus(Variable("X"))),
                String("1"),
            ),
            TermTuple(Number(0), String("1")),
        )

        # substitute
        var_npp = NPP("my_npp", var_terms, var_outcomes)
        assert var_npp.substitute(
            Substitution(
                {
                    Variable("X"): String("term"),
                    Number(-3): String("f"),
                    Variable("Y"): String("1"),
                }
            )
        ) == NPP(
            "my_npp",
            ground_terms,
            ground_outcomes,
        )  # NOTE: substitution is invalid

    def test_npp_fact(self: Self):
        # make sure debug mode is enabled
        assert ground_slash.debug()

        ground_terms = TermTuple(
            String("term"),
            Number(0),
            String("1"),
        )
        ground_outcomes = TermTuple(Number(0), String("1"))
        ground_npp = NPP("my_npp", ground_terms, ground_outcomes)
        ground_rule = NPPRule(ground_npp)

        var_terms = TermTuple(
            Variable("X"),
            Number(0),
            Variable("Y"),
        )
        var_outcomes = TermTuple(
            Number(0),
            Variable("Y"),
        )
        var_npp = NPP("my_npp", var_terms, var_outcomes)
        var_rule = NPPRule(var_npp)

        # string representation
        assert str(ground_rule) == '#npp(my_npp("term",0,"1"),[0,"1"]).'
        assert str(var_rule) == "#npp(my_npp(X,0,Y),[0,Y])."
        # equality
        assert ground_rule.npp == NPP(
            "my_npp", ground_terms, ground_outcomes
        )  # TODO: head
        assert ground_rule.body == LiteralCollection()
        assert var_rule.npp == NPP("my_npp", var_terms, var_outcomes)  # TODO: head
        assert var_rule.body == LiteralCollection()
        # hashing
        assert hash(ground_rule) == hash(
            NPPRule(NPP("my_npp", ground_terms, ground_outcomes))
        )
        assert hash(var_rule) == hash(NPPRule(NPP("my_npp", var_terms, var_outcomes)))
        # ground
        assert ground_rule.ground
        assert not var_rule.ground
        # safety
        assert ground_rule.safe
        assert not var_rule.safe
        # variables
        assert ground_rule.vars() == ground_rule.global_vars() == set()
        assert (
            var_rule.vars() == var_rule.global_vars() == {Variable("X"), Variable("Y")}
        )
        # replace arithmetic terms
        arith_terms = TermTuple(
            String("term"),
            Minus(Variable("X")),
            String("1"),
        )
        arith_outcomes = TermTuple(Add(Number(-1), Number(1)), String("1"))
        rule = NPPRule(NPP("my_npp", arith_terms, arith_outcomes))
        assert rule.replace_arith() == NPPRule(
            NPP(
                "my_npp",
                TermTuple(
                    String("term"),
                    ArithVariable(0, Minus(Variable("X"))),
                    String("1"),
                ),
                TermTuple(Number(0), String("1")),
            )
        )

        # substitution
        var_npp = NPP("my_npp", var_terms, var_outcomes)
        rule = NPPRule(NPP("my_npp", var_terms, var_outcomes))
        assert rule.substitute(
            Substitution(
                {
                    Variable("X"): String("term"),
                    Number(-3): String("f"),
                    Variable("Y"): String("1"),
                }
            )
        ) == NPPRule(
            NPP("my_npp", ground_terms, ground_outcomes)
        )  # NOTE: substitution is invalid

        # rewrite aggregates
        assert rule == rule.rewrite_aggregates(0, dict())

        # assembling
        assert rule == rule.assemble_aggregates(dict())

    def test_npp_rule(self: Self):
        # make sure debug mode is enabled
        assert ground_slash.debug()

        ground_terms = TermTuple(
            String("term"),
            Number(0),
            String("1"),
        )
        ground_outcomes = TermTuple(Number(0), String("1"))
        ground_npp = NPP("my_npp", ground_terms, ground_outcomes)
        ground_rule = NPPRule(ground_npp, (PredLiteral("q", Number(1)),))

        var_terms = TermTuple(
            Variable("X"),
            Number(0),
            Variable("Y"),
        )
        var_outcomes = TermTuple(
            Number(0),
            Variable("Y"),
        )
        var_npp = NPP("my_npp", var_terms, var_outcomes)
        safe_var_rule = NPPRule(
            var_npp,
            (
                PredLiteral("q", Variable("X")),
                PredLiteral("q", Variable("Y")),
            ),
        )
        unsafe_var_rule = NPPRule(var_npp, (PredLiteral("q", Variable("X")),))

        # string representation
        assert str(ground_rule) == '#npp(my_npp("term",0,"1"),[0,"1"]) :- q(1).'
        assert str(safe_var_rule) == "#npp(my_npp(X,0,Y),[0,Y]) :- q(X),q(Y)."
        assert str(unsafe_var_rule) == "#npp(my_npp(X,0,Y),[0,Y]) :- q(X)."
        # equality
        assert ground_rule == NPPRule(ground_npp, (PredLiteral("q", Number(1)),))
        assert safe_var_rule == NPPRule(
            var_npp,
            (
                PredLiteral("q", Variable("X")),
                PredLiteral("q", Variable("Y")),
            ),
        )
        assert unsafe_var_rule == NPPRule(
            var_npp,
            (PredLiteral("q", Variable("X")),),
        )
        assert ground_rule.body == LiteralCollection(PredLiteral("q", Number(1)))
        assert ground_rule.head == NPP("my_npp", ground_terms, ground_outcomes)
        assert ground_rule.body == LiteralCollection(PredLiteral("q", Number(1)))
        # hashing
        assert hash(ground_rule) == hash(
            NPPRule(ground_npp, (PredLiteral("q", Number(1)),))
        )
        assert hash(unsafe_var_rule) == hash(
            NPPRule(
                var_npp,
                (PredLiteral("q", Variable("X")),),
            ),
        )
        assert hash(safe_var_rule) == hash(
            NPPRule(
                var_npp,
                (
                    PredLiteral("q", Variable("X")),
                    PredLiteral("q", Variable("Y")),
                ),
            ),
        )
        # ground
        assert ground_rule.ground
        assert not unsafe_var_rule.ground
        assert not safe_var_rule.ground
        # safety
        assert ground_rule.safe
        assert not unsafe_var_rule.safe
        assert safe_var_rule.safe
        # contains aggregates
        assert not ground_rule.contains_aggregates
        assert not unsafe_var_rule.contains_aggregates
        assert not safe_var_rule.contains_aggregates
        assert NPPRule(
            ground_npp,
            (AggrLiteral(AggrCount(), tuple(), Guard(RelOp.EQUAL, Number(1), False)),),
        ).contains_aggregates
        # variables
        assert ground_rule.vars() == ground_rule.global_vars() == set()
        assert (
            unsafe_var_rule.vars()
            == unsafe_var_rule.global_vars()
            == {Variable("Y"), Variable("X")}
        )
        assert (
            safe_var_rule.vars()
            == safe_var_rule.global_vars()
            == {Variable("X"), Variable("Y")}
        )
        # TODO: replace arithmetic terms

        # substitution
        assert safe_var_rule.substitute(
            Substitution({Variable("X"): String("term"), Variable("Y"): String("1")})
        ) == NPPRule(
            NPP(
                "my_npp",
                ground_terms,
                ground_outcomes,
            ),
            (PredLiteral("q", String("term")), PredLiteral("q", String("1"))),
        )
