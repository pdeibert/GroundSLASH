import unittest
from typing import Set

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
    def __init__(self, vars: Set["Variable"]) -> None:
        self.vars = vars

    def global_vars(self) -> Set["Variable"]:
        return self.vars


class DummyRule:  # pragma: no cover
    def __init__(self, vars: Set["Variable"]) -> None:
        self.body = DummyBody(vars)


class TestNPP(unittest.TestCase):
    def test_npp(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

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
        self.assertEqual(ground_npp.terms, ground_terms)
        self.assertEqual(ground_npp.outcomes, ground_outcomes)
        self.assertEqual(ground_npp.atoms, ground_atoms)
        self.assertEqual(str(ground_npp), '#npp(my_npp("term",0,"1"),[0,"1"])')
        # equality
        self.assertEqual(
            ground_npp,
            NPP(
                "my_npp",
                ground_terms,
                ground_outcomes,
            ),
        )
        # hashing
        self.assertEqual(
            hash(ground_npp),
            hash(
                NPP(
                    "my_npp",
                    ground_terms,
                    ground_outcomes,
                )
            ),
        )
        # ground
        self.assertTrue(ground_npp.ground)
        self.assertFalse(var_npp.ground)
        # variables
        self.assertTrue(
            ground_npp.vars()
            == ground_npp.global_vars(DummyRule({Variable("Y")}))
            == set()
        )
        self.assertTrue(
            var_npp.vars()
            == var_npp.global_vars(DummyRule({Variable("Y")}))
            == {Variable("X"), Variable("Y")}
        )
        # positive/negative literal occurrences
        self.assertEqual(
            var_npp.pos_occ(),
            var_atoms,
        )
        self.assertEqual(
            var_npp.neg_occ(),
            LiteralCollection(),
        )

        # safety characterization
        self.assertRaises(Exception, var_npp.safety)
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
        self.assertEqual(
            npp.replace_arith(VariableTable()),
            NPP(
                "my_npp",
                TermTuple(
                    String("term"),
                    ArithVariable(0, Minus(Variable("X"))),
                    String("1"),
                ),
                TermTuple(Number(0), String("1")),
            ),
        )

        # substitute
        var_npp = NPP("my_npp", var_terms, var_outcomes)
        self.assertEqual(
            var_npp.substitute(
                Substitution(
                    {
                        Variable("X"): String("term"),
                        Number(-3): String("f"),
                        Variable("Y"): String("1"),
                    }
                )
            ),  # NOTE: substitution is invalid
            NPP(
                "my_npp",
                ground_terms,
                ground_outcomes,
            ),
        )

    def test_npp_fact(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

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
        self.assertEqual(str(ground_rule), '#npp(my_npp("term",0,"1"),[0,"1"]).')
        self.assertEqual(str(var_rule), "#npp(my_npp(X,0,Y),[0,Y]).")
        # equality
        self.assertEqual(
            ground_rule.npp, NPP("my_npp", ground_terms, ground_outcomes)  # TODO: head
        )
        self.assertEqual(ground_rule.body, LiteralCollection())
        self.assertEqual(
            var_rule.npp,  # TODO: head
            NPP("my_npp", var_terms, var_outcomes),
        )
        self.assertEqual(var_rule.body, LiteralCollection())
        # hashing
        self.assertEqual(
            hash(ground_rule),
            hash(NPPRule(NPP("my_npp", ground_terms, ground_outcomes))),
        )
        self.assertEqual(
            hash(var_rule),
            hash(NPPRule(NPP("my_npp", var_terms, var_outcomes))),
        )
        # ground
        self.assertTrue(ground_rule.ground)
        self.assertFalse(var_rule.ground)
        # safety
        self.assertTrue(ground_rule.safe)
        self.assertFalse(var_rule.safe)
        # variables
        self.assertTrue(ground_rule.vars() == ground_rule.global_vars() == set())
        self.assertTrue(
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
        self.assertEqual(
            rule.replace_arith(),
            NPPRule(
                NPP(
                    "my_npp",
                    TermTuple(
                        String("term"),
                        ArithVariable(0, Minus(Variable("X"))),
                        String("1"),
                    ),
                    TermTuple(Number(0), String("1")),
                )
            ),
        )

        # substitution
        var_npp = NPP("my_npp", var_terms, var_outcomes)
        rule = NPPRule(NPP("my_npp", var_terms, var_outcomes))
        self.assertEqual(
            rule.substitute(
                Substitution(
                    {
                        Variable("X"): String("term"),
                        Number(-3): String("f"),
                        Variable("Y"): String("1"),
                    }
                )
            ),  # NOTE: substitution is invalid
            NPPRule(NPP("my_npp", ground_terms, ground_outcomes)),
        )  # NOTE: substitution is invalid

        # rewrite aggregates
        self.assertEqual(rule, rule.rewrite_aggregates(0, dict()))

        # assembling
        self.assertEqual(rule, rule.assemble_aggregates(dict()))

    def test_npp_rule(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

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
        self.assertEqual(
            str(ground_rule), '#npp(my_npp("term",0,"1"),[0,"1"]) :- q(1).'
        )
        self.assertEqual(str(safe_var_rule), "#npp(my_npp(X,0,Y),[0,Y]) :- q(X),q(Y).")
        self.assertEqual(str(unsafe_var_rule), "#npp(my_npp(X,0,Y),[0,Y]) :- q(X).")
        # equality
        self.assertEqual(
            ground_rule, NPPRule(ground_npp, (PredLiteral("q", Number(1)),))
        )
        self.assertEqual(
            safe_var_rule,
            NPPRule(
                var_npp,
                (
                    PredLiteral("q", Variable("X")),
                    PredLiteral("q", Variable("Y")),
                ),
            ),
        )
        self.assertEqual(
            unsafe_var_rule,
            NPPRule(
                var_npp,
                (PredLiteral("q", Variable("X")),),
            ),
        )
        self.assertEqual(
            ground_rule.body, LiteralCollection(PredLiteral("q", Number(1)))
        )
        self.assertEqual(
            ground_rule.head,
            NPP("my_npp", ground_terms, ground_outcomes),
        )
        self.assertEqual(
            ground_rule.body, LiteralCollection(PredLiteral("q", Number(1)))
        )
        # hashing
        self.assertEqual(
            hash(ground_rule),
            hash(NPPRule(ground_npp, (PredLiteral("q", Number(1)),))),
        )
        self.assertEqual(
            hash(unsafe_var_rule),
            hash(
                NPPRule(
                    var_npp,
                    (PredLiteral("q", Variable("X")),),
                ),
            ),
        )
        self.assertEqual(
            hash(safe_var_rule),
            hash(
                NPPRule(
                    var_npp,
                    (
                        PredLiteral("q", Variable("X")),
                        PredLiteral("q", Variable("Y")),
                    ),
                ),
            ),
        )
        # ground
        self.assertTrue(ground_rule.ground)
        self.assertFalse(unsafe_var_rule.ground)
        self.assertFalse(safe_var_rule.ground)
        # safety
        self.assertTrue(ground_rule.safe)
        self.assertFalse(unsafe_var_rule.safe)
        self.assertTrue(safe_var_rule.safe)
        # contains aggregates
        self.assertFalse(ground_rule.contains_aggregates)
        self.assertFalse(unsafe_var_rule.contains_aggregates)
        self.assertFalse(safe_var_rule.contains_aggregates)
        self.assertTrue(
            NPPRule(
                ground_npp,
                (
                    AggrLiteral(
                        AggrCount(), tuple(), Guard(RelOp.EQUAL, Number(1), False)
                    ),
                ),
            ).contains_aggregates
        )
        # variables
        self.assertTrue(ground_rule.vars() == ground_rule.global_vars() == set())
        self.assertTrue(
            unsafe_var_rule.vars()
            == unsafe_var_rule.global_vars()
            == {Variable("Y"), Variable("X")}
        )
        self.assertTrue(
            safe_var_rule.vars()
            == safe_var_rule.global_vars()
            == {Variable("X"), Variable("Y")}
        )
        # TODO: replace arithmetic terms

        # substitution
        self.assertEqual(
            safe_var_rule.substitute(
                Substitution(
                    {Variable("X"): String("term"), Variable("Y"): String("1")}
                )
            ),
            NPPRule(
                NPP(
                    "my_npp",
                    ground_terms,
                    ground_outcomes,
                ),
                (PredLiteral("q", String("term")), PredLiteral("q", String("1"))),
            ),
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
