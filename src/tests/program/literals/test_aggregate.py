import unittest
from typing import Set

import aspy
from aspy.program.literals import (
    AggrCount,
    AggrElement,
    AggrLiteral,
    AggrMax,
    AggrMin,
    AggrSum,
    Guard,
    LiteralCollection,
    Naf,
    PredLiteral,
)
from aspy.program.operators import RelOp
from aspy.program.safety_characterization import SafetyRule, SafetyTriplet
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


class TestAggregate(unittest.TestCase):
    def test_aggregate_element(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        element = AggrElement(
            TermTuple(Number(5), Variable("X")),
            LiteralCollection(
                PredLiteral("p", String("str")),
                Naf(PredLiteral("q", Variable("Y"))),
            ),
        )
        # string representation
        self.assertEqual(str(element), '5,X:p("str"),not q(Y)')
        # equality
        self.assertEqual(
            element,
            AggrElement(
                TermTuple(Number(5), Variable("X")),
                LiteralCollection(
                    PredLiteral("p", String("str")),
                    Naf(PredLiteral("q", Variable("Y"))),
                ),
            ),
        )
        # head
        self.assertEqual(element.head, TermTuple(Number(5), Variable("X")))
        # body
        self.assertEqual(
            element.body,
            LiteralCollection(
                PredLiteral("p", String("str")),
                Naf(PredLiteral("q", Variable("Y"))),
            ),
        )
        # hashing
        self.assertEqual(
            hash(element),
            hash(
                AggrElement(
                    TermTuple(Number(5), Variable("X")),
                    LiteralCollection(
                        PredLiteral("p", String("str")),
                        Naf(PredLiteral("q", Variable("Y"))),
                    ),
                )
            ),
        )
        # ground
        self.assertFalse(element.ground)
        # positive/negative literal occurrences
        self.assertEqual(element.pos_occ(), {PredLiteral("p", String("str"))})
        self.assertEqual(element.neg_occ(), {PredLiteral("q", Variable("Y"))})
        # weight
        self.assertEqual(element.weight, 5)
        self.assertEqual(AggrElement(TermTuple(Variable("X"), Number(5))).weight, 0)
        # vars
        self.assertTrue(
            element.vars() == element.global_vars() == {Variable("X"), Variable("Y")}
        )
        # safety
        self.assertRaises(ValueError, element.safety)
        # replace arithmetic terms
        self.assertEqual(element.replace_arith(VariableTable()), element)
        element = AggrElement(
            TermTuple(Number(5), Minus(Variable("X"))),
            LiteralCollection(
                PredLiteral("p", String("str")),
                Naf(PredLiteral("q", Variable("Y"))),
            ),
        )
        self.assertEqual(
            element.replace_arith(VariableTable()),
            AggrElement(
                TermTuple(Number(5), ArithVariable(0, Minus(Variable("X")))),
                LiteralCollection(
                    PredLiteral("p", String("str")),
                    Naf(PredLiteral("q", Variable("Y"))),
                ),
            ),
        )

        # substitute
        self.assertEqual(
            element.substitute(
                Substitution({Variable("X"): Number(1), Number(5): String("f")})
            ),  # NOTE: substitution is invalid
            AggrElement(
                TermTuple(Number(5), Minus(Number(1))),
                LiteralCollection(
                    PredLiteral("p", String("str")),
                    Naf(PredLiteral("q", Variable("Y"))),
                ),
            ),
        )
        # match
        self.assertRaises(Exception, element.match, element)

    def test_aggregate_count(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        aggr_func = AggrCount()
        # equality
        self.assertEqual(aggr_func, AggrCount())
        # hashing
        self.assertEqual(hash(aggr_func), hash(AggrCount()))
        # string representation
        self.assertEqual(str(aggr_func), "#count")
        # base value
        self.assertEqual(aggr_func.base, Number(0))
        # evaluation
        self.assertEqual(
            aggr_func.eval({TermTuple(Number(5)), TermTuple(Number(-3))}), Number(2)
        )

        # ----- propagation -----
        element_instances = {
            AggrElement(
                TermTuple(Number(0)), LiteralCollection(PredLiteral("p", Number(0)))
            ),
            AggrElement(
                TermTuple(Number(1)),
                LiteralCollection(PredLiteral("p", Number(1))),
            ),
        }

        # >, >=
        # TODO: correct ???
        A = {PredLiteral("p", Number(0))}
        B = {PredLiteral("p", Number(0)), PredLiteral("p", Number(1))}
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
        A = {PredLiteral("p", Number(0))}
        B = {PredLiteral("p", Number(0)), PredLiteral("p", Number(1))}
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
        A = {PredLiteral("p", Number(0))}
        B = {PredLiteral("p", Number(0)), PredLiteral("p", Number(1))}
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
        A = {PredLiteral("p", Number(0))}
        B = {PredLiteral("p", Number(0)), PredLiteral("p", Number(1))}
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

    def test_aggregate_sum(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        aggr_func = AggrSum()
        # equality
        self.assertEqual(aggr_func, AggrSum())
        # hashing
        self.assertEqual(hash(aggr_func), hash(AggrSum()))
        # string representation
        self.assertEqual(str(aggr_func), "#sum")
        # base value
        self.assertEqual(aggr_func.base, Number(0))
        # evaluation
        self.assertEqual(
            aggr_func.eval({TermTuple(Number(5)), TermTuple(Number(-3))}), Number(2)
        )

        # ----- propagation -----
        element_instances = {
            AggrElement(
                TermTuple(Number(0)), LiteralCollection(PredLiteral("p", Number(0)))
            ),
            AggrElement(
                TermTuple(Number(1)),
                LiteralCollection(PredLiteral("p", Number(1))),
            ),
        }

        # >, >=
        # TODO: correct ???
        literals_I = {PredLiteral("p", Number(0))}
        literals_J = {
            PredLiteral("p", Number(0)),
            PredLiteral("p", Number(1)),
        }
        # I subset J
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.GREATER_OR_EQ, Number(1), True), None),
                element_instances,
                literals_I,
                literals_J,
            )
        )
        self.assertFalse(
            aggr_func.propagate(
                (Guard(RelOp.GREATER, Number(1), True), None),
                element_instances,
                literals_I,
                literals_J,
            )
        )
        # J subset I
        self.assertFalse(
            aggr_func.propagate(
                (Guard(RelOp.GREATER_OR_EQ, Number(1), True), None),
                element_instances,
                literals_J,
                literals_I,
            )
        )
        self.assertFalse(
            aggr_func.propagate(
                (Guard(RelOp.GREATER, Number(1), True), None),
                element_instances,
                literals_J,
                literals_I,
            )
        )

        # <, <=
        # TODO: correct ???
        literals_I = {PredLiteral("p", Number(0))}
        literals_J = {
            PredLiteral("p", Number(0)),
            PredLiteral("p", Number(1)),
        }
        # I subset J
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.LESS_OR_EQ, Number(1), True), None),
                element_instances,
                literals_I,
                literals_J,
            )
        )
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.LESS, Number(1), True), None),
                element_instances,
                literals_I,
                literals_J,
            )
        )
        # J subset I
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.LESS_OR_EQ, Number(1), True), None),
                element_instances,
                literals_J,
                literals_I,
            )
        )
        self.assertFalse(
            aggr_func.propagate(
                (Guard(RelOp.LESS, Number(1), True), None),
                element_instances,
                literals_J,
                literals_I,
            )
        )

        # =
        # TODO: correct ???
        literals_I = {PredLiteral("p", Number(0))}
        literals_J = {
            PredLiteral("p", Number(0)),
            PredLiteral("p", Number(1)),
        }
        # I subset J
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.EQUAL, Number(1), True), None),
                element_instances,
                literals_I,
                literals_J,
            )
        )
        # J subset I
        self.assertFalse(
            aggr_func.propagate(
                (Guard(RelOp.EQUAL, Number(1), True), None),
                element_instances,
                literals_J,
                literals_I,
            )
        )

        # !=
        # TODO: correct ???
        literals_I = {PredLiteral("p", Number(0))}
        literals_J = {
            PredLiteral("p", Number(0)),
            PredLiteral("p", Number(1)),
        }
        # I subset J
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.UNEQUAL, Number(1), True), None),
                element_instances,
                literals_I,
                literals_J,
            )
        )
        # J subset I
        self.assertFalse(
            aggr_func.propagate(
                (Guard(RelOp.UNEQUAL, Number(1), True), None),
                element_instances,
                literals_J,
                literals_I,
            )
        )

        # TODO: two different guards at a time
        # TODO: special cases?

    def test_aggregate_max(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        aggr_func = AggrMax()
        # equality
        self.assertEqual(aggr_func, AggrMax())
        # hashing
        self.assertEqual(hash(aggr_func), hash(AggrMax()))
        # string representation
        self.assertEqual(str(aggr_func), "#max")
        # base value
        self.assertEqual(aggr_func.base, Infimum())
        # evaluation
        self.assertEqual(
            aggr_func.eval({TermTuple(Number(5)), TermTuple(Number(-3))}), Number(5)
        )

        # ----- propagation -----
        element_instances = {
            AggrElement(
                TermTuple(Number(0)), LiteralCollection(PredLiteral("p", Number(0)))
            ),
            AggrElement(
                TermTuple(Number(1)),
                LiteralCollection(PredLiteral("p", Number(1))),
            ),
        }

        # >, >=
        # TODO: correct ???
        A = {PredLiteral("p", Number(0))}
        B = {PredLiteral("p", Number(0)), PredLiteral("p", Number(1))}
        # I subset J
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.GREATER_OR_EQ, Number(1), True), None),
                element_instances,
                A,
                B,
            )
        )
        self.assertFalse(
            aggr_func.propagate(
                (Guard(RelOp.GREATER, Number(1), True), None), element_instances, A, B
            )
        )
        # J subset I
        self.assertFalse(
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
        A = {PredLiteral("p", Number(0))}
        B = {PredLiteral("p", Number(0)), PredLiteral("p", Number(1))}
        # I subset J
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.LESS_OR_EQ, Number(1), True), None),
                element_instances,
                A,
                B,
            )
        )
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.LESS, Number(1), True), None), element_instances, A, B
            )
        )
        # J subset I
        self.assertTrue(
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
        A = {PredLiteral("p", Number(0))}
        B = {PredLiteral("p", Number(0)), PredLiteral("p", Number(1))}
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
        A = {PredLiteral("p", Number(0))}
        B = {PredLiteral("p", Number(0)), PredLiteral("p", Number(1))}
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

    def test_aggregate_min(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        aggr_func = AggrMin()
        # equality
        self.assertEqual(aggr_func, AggrMin())
        # hashing
        self.assertEqual(hash(aggr_func), hash(AggrMin()))
        # string representation
        self.assertEqual(str(aggr_func), "#min")
        # base value
        self.assertEqual(aggr_func.base, Supremum())
        # evaluation
        self.assertEqual(
            aggr_func.eval({TermTuple(Number(5)), TermTuple(Number(-3))}), Number(-3)
        )

        # ----- propagation -----
        element_instances = {
            AggrElement(
                TermTuple(Number(0)), LiteralCollection(PredLiteral("p", Number(0)))
            ),
            AggrElement(
                TermTuple(Number(1)),
                LiteralCollection(PredLiteral("p", Number(1))),
            ),
        }

        # >, >=
        # TODO: correct ???
        A = {PredLiteral("p", Number(0))}
        B = {PredLiteral("p", Number(0)), PredLiteral("p", Number(1))}
        # I subset J
        self.assertFalse(
            aggr_func.propagate(
                (Guard(RelOp.GREATER_OR_EQ, Number(1), True), None),
                element_instances,
                A,
                B,
            )
        )
        self.assertFalse(
            aggr_func.propagate(
                (Guard(RelOp.GREATER, Number(1), True), None), element_instances, A, B
            )
        )
        # J subset I
        self.assertFalse(
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
        A = {PredLiteral("p", Number(0))}
        B = {PredLiteral("p", Number(0)), PredLiteral("p", Number(1))}
        # I subset J
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.LESS_OR_EQ, Number(1), True), None),
                element_instances,
                A,
                B,
            )
        )
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.LESS, Number(1), True), None), element_instances, A, B
            )
        )
        # J subset I
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.LESS_OR_EQ, Number(1), True), None),
                element_instances,
                B,
                A,
            )
        )
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.LESS, Number(1), True), None), element_instances, B, A
            )
        )

        # =
        # TODO: correct ???
        A = {PredLiteral("p", Number(0))}
        B = {PredLiteral("p", Number(0)), PredLiteral("p", Number(1))}
        # I subset J
        self.assertFalse(
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
        A = {PredLiteral("p", Number(0))}
        B = {PredLiteral("p", Number(0)), PredLiteral("p", Number(1))}
        # I subset J
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.UNEQUAL, Number(1), True), None), element_instances, A, B
            )
        )
        # J subset I
        self.assertTrue(
            aggr_func.propagate(
                (Guard(RelOp.UNEQUAL, Number(1), True), None), element_instances, B, A
            )
        )

        # TODO: two different guards at a time
        # TODO: special cases?

    def test_aggregate_literal(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        ground_elements = (
            AggrElement(
                TermTuple(Number(5)),
                LiteralCollection(
                    PredLiteral("p", String("str")), Naf(PredLiteral("q"))
                ),
            ),
            AggrElement(
                TermTuple(Number(-3)),
                LiteralCollection(Naf(PredLiteral("p", String("str")))),
            ),
        )
        aggr_func = AggrCount()

        # no guards
        self.assertRaises(ValueError, AggrLiteral, aggr_func, ground_elements, tuple())
        # left guard only
        ground_literal = AggrLiteral(
            aggr_func, ground_elements, guards=Guard(RelOp.LESS, Number(3), False)
        )
        self.assertEqual(ground_literal.lguard, Guard(RelOp.LESS, Number(3), False))
        self.assertEqual(ground_literal.rguard, None)
        self.assertEqual(
            ground_literal.guards, (Guard(RelOp.LESS, Number(3), False), None)
        )
        self.assertFalse(ground_literal.eval())
        self.assertEqual(
            str(ground_literal), '3 < #count{5:p("str"),not q;-3:not p("str")}'
        )
        # right guard only
        ground_literal = AggrLiteral(
            aggr_func, ground_elements, Guard(RelOp.LESS, Number(3), True), naf=True
        )
        self.assertEqual(ground_literal.lguard, None)
        self.assertEqual(ground_literal.rguard, Guard(RelOp.LESS, Number(3), True))
        self.assertEqual(
            ground_literal.guards, (None, Guard(RelOp.LESS, Number(3), True))
        )
        self.assertTrue(ground_literal.eval())
        self.assertEqual(
            str(ground_literal), 'not #count{5:p("str"),not q;-3:not p("str")} < 3'
        )
        # both guards
        ground_literal = AggrLiteral(
            aggr_func,
            ground_elements,
            guards=(
                Guard(RelOp.LESS, Number(3), False),
                Guard(RelOp.LESS, Number(3), True),
            ),
        )
        self.assertEqual(ground_literal.lguard, Guard(RelOp.LESS, Number(3), False))
        self.assertEqual(ground_literal.rguard, Guard(RelOp.LESS, Number(3), True))
        self.assertEqual(
            ground_literal.guards,
            (Guard(RelOp.LESS, Number(3), False), Guard(RelOp.LESS, Number(3), True)),
        )
        self.assertFalse(ground_literal.eval())
        self.assertEqual(
            str(ground_literal), '3 < #count{5:p("str"),not q;-3:not p("str")} < 3'
        )

        var_elements = (
            AggrElement(
                TermTuple(Number(5)),
                LiteralCollection(
                    PredLiteral("p", Variable("X")), Naf(PredLiteral("q"))
                ),
            ),
            AggrElement(
                TermTuple(Number(-3)),
                LiteralCollection(Naf(PredLiteral("p", String("str")))),
            ),
        )
        var_literal = AggrLiteral(
            aggr_func, var_elements, guards=Guard(RelOp.LESS, Variable("Y"), False)
        )

        # equality
        self.assertEqual(
            ground_literal,
            AggrLiteral(
                aggr_func,
                ground_elements,
                guards=(
                    Guard(RelOp.LESS, Number(3), False),
                    Guard(RelOp.LESS, Number(3), True),
                ),
            ),
        )
        # hashing
        self.assertEqual(
            hash(ground_literal),
            hash(
                AggrLiteral(
                    aggr_func,
                    ground_elements,
                    guards=(
                        Guard(RelOp.LESS, Number(3), False),
                        Guard(RelOp.LESS, Number(3), True),
                    ),
                )
            ),
        )
        # ground
        self.assertTrue(ground_literal.ground)
        self.assertFalse(var_literal.ground)
        # negation
        self.assertFalse(ground_literal.naf)
        ground_literal.set_naf()
        self.assertTrue(ground_literal.naf)
        ground_literal.set_naf(False)
        self.assertFalse(ground_literal.naf)
        ground_literal.set_naf(True)
        self.assertTrue(ground_literal.naf)
        # variables
        self.assertTrue(
            ground_literal.invars()
            == ground_literal.outvars()
            == ground_literal.vars()
            == ground_literal.global_vars()
            == set()
        )
        self.assertEqual(var_literal.invars(), {Variable("X")})
        self.assertEqual(var_literal.outvars(), {Variable("Y")})
        self.assertEqual(var_literal.vars(), {Variable("X"), Variable("Y")})
        self.assertEqual(var_literal.global_vars(), {Variable("Y")})
        # positive/negative literal occurrences
        self.assertEqual(var_literal.pos_occ(), {PredLiteral("p", Variable("X"))})
        self.assertEqual(
            var_literal.neg_occ(),
            {PredLiteral("p", String("str")), PredLiteral("q")},
        )

        # safety characterization
        self.assertEqual(
            var_literal.safety(DummyRule({Variable("X")})),
            SafetyTriplet(unsafe={Variable("X")}),
        )
        self.assertEqual(
            var_literal.safety(DummyRule({Variable("Y")})), SafetyTriplet()
        )
        self.assertEqual(
            AggrLiteral(
                aggr_func, var_elements, Guard(RelOp.LESS, Variable("X"), False)
            ).safety(DummyRule({Variable("X")})),
            SafetyTriplet(unsafe={Variable("X")}),
        )
        self.assertEqual(
            AggrLiteral(
                aggr_func, var_elements, Guard(RelOp.LESS, Variable("X"), False)
            ).safety(DummyRule({Variable("Y")})),
            SafetyTriplet(),
        )
        # aggr_global_invars = {'X'}
        # aggr_global_vars = {'X','Y'} -> unsafe
        # rules = { ('Y', {'X'}) }
        self.assertEqual(
            AggrLiteral(
                aggr_func, var_elements, guards=Guard(RelOp.EQUAL, Variable("Y"), False)
            ).safety(DummyRule({Variable("X"), Variable("Y")})),
            SafetyTriplet(
                unsafe={Variable("X"), Variable("Y")},
                rules={SafetyRule(Variable("Y"), {Variable("X")})},
            ),
        )
        # aggr_global_invars = {}
        # aggr_global_vars = {'Y'} -> unsafe
        # rules = { ('Y', {}) } -> makes 'Y' safe
        self.assertEqual(
            AggrLiteral(
                aggr_func, var_elements, guards=Guard(RelOp.EQUAL, Variable("Y"), False)
            ).safety(DummyRule({Variable("Y")})),
            SafetyTriplet(safe={Variable("Y")}),
        )
        # aggr_global_invars = {'X'}
        # aggr_global_vars = {'X'} -> unsafe
        # rules = { ('X', {'X'}) } -> removes (without making 'X' safe)
        self.assertEqual(
            AggrLiteral(
                aggr_func, var_elements, guards=Guard(RelOp.EQUAL, Variable("X"), False)
            ).safety(DummyRule({Variable("X")})),
            SafetyTriplet(unsafe={Variable("X")}),
        )
        # aggr_global_invars = {}
        # aggr_global_vars = {'X'} -> unsafe
        # rules = { ('X', {}) } -> makes 'X' safe
        self.assertEqual(
            AggrLiteral(
                aggr_func, var_elements, guards=Guard(RelOp.EQUAL, Variable("X"), False)
            ).safety(DummyRule({Variable("Y")})),
            SafetyTriplet(safe={Variable("X")}),
        )
        # TODO: safety characterization for case with two guards

        # replace arithmetic terms
        arith_elements = (
            AggrElement(
                TermTuple(Number(5)),
                LiteralCollection(
                    PredLiteral("p", Minus(Variable("X"))),
                    Naf(PredLiteral("q")),
                ),
            ),
        )
        arith_literal = Naf(
            AggrLiteral(
                aggr_func,
                arith_elements,
                Guard(RelOp.EQUAL, Minus(Variable("X")), True),
            )
        )
        self.assertEqual(
            arith_literal.replace_arith(VariableTable()),
            Naf(
                AggrLiteral(
                    aggr_func,
                    (
                        AggrElement(
                            TermTuple(Number(5)),
                            LiteralCollection(
                                PredLiteral(
                                    "p", ArithVariable(0, Minus(Variable("X")))
                                ),
                                Naf(PredLiteral("q")),
                            ),
                        ),
                    ),
                    Guard(RelOp.EQUAL, ArithVariable(1, Minus(Variable("X"))), True),
                )
            ),
        )

        # substitute
        var_literal = AggrLiteral(
            aggr_func, var_elements, Guard(RelOp.LESS, Variable("X"), False)
        )
        self.assertEqual(
            var_literal.substitute(
                Substitution({Variable("X"): Number(1), Number(-3): String("f")})
            ),  # NOTE: substitution is invalid
            AggrLiteral(
                AggrCount(),
                (
                    AggrElement(
                        TermTuple(Number(5)),
                        LiteralCollection(
                            PredLiteral("p", Number(1)), Naf(PredLiteral("q"))
                        ),
                    ),
                    AggrElement(
                        TermTuple(Number(-3)),
                        LiteralCollection(Naf(PredLiteral("p", String("str")))),
                    ),
                ),
                guards=Guard(RelOp.LESS, Number(1), False),
            ),
        )


if __name__ == "__main__":  # pragma: no cover  # pragma: no cover
    unittest.main()
