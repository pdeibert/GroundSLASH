import unittest
from typing import Set

import ground_slash
from ground_slash.program.literals import (
    AggrCount,
    AggrLiteral,
    ChoiceBaseLiteral,
    ChoiceElemLiteral,
    ChoicePlaceholder,
    Equal,
    GreaterEqual,
    Guard,
    LiteralCollection,
    Naf,
    PredLiteral,
)
from ground_slash.program.operators import RelOp
from ground_slash.program.statements import (
    Choice,
    ChoiceBaseRule,
    ChoiceElement,
    ChoiceElemRule,
    ChoiceRule,
    Constraint,
    NormalRule,
)
from ground_slash.program.substitution import Substitution
from ground_slash.program.terms import (
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


class TestChoice(unittest.TestCase):
    def test_choice_element(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        element = ChoiceElement(
            PredLiteral("p", String("str")),
            LiteralCollection(
                PredLiteral("p", Number(0)),
                Naf(PredLiteral("q", Variable("Y"))),
            ),
        )
        # string representation
        self.assertEqual(str(element), 'p("str"):p(0),not q(Y)')
        # equality
        self.assertEqual(
            element,
            ChoiceElement(
                PredLiteral("p", String("str")),
                LiteralCollection(
                    PredLiteral("p", Number(0)),
                    Naf(PredLiteral("q", Variable("Y"))),
                ),
            ),
        )
        # head
        self.assertEqual(
            element.head,
            LiteralCollection(
                PredLiteral("p", String("str")),
            ),
        )
        # body
        self.assertEqual(
            element.body,
            LiteralCollection(
                PredLiteral("p", Number(0)),
                Naf(PredLiteral("q", Variable("Y"))),
            ),
        )
        # hashing
        self.assertEqual(
            hash(element),
            hash(
                ChoiceElement(
                    PredLiteral("p", String("str")),
                    LiteralCollection(
                        PredLiteral("p", Number(0)),
                        Naf(PredLiteral("q", Variable("Y"))),
                    ),
                ),
            ),
        )
        # ground
        self.assertFalse(element.ground)
        # positive/negative literal occurrences
        self.assertEqual(
            element.pos_occ(),
            LiteralCollection(
                PredLiteral("p", String("str")), PredLiteral("p", Number(0))
            ),
        )
        self.assertEqual(
            element.neg_occ(), LiteralCollection(PredLiteral("q", Variable("Y")))
        )
        # vars
        self.assertTrue(element.vars() == element.global_vars() == {Variable("Y")})
        # safety
        self.assertRaises(Exception, element.safety)
        # replace arithmetic terms
        self.assertEqual(element.replace_arith(VariableTable()), element)
        element = ChoiceElement(
            PredLiteral("p", String("str")),
            LiteralCollection(
                PredLiteral("p", Number(0)),
                Naf(PredLiteral("q", Minus(Variable("Y")))),
            ),
        )
        self.assertEqual(
            element.replace_arith(VariableTable()),
            ChoiceElement(
                PredLiteral("p", String("str")),
                LiteralCollection(
                    PredLiteral("p", Number(0)),
                    Naf(PredLiteral("q", ArithVariable(0, Minus(Variable("Y"))))),
                ),
            ),
        )
        # substitute
        self.assertEqual(
            element.substitute(
                Substitution({Variable("Y"): Number(1), Number(5): String("f")})
            ),  # NOTE: substitution is invalid
            ChoiceElement(
                PredLiteral("p", String("str")),
                LiteralCollection(
                    PredLiteral("p", Number(0)),
                    Naf(PredLiteral("q", Number(-1))),
                ),
            ),
        )
        # match
        self.assertRaises(Exception, element.match, element)

    def test_choice(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        ground_elements = (
            ChoiceElement(
                PredLiteral("p", Number(5)),
                LiteralCollection(
                    PredLiteral("p", String("str")), Naf(PredLiteral("q"))
                ),
            ),
            ChoiceElement(
                PredLiteral("p", Number(-3)),
                LiteralCollection(Naf(PredLiteral("p", String("str")))),
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
                PredLiteral("p", Number(5)),
                LiteralCollection(
                    PredLiteral("p", Variable("X")), Naf(PredLiteral("q"))
                ),
            ),
            ChoiceElement(
                PredLiteral("p", Number(-3)),
                LiteralCollection(Naf(PredLiteral("p", String("str")))),
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
            LiteralCollection(
                PredLiteral("p", Number(5)),
                PredLiteral("p", Number(-3)),
            ),
        )
        # body
        self.assertEqual(
            ground_choice.body,
            LiteralCollection(
                PredLiteral("p", String("str")),
                Naf(PredLiteral("q")),
                Naf(PredLiteral("p", String("str"))),
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
            LiteralCollection(
                PredLiteral("p", Number(5)),
                PredLiteral("p", Number(-3)),
                PredLiteral("p", Variable("X")),
            ),
        )
        self.assertEqual(
            var_choice.neg_occ(),
            LiteralCollection(PredLiteral("p", String("str")), PredLiteral("q")),
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
                PredLiteral("p", Number(5)),
                LiteralCollection(
                    PredLiteral("p", Minus(Variable("X"))),
                    Naf(PredLiteral("q")),
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
                        PredLiteral("p", Number(5)),
                        LiteralCollection(
                            PredLiteral("p", ArithVariable(0, Minus(Variable("X")))),
                            Naf(PredLiteral("q")),
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
                        PredLiteral("p", Number(5)),
                        LiteralCollection(
                            PredLiteral("p", Number(1)), Naf(PredLiteral("q"))
                        ),
                    ),
                    ChoiceElement(
                        PredLiteral("p", Number(-3)),
                        LiteralCollection(Naf(PredLiteral("p", String("str")))),
                    ),
                ),
                guards=Guard(RelOp.LESS, Number(1), False),
            ),
        )

    def test_choice_fact(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        ground_elements = (
            ChoiceElement(
                PredLiteral("p", Number(5)),
                LiteralCollection(
                    PredLiteral("p", String("str")), Naf(PredLiteral("q"))
                ),
            ),
            ChoiceElement(
                PredLiteral("p", Number(-3)),
                LiteralCollection(Naf(PredLiteral("p", String("str")))),
            ),
        )
        ground_choice = Choice(
            ground_elements,
            guards=Guard(RelOp.LESS, Number(3), False),
        )
        ground_rule = ChoiceRule(ground_choice)

        var_elements = (
            ChoiceElement(
                PredLiteral("p", Number(5)),
                LiteralCollection(
                    PredLiteral("p", Variable("X")), Naf(PredLiteral("q"))
                ),
            ),
            ChoiceElement(
                PredLiteral("p", Number(-3)),
                LiteralCollection(Naf(PredLiteral("p", String("str")))),
            ),
        )
        var_choice = Choice(
            var_elements, guards=Guard(RelOp.LESS, Variable("Y"), False)
        )
        var_rule = ChoiceRule(var_choice)

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
        self.assertEqual(ground_rule.body, LiteralCollection())
        self.assertEqual(
            var_rule.choice,  # TODO: head
            Choice(var_elements, guards=Guard(RelOp.LESS, Variable("Y"), False)),
        )
        self.assertEqual(var_rule.body, LiteralCollection())
        # hashing
        self.assertEqual(
            hash(ground_rule),
            hash(
                ChoiceRule(
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
                ChoiceRule(
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
                PredLiteral("p", Number(5)),
                LiteralCollection(
                    PredLiteral("p", Minus(Variable("X"))),
                    Naf(PredLiteral("q")),
                ),
            ),
        )
        rule = ChoiceRule(
            Choice(
                arith_elements,
                Guard(RelOp.EQUAL, Minus(Variable("X")), True),
            ),
        )
        self.assertEqual(
            rule.replace_arith(),
            ChoiceRule(
                Choice(
                    (
                        ChoiceElement(
                            PredLiteral("p", Number(5)),
                            LiteralCollection(
                                PredLiteral(
                                    "p", ArithVariable(0, Minus(Variable("X")))
                                ),
                                Naf(PredLiteral("q")),
                            ),
                        ),
                    ),
                    Guard(RelOp.EQUAL, ArithVariable(1, Minus(Variable("X"))), True),
                ),
            ),
        )

        # substitution
        rule = ChoiceRule(Choice(var_elements, Guard(RelOp.LESS, Variable("X"), False)))
        self.assertEqual(
            rule.substitute(
                Substitution({Variable("X"): Number(1), Number(-3): String("f")})
            ),  # NOTE: substitution is invalid
            ChoiceRule(
                Choice(
                    (
                        ChoiceElement(
                            PredLiteral("p", Number(5)),
                            LiteralCollection(
                                PredLiteral("p", Number(1)),
                                Naf(PredLiteral("q")),
                            ),
                        ),
                        ChoiceElement(
                            PredLiteral("p", Number(-3)),
                            LiteralCollection(Naf(PredLiteral("p", String("str")))),
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

        # rewrite choice
        elements = (
            ChoiceElement(
                PredLiteral("p", Variable("X")),
                LiteralCollection(PredLiteral("q", Variable("X"))),
            ),
            ChoiceElement(
                PredLiteral("p", Number(1)),
                LiteralCollection(PredLiteral("p", Number(0))),
            ),
        )
        rule = ChoiceRule(
            Choice(
                elements,
                Guard(RelOp.GREATER_OR_EQ, Number(-1), False),
            ),
        )
        target_rule = NormalRule(
            ChoicePlaceholder(
                1,
                TermTuple(),
                TermTuple(),
            ),
        )
        choice_map = dict()
        self.assertEqual(rule.rewrite_choices(1, choice_map), target_rule)
        self.assertEqual(len(choice_map), 1)

        choice, chi_literal, eps_rule, eta_rules = choice_map[1]
        self.assertEqual(choice, rule.head)

        self.assertEqual(chi_literal, target_rule.atom)
        self.assertEqual(
            eps_rule,
            ChoiceBaseRule(
                ChoiceBaseLiteral(
                    1,
                    TermTuple(),
                    TermTuple(),
                ),
                Guard(RelOp.GREATER_OR_EQ, Number(-1), False),
                None,
                LiteralCollection(
                    GreaterEqual(Number(-1), Number(0)),
                ),
            ),
        )

        self.assertEqual(len(eta_rules), 2)
        # """
        self.assertEqual(
            eta_rules[0],
            ChoiceElemRule(
                ChoiceElemLiteral(
                    1,
                    0,
                    TermTuple(Variable("X")),
                    TermTuple(),
                    TermTuple(Variable("X")),
                ),
                elements[0],
                LiteralCollection(
                    PredLiteral("q", Variable("X")),
                ),
            ),
        )
        self.assertEqual(
            eta_rules[1],
            ChoiceElemRule(
                ChoiceElemLiteral(
                    1,
                    1,
                    TermTuple(),
                    TermTuple(),
                    TermTuple(),
                ),
                elements[1],
                LiteralCollection(
                    PredLiteral("p", Number(0)),
                ),
            ),
        )

        # assembling choice
        self.assertEqual(
            target_rule.assemble_choices(
                {
                    ChoicePlaceholder(
                        1,
                        TermTuple(),
                        TermTuple(),
                    ): Choice(
                        (
                            ChoiceElement(
                                PredLiteral("p", Number(0)),
                                LiteralCollection(PredLiteral("q", Number(0))),
                            ),
                            ChoiceElement(
                                PredLiteral("p", Number(1)),
                                LiteralCollection(PredLiteral("p", Number(0))),
                            ),
                        ),
                        Guard(RelOp.GREATER_OR_EQ, Number(-1), False),
                    ),
                },
            ),
            ChoiceRule(
                Choice(
                    (
                        ChoiceElement(
                            PredLiteral("p", Number(0)),
                            LiteralCollection(PredLiteral("q", Number(0))),
                        ),
                        ChoiceElement(
                            PredLiteral("p", Number(1)),
                            LiteralCollection(PredLiteral("p", Number(0))),
                        ),
                    ),
                    Guard(RelOp.GREATER_OR_EQ, Number(-1), False),
                ),
            ),
        )  # choice is satisfiable

        self.assertEqual(
            target_rule.assemble_choices(
                dict(),
            ),
            Constraint(),
        )  # choice is unsatisfiable (yields constraint)

    def test_choice_rule(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        ground_elements = (
            ChoiceElement(
                PredLiteral("p", Number(5)),
                LiteralCollection(
                    PredLiteral("p", String("str")), Naf(PredLiteral("q"))
                ),
            ),
            ChoiceElement(
                PredLiteral("p", Number(-3)),
                LiteralCollection(Naf(PredLiteral("p", String("str")))),
            ),
        )
        ground_choice = Choice(
            ground_elements,
            guards=Guard(RelOp.LESS, Number(3), False),
        )
        ground_rule = ChoiceRule(ground_choice, (PredLiteral("q", Number(1)),))

        var_elements = (
            ChoiceElement(
                PredLiteral("p", Number(5)),
                LiteralCollection(
                    PredLiteral("p", Variable("X")), Naf(PredLiteral("q"))
                ),
            ),
            ChoiceElement(
                PredLiteral("p", Number(-3)),
                LiteralCollection(Naf(PredLiteral("p", String("str")))),
            ),
        )
        var_choice = Choice(
            var_elements, guards=Guard(RelOp.LESS, Variable("Y"), False)
        )
        safe_var_rule = ChoiceRule(
            var_choice,
            (
                PredLiteral("q", Variable("X")),
                PredLiteral("q", Variable("Y")),
            ),
        )
        unsafe_var_rule = ChoiceRule(var_choice, (PredLiteral("q", Variable("X")),))

        # string representation
        self.assertEqual(
            str(ground_rule), '3 < {p(5):p("str"),not q;p(-3):not p("str")} :- q(1).'
        )
        self.assertEqual(
            str(safe_var_rule),
            'Y < {p(5):p(X),not q;p(-3):not p("str")} :- q(X),q(Y).',
        )
        self.assertEqual(
            str(unsafe_var_rule), 'Y < {p(5):p(X),not q;p(-3):not p("str")} :- q(X).'
        )
        # self.assertEqual(str(unsafe_var_rule), "p(1) | p(X) :- q.")
        # equality
        self.assertEqual(
            ground_rule, ChoiceRule(ground_choice, (PredLiteral("q", Number(1)),))
        )
        self.assertEqual(
            safe_var_rule,
            ChoiceRule(
                var_choice,
                (
                    PredLiteral("q", Variable("X")),
                    PredLiteral("q", Variable("Y")),
                ),
            ),
        )
        self.assertEqual(
            unsafe_var_rule,
            ChoiceRule(
                var_choice,
                (PredLiteral("q", Variable("X")),),
            ),
        )
        self.assertEqual(
            ground_rule.body, LiteralCollection(PredLiteral("q", Number(1)))
        )
        self.assertEqual(
            ground_rule.head,
            Choice(
                ground_elements,
                guards=Guard(RelOp.LESS, Number(3), False),
            ),
        )
        self.assertEqual(
            ground_rule.body, LiteralCollection(PredLiteral("q", Number(1)))
        )
        # hashing
        self.assertEqual(
            hash(ground_rule),
            hash(ChoiceRule(ground_choice, (PredLiteral("q", Number(1)),))),
        )
        self.assertEqual(
            hash(unsafe_var_rule),
            hash(
                ChoiceRule(
                    var_choice,
                    (PredLiteral("q", Variable("X")),),
                ),
            ),
        )
        self.assertEqual(
            hash(safe_var_rule),
            hash(
                ChoiceRule(
                    var_choice,
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
            ChoiceRule(
                ground_choice,
                (
                    AggrLiteral(
                        AggrCount(), tuple(), Guard(RelOp.EQUAL, Number(1), False)
                    ),
                ),
            ).contains_aggregates
        )
        # variables
        self.assertTrue(ground_rule.vars() == ground_rule.global_vars() == set())
        self.assertEqual(
            unsafe_var_rule.vars(),
            {Variable("Y"), Variable("X")},
        )
        self.assertEqual(unsafe_var_rule.global_vars(), {Variable("Y"), Variable("X")})
        self.assertTrue(
            safe_var_rule.vars()
            == safe_var_rule.global_vars()
            == {Variable("X"), Variable("Y")}
        )
        # TODO: replace arithmetic terms

        var_elements = (
            ChoiceElement(
                PredLiteral("p", Number(5)),
                LiteralCollection(
                    PredLiteral("p", Variable("X")), Naf(PredLiteral("q"))
                ),
            ),
            ChoiceElement(
                PredLiteral("p", Number(-3)),
                LiteralCollection(Naf(PredLiteral("p", String("str")))),
            ),
        )
        var_choice = Choice(
            var_elements, guards=Guard(RelOp.LESS, Variable("Y"), False)
        )
        safe_var_rule = ChoiceRule(
            var_choice,
            (
                PredLiteral("q", Variable("X")),
                PredLiteral("q", Variable("Y")),
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
                            PredLiteral("p", Number(5)),
                            LiteralCollection(
                                PredLiteral("p", Number(1)),
                                Naf(PredLiteral("q")),
                            ),
                        ),
                        ChoiceElement(
                            PredLiteral("p", Number(-3)),
                            LiteralCollection(Naf(PredLiteral("p", String("str")))),
                        ),
                    ),
                    guards=Guard(RelOp.LESS, String("f"), False),
                ),
                (PredLiteral("q", Number(1)), PredLiteral("q", String("f"))),
            ),
        )

        # rewrite choice
        elements = (
            ChoiceElement(
                PredLiteral("p", Variable("X")),
                LiteralCollection(PredLiteral("q", Variable("X"))),
            ),
            ChoiceElement(
                PredLiteral("p", Number(1)),
                LiteralCollection(PredLiteral("p", Number(0))),
            ),
        )
        rule = ChoiceRule(
            Choice(
                elements,
                Guard(RelOp.GREATER_OR_EQ, Variable("Y"), False),
            ),
            (
                PredLiteral("q", Variable("Y")),
                Equal(Number(0), Variable("X")),
            ),
        )
        target_rule = NormalRule(
            ChoicePlaceholder(
                1,
                TermTuple(Variable("X"), Variable("Y")),
                TermTuple(Variable("X"), Variable("Y")),
            ),
            [PredLiteral("q", Variable("Y")), Equal(Number(0), Variable("X"))],
        )
        choice_map = dict()

        self.assertEqual(rule.rewrite_choices(1, choice_map), target_rule)
        self.assertEqual(len(choice_map), 1)

        choice, chi_literal, eps_rule, eta_rules = choice_map[1]
        self.assertEqual(choice, rule.head)

        self.assertEqual(chi_literal, target_rule.atom)
        self.assertEqual(
            eps_rule,
            ChoiceBaseRule(
                ChoiceBaseLiteral(
                    1,
                    TermTuple(Variable("X"), Variable("Y")),
                    TermTuple(Variable("X"), Variable("Y")),
                ),
                Guard(RelOp.GREATER_OR_EQ, Variable("Y"), False),
                None,
                LiteralCollection(
                    GreaterEqual(Variable("Y"), Number(0)),
                    PredLiteral("q", Variable("Y")),
                    Equal(Number(0), Variable("X")),
                ),
            ),
        )

        self.assertEqual(len(eta_rules), 2)
        self.assertEqual(
            eta_rules[0],
            ChoiceElemRule(
                ChoiceElemLiteral(
                    1,
                    0,
                    TermTuple(),
                    TermTuple(Variable("X"), Variable("Y")),
                    TermTuple(Variable("X"), Variable("Y")),
                ),
                elements[0],
                LiteralCollection(
                    PredLiteral("q", Variable("X")),
                    PredLiteral("q", Variable("Y")),
                    Equal(Number(0), Variable("X")),
                ),
            ),
        )
        self.assertEqual(
            eta_rules[1],
            ChoiceElemRule(
                ChoiceElemLiteral(
                    1,
                    1,
                    TermTuple(),
                    TermTuple(Variable("X"), Variable("Y")),
                    TermTuple(Variable("X"), Variable("Y")),
                ),
                elements[1],
                LiteralCollection(
                    PredLiteral("p", Number(0)),
                    PredLiteral("q", Variable("Y")),
                    Equal(Number(0), Variable("X")),
                ),
            ),
        )

        # assembling choice
        self.assertEqual(
            target_rule.assemble_choices(
                {
                    ChoicePlaceholder(
                        1,
                        TermTuple(Variable("X"), Variable("Y")),
                        TermTuple(Variable("X"), Variable("Y")),
                    ): Choice(
                        (
                            ChoiceElement(
                                PredLiteral("p", Number(0)),
                                LiteralCollection(PredLiteral("q", Number(0))),
                            ),
                            ChoiceElement(
                                PredLiteral("p", Number(1)),
                                LiteralCollection(PredLiteral("p", Number(0))),
                            ),
                        ),
                        Guard(RelOp.GREATER_OR_EQ, Number(-1), False),
                    ),
                },
            ),
            ChoiceRule(
                Choice(
                    (
                        ChoiceElement(
                            PredLiteral("p", Number(0)),
                            LiteralCollection(PredLiteral("q", Number(0))),
                        ),
                        ChoiceElement(
                            PredLiteral("p", Number(1)),
                            LiteralCollection(PredLiteral("p", Number(0))),
                        ),
                    ),
                    Guard(RelOp.GREATER_OR_EQ, Number(-1), False),
                ),
                (
                    PredLiteral("q", Variable("Y")),
                    Equal(Number(0), Variable("X")),
                ),
            ),
        )  # choice is satisfiable

        self.assertEqual(
            target_rule.assemble_choices(
                dict(),
            ),
            Constraint(
                PredLiteral("q", Variable("Y")),
                Equal(Number(0), Variable("X")),
            ),
        )  # choice is unsatisfiable (yields constraint)

        # TODO: propagate


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
