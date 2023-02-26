import unittest

import aspy
from aspy.program.substitution import Substitution
from aspy.program.variable_table import VariableTable
from aspy.program.terms import TermTuple, Number, Variable, Minus, String, Infimum, Supremum, ArithVariable
from aspy.program.literals import Naf, PredicateLiteral, AggregateElement, AggregateCount, AggregateSum, AggregateMax, AggregateMin, AggregateLiteral, LiteralTuple, Guard
from aspy.program.operators import RelOp
from aspy.program.safety_characterization import SafetyTriplet, SafetyRule


class TestAggregate(unittest.TestCase):
    def test_aggregate_element(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        element = AggregateElement(
            TermTuple(Number(5), Variable('X')),
            LiteralTuple(PredicateLiteral('p', String('str')), Naf(PredicateLiteral('q', Variable('Y'))))
        )
        self.assertEqual(str(element), '5,X:p("str"),not q(Y)')
        self.assertEqual(element, AggregateElement(TermTuple(Number(5), Variable('X')), LiteralTuple(PredicateLiteral('p', String('str')), Naf(PredicateLiteral('q', Variable('Y'))))))
        self.assertEqual(hash(element), hash(AggregateElement(TermTuple(Number(5), Variable('X')), LiteralTuple(PredicateLiteral('p', String('str')), Naf(PredicateLiteral('q', Variable('Y')))))))
        self.assertEqual(element.head, TermTuple(Number(5), Variable('X')))
        self.assertEqual(element.body, LiteralTuple(PredicateLiteral('p', String('str')), Naf(PredicateLiteral('q', Variable('Y')))))
        self.assertFalse(element.ground)
        self.assertEqual(element.pos_occ(), {PredicateLiteral('p', String('str'))})
        self.assertEqual(element.neg_occ(), {PredicateLiteral('q', Variable('Y'))})
        self.assertEqual(element.weight, 5)
        self.assertEqual(AggregateElement(TermTuple(Variable('X'), Number(5))).weight, 0)
        self.assertTrue(element.vars() == element.vars(True) == {Variable('X'), Variable('Y')})
        self.assertRaises(ValueError, element.safety)
        self.assertEqual(element.replace_arith(VariableTable()), element)
        element = AggregateElement(
            TermTuple(Number(5), Minus(Variable('X'))),
            LiteralTuple(PredicateLiteral('p', String('str')), Naf(PredicateLiteral('q', Variable('Y'))))
        )
        self.assertEqual(element.replace_arith(VariableTable()),
            AggregateElement(
                TermTuple(Number(5), ArithVariable(0, Minus(Variable('X')))),
                LiteralTuple(PredicateLiteral('p', String('str')), Naf(PredicateLiteral('q', Variable('Y'))))
            )
        )

        # substitute
        self.assertEqual(element.substitute(Substitution({Variable('X'): Number(1), Number(5): String('f')})), # NOTE: substitution is invalid
            AggregateElement(
                TermTuple(Number(5), Minus(Number(1))),
                LiteralTuple(PredicateLiteral('p', String('str')), Naf(PredicateLiteral('q', Variable('Y'))))
            )                 
        )
        # TODO: match

    def test_aggregate_count(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        elements = (
            AggregateElement(
                TermTuple(Number(5)),
                LiteralTuple(PredicateLiteral('p', String('str')), Naf(PredicateLiteral('q')))
            ),
            AggregateElement(
                TermTuple(Number(-3)),
                LiteralTuple(Naf(PredicateLiteral('p', String('str'))))
            )
        )
        aggregate = AggregateCount(*elements)
        self.assertEqual(aggregate, AggregateCount(*elements))
        self.assertEqual(hash(aggregate), hash(AggregateCount(*elements)))
        self.assertEqual(str(aggregate), '#count{5:p("str"),not q;-3:not p("str")}')
        self.assertTrue(aggregate.ground)
        self.assertEqual(aggregate.eval(), Number(2))
        self.assertEqual(aggregate.base(), Number(0))
        self.assertTrue(aggregate.vars() == aggregate.vars(True) == set())
        self.assertEqual(aggregate.pos_occ(), {PredicateLiteral('p', String('str'))})
        self.assertEqual(aggregate.neg_occ(), {PredicateLiteral('p', String('str')), PredicateLiteral('q')})

        self.assertEqual(aggregate.replace_arith(VariableTable()), aggregate)
        aggregate = AggregateCount(AggregateElement(TermTuple(Number(5)), LiteralTuple(PredicateLiteral('p', Variable('X')), Naf(PredicateLiteral('q')))))
        self.assertEqual(aggregate.replace_arith(VariableTable()), aggregate)
        aggregate = AggregateCount(AggregateElement(TermTuple(Number(5)), LiteralTuple(PredicateLiteral('p', Minus(Variable('X'))), Naf(PredicateLiteral('q')))))
        self.assertEqual(aggregate.replace_arith(VariableTable()),
            AggregateCount(
                AggregateElement(
                    TermTuple(Number(5)),
                    LiteralTuple(
                        PredicateLiteral('p', ArithVariable(0, Minus(Variable('X')))),
                        Naf(PredicateLiteral('q'))
                    )
                )
            )
        )

        # substitute
        self.assertEqual(aggregate.substitute(Substitution({Variable('X'): Number(1), Number(5): String('f')})), # NOTE: substitution is invalid
            AggregateCount(AggregateElement(TermTuple(Number(5)), LiteralTuple(PredicateLiteral('p', Minus(Number(1))), Naf(PredicateLiteral('q')))))
        )
        # TODO: match

    def test_aggregate_sum(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        elements = (
            AggregateElement(
                TermTuple(Number(5)),
                LiteralTuple(PredicateLiteral('p', String('str')), Naf(PredicateLiteral('q')))
            ),
            AggregateElement(
                TermTuple(Number(-3)),
                LiteralTuple(Naf(PredicateLiteral('p', String('str'))))
            )
        )
        aggregate = AggregateSum(*elements)
        self.assertEqual(aggregate, AggregateSum(*elements))
        self.assertEqual(hash(aggregate), hash(AggregateSum(*elements)))
        self.assertEqual(str(aggregate), '#sum{5:p("str"),not q;-3:not p("str")}')
        self.assertTrue(aggregate.ground)
        self.assertEqual(aggregate.eval(), Number(2))
        self.assertEqual(aggregate.base(), Number(0))
        self.assertTrue(aggregate.vars() == aggregate.vars(True) == set())
        self.assertEqual(aggregate.pos_occ(), {PredicateLiteral('p', String('str'))})
        self.assertEqual(aggregate.neg_occ(), {PredicateLiteral('p', String('str')), PredicateLiteral('q')})

        self.assertEqual(aggregate.replace_arith(VariableTable()), aggregate)
        aggregate = AggregateSum(AggregateElement(TermTuple(Number(5)), LiteralTuple(PredicateLiteral('p', Variable('X')), Naf(PredicateLiteral('q')))))
        self.assertFalse(aggregate.ground)
        self.assertEqual(aggregate.replace_arith(VariableTable()), aggregate)
        aggregate = AggregateSum(AggregateElement(TermTuple(Number(5)), LiteralTuple(PredicateLiteral('p', Minus(Variable('X'))), Naf(PredicateLiteral('q')))))
        self.assertEqual(aggregate.replace_arith(VariableTable()),
            AggregateSum(
                AggregateElement(
                    TermTuple(Number(5)),
                    LiteralTuple(
                        PredicateLiteral('p', ArithVariable(0, Minus(Variable('X')))),
                        Naf(PredicateLiteral('q'))
                    )
                )
            )
        )

        # substitute
        self.assertEqual(aggregate.substitute(Substitution({Variable('X'): Number(1), Number(5): String('f')})), # NOTE: substitution is invalid
            AggregateSum(AggregateElement(TermTuple(Number(5)), LiteralTuple(PredicateLiteral('p', Minus(Number(1))), Naf(PredicateLiteral('q')))))
        )
        # TODO: match

    def test_aggregate_max(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        elements = (
            AggregateElement(
                TermTuple(Number(5)),
                LiteralTuple(PredicateLiteral('p', String('str')), Naf(PredicateLiteral('q')))
            ),
            AggregateElement(
                TermTuple(Number(-3)),
                LiteralTuple(Naf(PredicateLiteral('p', String('str'))))
            )
        )
        aggregate = AggregateMax(*elements)
        self.assertEqual(aggregate, AggregateMax(*elements))
        self.assertEqual(hash(aggregate), hash(AggregateMax(*elements)))
        self.assertEqual(str(aggregate), '#max{5:p("str"),not q;-3:not p("str")}')
        self.assertTrue(aggregate.ground)
        self.assertEqual(aggregate.eval(), Number(5))
        self.assertEqual(aggregate.base(), Infimum)
        self.assertTrue(aggregate.vars() == aggregate.vars(True) == set())
        self.assertEqual(aggregate.pos_occ(), {PredicateLiteral('p', String('str'))})
        self.assertEqual(aggregate.neg_occ(), {PredicateLiteral('p', String('str')), PredicateLiteral('q')})

        self.assertEqual(aggregate.replace_arith(VariableTable()), aggregate)
        aggregate = AggregateMax(AggregateElement(TermTuple(Number(5)), LiteralTuple(PredicateLiteral('p', Variable('X')), Naf(PredicateLiteral('q')))))
        self.assertFalse(aggregate.ground)
        self.assertEqual(aggregate.replace_arith(VariableTable()), aggregate)
        aggregate = AggregateMax(AggregateElement(TermTuple(Number(5)), LiteralTuple(PredicateLiteral('p', Minus(Variable('X'))), Naf(PredicateLiteral('q')))))
        self.assertEqual(aggregate.replace_arith(VariableTable()),
            AggregateMax(
                AggregateElement(
                    TermTuple(Number(5)),
                    LiteralTuple(
                        PredicateLiteral('p', ArithVariable(0, Minus(Variable('X')))),
                        Naf(PredicateLiteral('q'))
                    )
                )
            )
        )

        # substitute
        self.assertEqual(aggregate.substitute(Substitution({Variable('X'): Number(1), Number(5): String('f')})), # NOTE: substitution is invalid
            AggregateMax(AggregateElement(TermTuple(Number(5)), LiteralTuple(PredicateLiteral('p', Minus(Number(1))), Naf(PredicateLiteral('q')))))
        )
        # TODO: match

    def test_aggregate_min(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        elements = (
            AggregateElement(
                TermTuple(Number(5)),
                LiteralTuple(PredicateLiteral('p', String('str')), Naf(PredicateLiteral('q')))
            ),
            AggregateElement(
                TermTuple(Number(-3)),
                LiteralTuple(Naf(PredicateLiteral('p', String('str'))))
            )
        )
        aggregate = AggregateMin(*elements)
        self.assertEqual(aggregate, AggregateMin(*elements))
        self.assertEqual(hash(aggregate), hash(AggregateMin(*elements)))
        self.assertEqual(str(aggregate), '#min{5:p("str"),not q;-3:not p("str")}')
        self.assertTrue(aggregate.ground)
        self.assertEqual(aggregate.eval(), Number(-3))
        self.assertEqual(aggregate.base(), Supremum)
        self.assertTrue(aggregate.vars() == aggregate.vars(True) == set())
        self.assertEqual(aggregate.pos_occ(), {PredicateLiteral('p', String('str'))})
        self.assertEqual(aggregate.neg_occ(), {PredicateLiteral('p', String('str')), PredicateLiteral('q')})

        self.assertEqual(aggregate.replace_arith(VariableTable()), aggregate)
        aggregate = AggregateMin(AggregateElement(TermTuple(Number(5)), LiteralTuple(PredicateLiteral('p', Variable('X')), Naf(PredicateLiteral('q')))))
        self.assertFalse(aggregate.ground)
        self.assertEqual(aggregate.replace_arith(VariableTable()), aggregate)
        aggregate = AggregateMin(AggregateElement(TermTuple(Number(5)), LiteralTuple(PredicateLiteral('p', Minus(Variable('X'))), Naf(PredicateLiteral('q')))))
        self.assertEqual(aggregate.replace_arith(VariableTable()),
            AggregateMin(
                AggregateElement(
                    TermTuple(Number(5)),
                    LiteralTuple(
                        PredicateLiteral('p', ArithVariable(0, Minus(Variable('X')))),
                        Naf(PredicateLiteral('q'))
                    )
                )
            )
        )

        # substitute
        self.assertEqual(aggregate.substitute(Substitution({Variable('X'): Number(1), Number(5): String('f')})), # NOTE: substitution is invalid
            AggregateMin(AggregateElement(TermTuple(Number(5)), LiteralTuple(PredicateLiteral('p', Minus(Number(1))), Naf(PredicateLiteral('q')))))
        )
        # TODO: match

    def test_aggregate_literal(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        elements = (
            AggregateElement(
                TermTuple(Number(5)),
                LiteralTuple(PredicateLiteral('p', String('str')), Naf(PredicateLiteral('q')))
            ),
            AggregateElement(
                TermTuple(Number(-3)),
                LiteralTuple(Naf(PredicateLiteral('p', String('str'))))
            )
        )
        aggregate = AggregateCount(*elements)

        # no guards
        self.assertRaises(ValueError, AggregateLiteral, aggregate, tuple())
        # left guard only
        literal = AggregateLiteral(aggregate, guards=Guard(RelOp.LESS, Number(3), False))
        self.assertEqual(literal.lguard, Guard(RelOp.LESS, Number(3), False))
        self.assertEqual(literal.rguard, None)
        self.assertEqual(literal.guards, (Guard(RelOp.LESS, Number(3), False), None))
        self.assertFalse(literal.eval())
        self.assertEqual(str(literal), '3 < #count{5:p("str"),not q;-3:not p("str")}')
        # right guard only
        literal = AggregateLiteral(aggregate, Guard(RelOp.LESS, Number(3), True))
        self.assertEqual(literal.lguard, None)
        self.assertEqual(literal.rguard, Guard(RelOp.LESS, Number(3), True))
        self.assertEqual(literal.guards, (None, Guard(RelOp.LESS, Number(3), True)))
        self.assertTrue(literal.eval())
        self.assertEqual(str(literal), '#count{5:p("str"),not q;-3:not p("str")} < 3')
        # both guards
        literal = AggregateLiteral(aggregate, guards=(Guard(RelOp.LESS, Number(3), False), Guard(RelOp.LESS, Number(3), True)))
        self.assertEqual(literal.lguard, Guard(RelOp.LESS, Number(3), False))
        self.assertEqual(literal.rguard, Guard(RelOp.LESS, Number(3), True))
        self.assertEqual(literal.guards, (Guard(RelOp.LESS, Number(3), False), Guard(RelOp.LESS, Number(3), True)))
        self.assertFalse(literal.eval())
        self.assertEqual(str(literal), '3 < #count{5:p("str"),not q;-3:not p("str")} < 3')

        self.assertFalse(literal.naf)
        self.assertTrue(literal.ground)
        literal.set_naf()
        self.assertTrue(literal.naf)
        literal.set_naf(False)
        self.assertFalse(literal.naf)
        literal.set_naf(True)
        self.assertTrue(literal.naf)

        elements = (
            AggregateElement(
                TermTuple(Number(5)),
                LiteralTuple(PredicateLiteral('p', Variable('X')), Naf(PredicateLiteral('q')))
            ),
            AggregateElement(
                TermTuple(Number(-3)),
                LiteralTuple(Naf(PredicateLiteral('p', String('str'))))
            )
        )
        aggregate = AggregateCount(*elements)
        literal = AggregateLiteral(aggregate, guards=Guard(RelOp.LESS, Variable('Y'), False))
        self.assertEqual(literal.invars(), {Variable('X')})
        self.assertEqual(literal.outvars(), {Variable('Y')})
        self.assertEqual(literal.vars(), {Variable('X'), Variable('Y')})
        self.assertEqual(literal.vars(True), {Variable('Y')})
        self.assertEqual(literal.pos_occ(), {PredicateLiteral('p', Variable('X'))})
        self.assertEqual(literal.neg_occ(), {PredicateLiteral('p', String('str')), PredicateLiteral('q')})

        self.assertEqual(literal.safety(global_vars={Variable('X')}), SafetyTriplet(unsafe={Variable('X')}))
        self.assertEqual(literal.safety(global_vars={Variable('Y')}), SafetyTriplet())
        literal = AggregateLiteral(aggregate, Guard(RelOp.LESS, Variable('X'), False))
        self.assertEqual(literal.safety(global_vars={Variable('X')}), SafetyTriplet(unsafe={Variable('X')}))
        self.assertEqual(literal.safety(global_vars={Variable('Y')}), SafetyTriplet())

        # substitute
        self.assertEqual(literal.substitute(Substitution({Variable('X'): Number(1), Number(-3): String('f')})), # NOTE: substitution is invalid
            AggregateLiteral(AggregateCount( (
                AggregateElement(
                    TermTuple(Number(5)),
                    LiteralTuple(PredicateLiteral('p', Number(1)), Naf(PredicateLiteral('q')))
                ),
                AggregateElement(
                    TermTuple(Number(-3)),
                    LiteralTuple(Naf(PredicateLiteral('p', String('str'))))
                )
            )), guards=Guard(RelOp.LESS, Number(1), False)
        ))
        # TODO: match

        literal = AggregateLiteral(aggregate, guards=Guard(RelOp.EQUAL, Variable('Y'), False))
        # aggr_global_invars = {'X'}
        # aggr_global_vars = {'X','Y'} -> unsafe
        # rules = { ('Y', {'X'}) }
        self.assertEqual(literal.safety(global_vars={Variable('X'), Variable('Y')}), SafetyTriplet(unsafe={Variable('X'), Variable('Y')}, rules={SafetyRule(Variable('Y'), {Variable('X')})}))
        # aggr_global_invars = {}
        # aggr_global_vars = {'Y'} -> unsafe
        # rules = { ('Y', {}) } -> makes 'Y' safe
        self.assertEqual(literal.safety(global_vars={Variable('Y')}), SafetyTriplet(safe={Variable('Y')}))

        literal = AggregateLiteral(aggregate, guards=Guard(RelOp.EQUAL, Variable('X'), False))
        # aggr_global_invars = {'X'}
        # aggr_global_vars = {'X'} -> unsafe
        # rules = { ('X', {'X'}) } -> removes (without making 'X' safe)
        self.assertEqual(literal.safety(global_vars={Variable('X')}), SafetyTriplet(unsafe={Variable('X')}))
        # aggr_global_invars = {}
        # aggr_global_vars = {'X'} -> unsafe
        # rules = { ('X', {}) } -> makes 'X' safe
        self.assertEqual(literal.safety(global_vars={Variable('Y')}), SafetyTriplet(safe={Variable('X')}))

        # TODO: safety characterization for case with two guards

        aggregate = AggregateCount(AggregateElement(TermTuple(Number(5)), LiteralTuple(PredicateLiteral('p', Minus(Variable('X'))), Naf(PredicateLiteral('q')))))
        literal = Naf(AggregateLiteral(aggregate, Guard(RelOp.EQUAL, Minus(Variable('X')), True)))
        # replace arithmetic terms
        self.assertEqual(LiteralTuple(PredicateLiteral('p', Number(0), Variable('X')), PredicateLiteral('q', Minus(Variable('Y')))).replace_arith(VariableTable()), LiteralTuple(PredicateLiteral('p', Number(0), Variable('X')), PredicateLiteral('q', ArithVariable(0, Minus(Variable('Y'))))))


if __name__ == "__main__":
    unittest.main()


