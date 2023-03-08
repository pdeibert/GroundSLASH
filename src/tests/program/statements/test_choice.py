import unittest
from typing import Set

import aspy
from aspy.program.literals import Guard, LiteralTuple, Naf, PredicateLiteral
from aspy.program.operators import RelOp
from aspy.program.safety_characterization import SafetyRule, SafetyTriplet
from aspy.program.statements import Choice, ChoiceElement, ChoiceFact, ChoiceRule
from aspy.program.substitution import Substitution
from aspy.program.terms import (
    ArithVariable,
    Infimum,
    Minus,
    Number,
    String,
    Supremum,
    TermTuple,
    Variable,
)
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

    """
    def test_aggregate_count(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        aggr_func = AggregateCount()
        # equality
        self.assertEqual(aggr_func, AggregateCount())
        # hashing
        self.assertEqual(hash(aggr_func), hash(AggregateCount()))
        # string representation
        self.assertEqual(str(aggr_func), "#count")
        # base value
        self.assertEqual(aggr_func.base(), Number(0))
        # evaluation
        self.assertEqual(
            aggr_func.eval({TermTuple(Number(5)), TermTuple(Number(-3))}), Number(2)
        )

        # ----- propagation -----
        element_instances = {
            AggregateElement(
                TermTuple(Number(0)), LiteralTuple(PredicateLiteral("p", Number(0)))
            ),
            AggregateElement(
                TermTuple(Number(1)),
                LiteralTuple(PredicateLiteral("p", Number(1))),
            ),
        }

        # >, >=
        # TODO: correct ???
        A = {PredicateLiteral("p", Number(0))}
        B = {PredicateLiteral("p", Number(0)), PredicateLiteral("p", Number(1))}
        # I subset J
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.GREATER_OR_EQ, Number(1), True), None),
                element_instances,
                A,
                B,
            )
        )
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.GREATER, Number(1), True), None), element_instances, A, B
            )
        )
        # J subset I
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.GREATER_OR_EQ, Number(1), True), None),
                element_instances,
                B,
                A,
            )
        )
        self.assertFalse(
            aggr_func.propagate(
                (Guard(RelOp.GREATER, Number(1), True), None), element_instances, B, A
            )
        )

        # <, <=
        # TODO: correct ???
        A = {PredicateLiteral("p", Number(0))}
        B = {PredicateLiteral("p", Number(0)), PredicateLiteral("p", Number(1))}
        # I subset J
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.LESS_OR_EQ, Number(1), True), None),
                element_instances,
                A,
                B,
            )
        )
        self.assertFalse(
            aggr_func.propagate(
                (Guard(RelOp.LESS, Number(1), True), None), element_instances, A, B
            )
        )
        # J subset I
        self.assertFalse(
            aggr_func.propagate(
                (Guard(RelOp.LESS_OR_EQ, Number(1), True), None),
                element_instances,
                B,
                A,
            )
        )
        self.assertFalse(
            aggr_func.propagate(
                (Guard(RelOp.LESS, Number(1), True), None), element_instances, B, A
            )
        )

        # =
        # TODO: correct ???
        A = {PredicateLiteral("p", Number(0))}
        B = {PredicateLiteral("p", Number(0)), PredicateLiteral("p", Number(1))}
        # I subset J
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.EQUAL, Number(1), True), None), element_instances, A, B
            )
        )
        # J subset I
        self.assertFalse(
            aggr_func.propagate(
                (Guard(RelOp.EQUAL, Number(1), True), None), element_instances, B, A
            )
        )

        # !=
        # TODO: correct ???
        A = {PredicateLiteral("p", Number(0))}
        B = {PredicateLiteral("p", Number(0)), PredicateLiteral("p", Number(1))}
        # I subset J
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.UNEQUAL, Number(1), True), None), element_instances, A, B
            )
        )
        # J subset I
        self.assertFalse(
            aggr_func.propagate(
                (Guard(RelOp.UNEQUAL, Number(1), True), None), element_instances, B, A
            )
        )

        # TODO: two different guards at a time
        # TODO: special cases?

    """

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
        # positive/negative literal occurrences
        self.assertEqual(var_choice.pos_occ(),
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
            Choice(
                ground_elements,
                # satisfiable lower bound
                guards=Guard(RelOp.LESS, Number(1), False),
            ).eval()
        )
        self.assertFalse(
            Choice(
                ground_elements,
                # unsatisfiable lower bound
                guards=Guard(RelOp.LESS, Number(2), False),
            ).eval()
        )
        self.assertTrue(
            Choice(
                ground_elements,
                # satisfiable lower bound
                guards=Guard(RelOp.LESS_OR_EQ, Number(2), False),
            ).eval()
        )
        self.assertFalse(
            Choice(
                ground_elements,
                # unsatisfiable lower bound
                guards=Guard(RelOp.LESS_OR_EQ, Number(3), False),
            ).eval()
        )
        self.assertTrue(
            Choice(
                ground_elements,
                # satisfiable upper bound
                guards=Guard(RelOp.GREATER, Number(1), False),
            ).eval()
        )
        self.assertFalse(
            Choice(
                ground_elements,
                # unsatisfiable upper bound
                guards=Guard(RelOp.GREATER, Number(0), False),
            ).eval()
        )
        self.assertTrue(
            Choice(
                ground_elements,
                # satisfiable upper bound
                guards=Guard(RelOp.GREATER_OR_EQ, Number(0), False),
            ).eval()
        )
        self.assertFalse(
            Choice(
                ground_elements,
                # unsatisfiable upper bound
                guards=Guard(RelOp.GREATER_OR_EQ, Number(-1), False),
            ).eval()
        )
        self.assertTrue(
            Choice(
                ground_elements,
                # satisfiable equality bound
                guards=Guard(RelOp.EQUAL, Number(2), False),
            ).eval()
        )
        self.assertFalse(
            Choice(
                ground_elements,
                # unsatisfiable equality bound
                guards=Guard(RelOp.EQUAL, Number(-1), False),
            ).eval()
        )
        self.assertFalse(
            Choice(
                ground_elements,
                # unsatisfiable equality bound
                guards=Guard(RelOp.EQUAL, Number(3), False),
            ).eval()
        )
        self.assertTrue(
            Choice(
                # no elements
                tuple(),
                # satisfiable unequality bound
                guards=Guard(RelOp.UNEQUAL, Number(-1), False),
            ).eval()
        )
        self.assertFalse(
            Choice(
                # no elements
                tuple(),
                # unsatisfiable unequality bound
                guards=Guard(RelOp.UNEQUAL, Number(0), False),
            ).eval()
        )
        self.assertTrue(
            Choice(
                ground_elements,
                # satisfiable unequality bound
                guards=Guard(RelOp.UNEQUAL, Number(-1), False),
            ).eval()
        )
        self.assertTrue(
            Choice(
                ground_elements,
                # satisfiable unequality bound
                guards=Guard(RelOp.UNEQUAL, Number(0), False),
            ).eval()
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
            )
        )

        # substitute
        var_choice = Choice(
            var_elements, Guard(RelOp.LESS, Variable("X"), False)
        )
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


if __name__ == "__main__":
    unittest.main()
