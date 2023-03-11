import unittest
from typing import Set

import aspy
from aspy.program.literals import (
    AggregateCount,
    AggregateLiteral,
    Guard,
    LiteralTuple,
    Naf,
    PredicateLiteral,
)
from aspy.program.operators import RelOp
from aspy.program.statements import Choice, ChoiceElement, ChoiceFact, ChoiceRule
from aspy.program.substitution import Substitution
from aspy.program.terms import ArithVariable, Minus, Number, String, Variable
from aspy.program.variable_table import VariableTable


class DummyRule:
    def __init__(self, vars: Set["Variable"]) -> None:
        self.vars = vars

    def global_vars(self) -> Set["Variable"]:
        return self.vars


class TestChoice(unittest.TestCase):
    def test_choice_element(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        element = ChoiceElement(
            PredicateLiteral("p", String("str")),
            LiteralTuple(
                PredicateLiteral("p", Number(0)),
                Naf(PredicateLiteral("q", Variable("Y"))),
            ),
        )
        # string representation
        self.assertEqual(str(element), 'p("str"):p(0),not q(Y)')
        # equality
        self.assertEqual(
            element,
            ChoiceElement(
                PredicateLiteral("p", String("str")),
                LiteralTuple(
                    PredicateLiteral("p", Number(0)),
                    Naf(PredicateLiteral("q", Variable("Y"))),
                ),
            ),
        )
        # head
        self.assertEqual(
            element.head,
            LiteralTuple(
                PredicateLiteral("p", String("str")),
            ),
        )
        # body
        self.assertEqual(
            element.body,
            LiteralTuple(
                PredicateLiteral("p", Number(0)),
                Naf(PredicateLiteral("q", Variable("Y"))),
            ),
        )
        # hashing
        self.assertEqual(
            hash(element),
            hash(
                ChoiceElement(
                    PredicateLiteral("p", String("str")),
                    LiteralTuple(
                        PredicateLiteral("p", Number(0)),
                        Naf(PredicateLiteral("q", Variable("Y"))),
                    ),
                ),
            ),
        )
        # ground
        self.assertFalse(element.ground)
        # positive/negative literal occurrences
        self.assertEqual(
            element.pos_occ(),
            {PredicateLiteral("p", String("str")), PredicateLiteral("p", Number(0))},
        )
        self.assertEqual(element.neg_occ(), {PredicateLiteral("q", Variable("Y"))})
        # vars
        self.assertTrue(element.vars() == element.global_vars() == {Variable("Y")})
        # safety
        self.assertRaises(Exception, element.safety)
        # replace arithmetic terms
        self.assertEqual(element.replace_arith(VariableTable()), element)
        element = ChoiceElement(
            PredicateLiteral("p", String("str")),
            LiteralTuple(
                PredicateLiteral("p", Number(0)),
                Naf(PredicateLiteral("q", Minus(Variable("Y")))),
            ),
        )
        self.assertEqual(
            element.replace_arith(VariableTable()),
            ChoiceElement(
                PredicateLiteral("p", String("str")),
                LiteralTuple(
                    PredicateLiteral("p", Number(0)),
                    Naf(PredicateLiteral("q", ArithVariable(0, Minus(Variable("Y"))))),
                ),
            ),
        )
        # substitute
        self.assertEqual(
            element.substitute(
                Substitution({Variable("Y"): Number(1), Number(5): String("f")})
            ),  # NOTE: substitution is invalid
            ChoiceElement(
                PredicateLiteral("p", String("str")),
                LiteralTuple(
                    PredicateLiteral("p", Number(0)),
                    Naf(PredicateLiteral("q", Minus(Number(1)))),
                ),
            ),
        )
        # match
        self.assertRaises(Exception, element.match, element)

    def test_choice(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        ground_elements = (
            ChoiceElement(
                PredicateLiteral("p", Number(5)),
                LiteralTuple(
                    PredicateLiteral("p", String("str")), Naf(PredicateLiteral("q"))
                ),
            ),
            ChoiceElement(
                PredicateLiteral("p", Number(-3)),
                LiteralTuple(Naf(PredicateLiteral("p", String("str")))),
            ),
        )

        # no guards
        ground_choice = Choice(ground_elements, guards=())
        self.assertEqual(ground_choice.lguard, None)
        self.assertEqual(ground_choice.rguard, None)
        self.assertEqual(ground_choice.guards, (None, None))
        self.assertEqual(str(ground_choice), '{p(5):p("str"),not q;p(-3):not p("str")}')
        # left guard only
        ground_choice = Choice(
            ground_elements, guards=Guard(RelOp.LESS, Number(3), False)
        )
        self.assertEqual(ground_choice.lguard, Guard(RelOp.LESS, Number(3), False))
        self.assertEqual(ground_choice.rguard, None)
        self.assertEqual(
            ground_choice.guards, (Guard(RelOp.LESS, Number(3), False), None)
        )
        self.assertEqual(
            str(ground_choice), '3 < {p(5):p("str"),not q;p(-3):not p("str")}'
        )
        # right guard only
        ground_choice = Choice(ground_elements, Guard(RelOp.LESS, Number(3), True))
        self.assertEqual(ground_choice.lguard, None)
        self.assertEqual(ground_choice.rguard, Guard(RelOp.LESS, Number(3), True))
        self.assertEqual(
            ground_choice.guards, (None, Guard(RelOp.LESS, Number(3), True))
        )
        self.assertEqual(
            str(ground_choice), '{p(5):p("str"),not q;p(-3):not p("str")} < 3'
        )
        # both guards
        ground_choice = Choice(
            ground_elements,
            guards=(
                Guard(RelOp.LESS, Number(3), False),
                Guard(RelOp.LESS, Number(3), True),
            ),
        )
        self.assertEqual(ground_choice.lguard, Guard(RelOp.LESS, Number(3), False))
        self.assertEqual(ground_choice.rguard, Guard(RelOp.LESS, Number(3), True))
        self.assertEqual(
            ground_choice.guards,
            (Guard(RelOp.LESS, Number(3), False), Guard(RelOp.LESS, Number(3), True)),
        )
        self.assertEqual(
            str(ground_choice), '3 < {p(5):p("str"),not q;p(-3):not p("str")} < 3'
        )

        var_elements = (
            ChoiceElement(
                PredicateLiteral("p", Number(5)),
                LiteralTuple(
                    PredicateLiteral("p", Variable("X")), Naf(PredicateLiteral("q"))
                ),
            ),
            ChoiceElement(
                PredicateLiteral("p", Number(-3)),
                LiteralTuple(Naf(PredicateLiteral("p", String("str")))),
            ),
        )
        var_choice = Choice(
            var_elements, guards=Guard(RelOp.LESS, Variable("Y"), False)
        )

        # equality
        self.assertEqual(
            ground_choice,
            Choice(
                ground_elements,
                guards=(
                    Guard(RelOp.LESS, Number(3), False),
                    Guard(RelOp.LESS, Number(3), True),
                ),
            ),
        )
        # hashing
        self.assertEqual(
            hash(ground_choice),
            hash(
                Choice(
                    ground_elements,
                    guards=(
                        Guard(RelOp.LESS, Number(3), False),
                        Guard(RelOp.LESS, Number(3), True),
                    ),
                )
            ),
        )
        # head
        self.assertEqual(
            ground_choice.head,
            LiteralTuple(
                PredicateLiteral("p", Number(5)),
                PredicateLiteral("p", Number(-3)),
            ),
        )
        # body
        self.assertEqual(
            ground_choice.body,
            LiteralTuple(
                PredicateLiteral("p", String("str")),
                Naf(PredicateLiteral("q")),
                Naf(PredicateLiteral("p", String("str"))),
            ),
        )
        # ground
        self.assertTrue(ground_choice.ground)
        self.assertFalse(var_choice.ground)
        # variables
        self.assertTrue(
            ground_choice.invars()
            == ground_choice.outvars()
            == ground_choice.vars()
            == ground_choice.global_vars(DummyRule({Variable("Y")}))
            == set()
        )
        self.assertEqual(var_choice.invars(), {Variable("X")})
        self.assertEqual(var_choice.outvars(), {Variable("Y")})
        self.assertEqual(var_choice.vars(), {Variable("X"), Variable("Y")})
        self.assertEqual(
            var_choice.global_vars(DummyRule({Variable("Y")})), {Variable("Y")}
        )
        # self.assertEqual(var_choice.global_vars(), {Variable("X"), Variable("Y")})
        # positive/negative literal occurrences
        self.assertEqual(
            var_choice.pos_occ(),
            {
                PredicateLiteral("p", Number(5)),
                PredicateLiteral("p", Number(-3)),
                PredicateLiteral("p", Variable("X")),
            },
        )
        self.assertEqual(
            var_choice.neg_occ(),
            {PredicateLiteral("p", String("str")), PredicateLiteral("q")},
        )
        # evaluation
        self.assertTrue(
            Choice.eval(
                ground_elements,
                # satisfiable lower bound
                guards=(Guard(RelOp.LESS, Number(1), False), None),
            )
        )
        self.assertFalse(
            Choice.eval(
                ground_elements,
                # unsatisfiable lower bound
                guards=(Guard(RelOp.LESS, Number(2), False), None),
            )
        )
        self.assertTrue(
            Choice.eval(
                ground_elements,
                # satisfiable lower bound
                guards=(Guard(RelOp.LESS_OR_EQ, Number(2), False), None),
            )
        )
        self.assertFalse(
            Choice.eval(
                ground_elements,
                # unsatisfiable lower bound
                guards=(Guard(RelOp.LESS_OR_EQ, Number(3), False), None),
            )
        )
        self.assertTrue(
            Choice.eval(
                ground_elements,
                # satisfiable upper bound
                guards=(Guard(RelOp.GREATER, Number(1), False), None),
            )
        )
        self.assertFalse(
            Choice.eval(
                ground_elements,
                # unsatisfiable upper bound
                guards=(Guard(RelOp.GREATER, Number(0), False), None),
            )
        )
        self.assertTrue(
            Choice.eval(
                ground_elements,
                # satisfiable upper bound
                guards=(Guard(RelOp.GREATER_OR_EQ, Number(0), False), None),
            )
        )
        self.assertFalse(
            Choice.eval(
                ground_elements,
                # unsatisfiable upper bound
                guards=(Guard(RelOp.GREATER_OR_EQ, Number(-1), False), None),
            )
        )
        self.assertTrue(
            Choice.eval(
                ground_elements,
                # satisfiable equality bound
                guards=(Guard(RelOp.EQUAL, Number(2), False), None),
            )
        )
        self.assertFalse(
            Choice.eval(
                ground_elements,
                # unsatisfiable equality bound
                guards=(Guard(RelOp.EQUAL, Number(-1), False), None),
            )
        )
        self.assertFalse(
            Choice.eval(
                ground_elements,
                # unsatisfiable equality bound
                guards=(Guard(RelOp.EQUAL, Number(3), False), None),
            )
        )
        self.assertTrue(
            Choice.eval(
                # no elements
                tuple(),
                # satisfiable unequality bound
                guards=(Guard(RelOp.UNEQUAL, Number(-1), False), None),
            )
        )
        self.assertFalse(
            Choice.eval(
                # no elements
                tuple(),
                # unsatisfiable unequality bound
                guards=(Guard(RelOp.UNEQUAL, Number(0), False), None),
            )
        )
        self.assertTrue(
            Choice.eval(
                ground_elements,
                # satisfiable unequality bound
                guards=(Guard(RelOp.UNEQUAL, Number(-1), False), None),
            )
        )
        self.assertTrue(
            Choice.eval(
                ground_elements,
                # satisfiable unequality bound
                guards=(Guard(RelOp.UNEQUAL, Number(0), False), None),
            )
        )
        # TODO: test evaluation with two guards

        # safety characterization
        self.assertRaises(Exception, var_choice.safety)
        # replace arithmetic terms
        arith_elements = (
            ChoiceElement(
                PredicateLiteral("p", Number(5)),
                LiteralTuple(
                    PredicateLiteral("p", Minus(Variable("X"))),
                    Naf(PredicateLiteral("q")),
                ),
            ),
        )
        choice = Choice(
            arith_elements,
            Guard(RelOp.EQUAL, Minus(Variable("X")), True),
        )
        self.assertEqual(
            choice.replace_arith(VariableTable()),
            Choice(
                (
                    ChoiceElement(
                        PredicateLiteral("p", Number(5)),
                        LiteralTuple(
                            PredicateLiteral(
                                "p", ArithVariable(0, Minus(Variable("X")))
                            ),
                            Naf(PredicateLiteral("q")),
                        ),
                    ),
                ),
                Guard(RelOp.EQUAL, ArithVariable(1, Minus(Variable("X"))), True),
            ),
        )

        # substitute
        var_choice = Choice(var_elements, Guard(RelOp.LESS, Variable("X"), False))
        self.assertEqual(
            var_choice.substitute(
                Substitution({Variable("X"): Number(1), Number(-3): String("f")})
            ),  # NOTE: substitution is invalid
            Choice(
                (
                    ChoiceElement(
                        PredicateLiteral("p", Number(5)),
                        LiteralTuple(
                            PredicateLiteral("p", Number(1)), Naf(PredicateLiteral("q"))
                        ),
                    ),
                    ChoiceElement(
                        PredicateLiteral("p", Number(-3)),
                        LiteralTuple(Naf(PredicateLiteral("p", String("str")))),
                    ),
                ),
                guards=Guard(RelOp.LESS, Number(1), False),
            ),
        )

    def test_choice_fact(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        ground_elements = (
            ChoiceElement(
                PredicateLiteral("p", Number(5)),
                LiteralTuple(
                    PredicateLiteral("p", String("str")), Naf(PredicateLiteral("q"))
                ),
            ),
            ChoiceElement(
                PredicateLiteral("p", Number(-3)),
                LiteralTuple(Naf(PredicateLiteral("p", String("str")))),
            ),
        )
        ground_choice = Choice(
            ground_elements,
            guards=Guard(RelOp.LESS, Number(3), False),
        )
        ground_rule = ChoiceFact(ground_choice)

        var_elements = (
            ChoiceElement(
                PredicateLiteral("p", Number(5)),
                LiteralTuple(
                    PredicateLiteral("p", Variable("X")), Naf(PredicateLiteral("q"))
                ),
            ),
            ChoiceElement(
                PredicateLiteral("p", Number(-3)),
                LiteralTuple(Naf(PredicateLiteral("p", String("str")))),
            ),
        )
        var_choice = Choice(
            var_elements, guards=Guard(RelOp.LESS, Variable("Y"), False)
        )
        var_rule = ChoiceFact(var_choice)

        # string representation
        self.assertEqual(
            str(ground_rule), '3 < {p(5):p("str"),not q;p(-3):not p("str")}.'
        )
        self.assertEqual(str(var_rule), 'Y < {p(5):p(X),not q;p(-3):not p("str")}.')
        # equality
        self.assertEqual(
            ground_rule.choice,  # TODO: head
            Choice(
                ground_elements,
                guards=Guard(RelOp.LESS, Number(3), False),
            ),
        )
        self.assertEqual(ground_rule.body, LiteralTuple())
        self.assertEqual(
            var_rule.choice,  # TODO: head
            Choice(var_elements, guards=Guard(RelOp.LESS, Variable("Y"), False)),
        )
        self.assertEqual(var_rule.body, LiteralTuple())
        # hashing
        self.assertEqual(
            hash(ground_rule),
            hash(
                ChoiceFact(
                    Choice(
                        ground_elements,
                        guards=Guard(RelOp.LESS, Number(3), False),
                    ),
                )
            ),
        )
        self.assertEqual(
            hash(var_rule),
            hash(
                ChoiceFact(
                    Choice(
                        var_elements, guards=Guard(RelOp.LESS, Variable("Y"), False)
                    ),
                )
            ),
        )
        # ground
        self.assertTrue(ground_rule.ground)
        self.assertFalse(var_rule.ground)
        # safety
        self.assertTrue(ground_rule.safe)
        self.assertFalse(var_rule.safe)
        # variables
        self.assertTrue(ground_rule.vars() == ground_rule.global_vars() == set())
        self.assertEqual(var_rule.vars(), {Variable("X"), Variable("Y")})
        # self.assertTrue(
        #    var_rule.vars() == var_rule.global_vars() == {Variable("X"), Variable("Y")}
        # )
        self.assertEqual(var_rule.global_vars(), {Variable("Y")})
        # replace arithmetic terms
        arith_elements = (
            ChoiceElement(
                PredicateLiteral("p", Number(5)),
                LiteralTuple(
                    PredicateLiteral("p", Minus(Variable("X"))),
                    Naf(PredicateLiteral("q")),
                ),
            ),
        )
        rule = ChoiceFact(
            Choice(
                arith_elements,
                Guard(RelOp.EQUAL, Minus(Variable("X")), True),
            ),
        )
        self.assertEqual(
            rule.replace_arith(),
            ChoiceFact(
                Choice(
                    (
                        ChoiceElement(
                            PredicateLiteral("p", Number(5)),
                            LiteralTuple(
                                PredicateLiteral(
                                    "p", ArithVariable(0, Minus(Variable("X")))
                                ),
                                Naf(PredicateLiteral("q")),
                            ),
                        ),
                    ),
                    Guard(RelOp.EQUAL, ArithVariable(1, Minus(Variable("X"))), True),
                ),
            ),
        )

        # substitution
        rule = ChoiceFact(Choice(var_elements, Guard(RelOp.LESS, Variable("X"), False)))
        self.assertEqual(
            rule.substitute(
                Substitution({Variable("X"): Number(1), Number(-3): String("f")})
            ),  # NOTE: substitution is invalid
            ChoiceFact(
                Choice(
                    (
                        ChoiceElement(
                            PredicateLiteral("p", Number(5)),
                            LiteralTuple(
                                PredicateLiteral("p", Number(1)),
                                Naf(PredicateLiteral("q")),
                            ),
                        ),
                        ChoiceElement(
                            PredicateLiteral("p", Number(-3)),
                            LiteralTuple(Naf(PredicateLiteral("p", String("str")))),
                        ),
                    ),
                    guards=Guard(RelOp.LESS, Number(1), False),
                ),
            ),
        )  # NOTE: substitution is invalid

        # rewrite aggregates
        self.assertEqual(rule, rule.rewrite_aggregates(0, dict()))

        # assembling
        self.assertEqual(rule, rule.assemble_aggregates(dict()))

        # TODO: propagate

    def test_choice_rule(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        # invalid initialization
        self.assertRaises(
            ValueError,
            ChoiceRule,
            Choice(tuple()),
            tuple(),
        )  # not enough literals

        ground_elements = (
            ChoiceElement(
                PredicateLiteral("p", Number(5)),
                LiteralTuple(
                    PredicateLiteral("p", String("str")), Naf(PredicateLiteral("q"))
                ),
            ),
            ChoiceElement(
                PredicateLiteral("p", Number(-3)),
                LiteralTuple(Naf(PredicateLiteral("p", String("str")))),
            ),
        )
        ground_choice = Choice(
            ground_elements,
            guards=Guard(RelOp.LESS, Number(3), False),
        )
        ground_rule = ChoiceRule(ground_choice, (PredicateLiteral("q", Number(1)),))

        var_elements = (
            ChoiceElement(
                PredicateLiteral("p", Number(5)),
                LiteralTuple(
                    PredicateLiteral("p", Variable("X")), Naf(PredicateLiteral("q"))
                ),
            ),
            ChoiceElement(
                PredicateLiteral("p", Number(-3)),
                LiteralTuple(Naf(PredicateLiteral("p", String("str")))),
            ),
        )
        var_choice = Choice(
            var_elements, guards=Guard(RelOp.LESS, Variable("Y"), False)
        )
        safe_var_rule = ChoiceRule(
            var_choice,
            (
                PredicateLiteral("q", Variable("X")),
                PredicateLiteral("q", Variable("Y")),
            ),
        )
        unsafe_var_rule = ChoiceRule(
            var_choice, (PredicateLiteral("q", Variable("X")),)
        )

        # string representation
        self.assertEqual(
            str(ground_rule), '3 < {p(5):p("str"),not q;p(-3):not p("str")} :- q(1).'
        )
        self.assertEqual(
            str(safe_var_rule),
            'Y < {p(5):p(X),not q;p(-3):not p("str")} :- q(X), q(Y).',
        )
        self.assertEqual(
            str(unsafe_var_rule), 'Y < {p(5):p(X),not q;p(-3):not p("str")} :- q(X).'
        )
        # self.assertEqual(str(unsafe_var_rule), "p(1) | p(X) :- q.")
        # equality
        self.assertEqual(
            ground_rule, ChoiceRule(ground_choice, (PredicateLiteral("q", Number(1)),))
        )
        self.assertEqual(
            safe_var_rule,
            ChoiceRule(
                var_choice,
                (
                    PredicateLiteral("q", Variable("X")),
                    PredicateLiteral("q", Variable("Y")),
                ),
            ),
        )
        self.assertEqual(
            unsafe_var_rule,
            ChoiceRule(
                var_choice,
                (PredicateLiteral("q", Variable("X")),),
            ),
        )
        self.assertEqual(
            ground_rule.body, LiteralTuple(PredicateLiteral("q", Number(1)))
        )
        self.assertEqual(
            ground_rule.head,
            Choice(
                ground_elements,
                guards=Guard(RelOp.LESS, Number(3), False),
            ),
        )
        self.assertEqual(
            ground_rule.body, LiteralTuple(PredicateLiteral("q", Number(1)))
        )
        # hashing
        self.assertEqual(
            hash(ground_rule),
            hash(ChoiceRule(ground_choice, (PredicateLiteral("q", Number(1)),))),
        )
        self.assertEqual(
            hash(unsafe_var_rule),
            hash(
                ChoiceRule(
                    var_choice,
                    (PredicateLiteral("q", Variable("X")),),
                ),
            ),
        )
        self.assertEqual(
            hash(safe_var_rule),
            hash(
                ChoiceRule(
                    var_choice,
                    (
                        PredicateLiteral("q", Variable("X")),
                        PredicateLiteral("q", Variable("Y")),
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
            ChoiceRule(
                ground_choice,
                (
                    AggregateLiteral(
                        AggregateCount(), tuple(), Guard(RelOp.EQUAL, Number(1), False)
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

        var_elements = (
            ChoiceElement(
                PredicateLiteral("p", Number(5)),
                LiteralTuple(
                    PredicateLiteral("p", Variable("X")), Naf(PredicateLiteral("q"))
                ),
            ),
            ChoiceElement(
                PredicateLiteral("p", Number(-3)),
                LiteralTuple(Naf(PredicateLiteral("p", String("str")))),
            ),
        )
        var_choice = Choice(
            var_elements, guards=Guard(RelOp.LESS, Variable("Y"), False)
        )
        safe_var_rule = ChoiceRule(
            var_choice,
            (
                PredicateLiteral("q", Variable("X")),
                PredicateLiteral("q", Variable("Y")),
            ),
        )

        # substitution
        self.assertEqual(
            safe_var_rule.substitute(
                Substitution({Variable("X"): Number(1), Variable("Y"): String("f")})
            ),
            ChoiceRule(
                Choice(
                    (
                        ChoiceElement(
                            PredicateLiteral("p", Number(5)),
                            LiteralTuple(
                                PredicateLiteral("p", Number(1)),
                                Naf(PredicateLiteral("q")),
                            ),
                        ),
                        ChoiceElement(
                            PredicateLiteral("p", Number(-3)),
                            LiteralTuple(Naf(PredicateLiteral("p", String("str")))),
                        ),
                    ),
                    guards=Guard(RelOp.LESS, String("f"), False),
                ),
                (PredicateLiteral("q", Number(1)), PredicateLiteral("q", String("f"))),
            ),
        )

        # TODO: rewrite aggregates
        # TODO: assembling aggregates
        # TODO: propagate


if __name__ == "__main__":
    unittest.main()
