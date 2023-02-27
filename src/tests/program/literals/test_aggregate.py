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

        aggr_func = AggregateCount()
        # equality
        self.assertEqual(aggr_func, AggregateCount())
        # hashing
        self.assertEqual(hash(aggr_func), hash(AggregateCount()))
        # string representation
        self.assertEqual(str(aggr_func), '#count')
        # base value
        self.assertEqual(aggr_func.base(), Number(0))
        # evaluation
        self.assertEqual(aggr_func.eval({TermTuple(Number(5)), TermTuple(Number(-3))}), Number(2))

        # ----- propagation -----
        element_instances = {
            AggregateElement(
                TermTuple(Number(0)),
                LiteralTuple(PredicateLiteral('p', Number(0)))
            ),
            AggregateElement(
                TermTuple(Number(1)),
                LiteralTuple(PredicateLiteral('p', Number(1))),
            )
        }

        # >, >=
        # TODO: correct ???
        A = {PredicateLiteral('p', Number(0))}
        B = {PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))}
        # I subset J
        self.assertTrue(  aggr_func.propagate((Guard(RelOp.GREATER_OR_EQ, Number(1), True), None), element_instances, A, B) )
        self.assertTrue(  aggr_func.propagate((Guard(RelOp.GREATER,       Number(1), True), None), element_instances, A, B) )
        # J subset I
        self.assertTrue(  aggr_func.propagate((Guard(RelOp.GREATER_OR_EQ, Number(1), True), None), element_instances, B, A) )
        self.assertFalse( aggr_func.propagate((Guard(RelOp.GREATER,       Number(1), True), None), element_instances, B, A) )

        # <, <=
        # TODO: correct ???
        A = {PredicateLiteral('p', Number(0))}
        B = {PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))}
        # I subset J
        self.assertTrue(  aggr_func.propagate((Guard(RelOp.LESS_OR_EQ, Number(1), True), None), element_instances, A, B) )
        self.assertFalse( aggr_func.propagate((Guard(RelOp.LESS,       Number(1), True), None), element_instances, A, B) ) 
        # J subset I
        self.assertFalse( aggr_func.propagate((Guard(RelOp.LESS_OR_EQ, Number(1), True), None), element_instances, B, A) ) 
        self.assertFalse( aggr_func.propagate((Guard(RelOp.LESS,       Number(1), True), None), element_instances, B, A) ) 

        # =
        # TODO: correct ???
        A = {PredicateLiteral('p', Number(0))}
        B = {PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))}
        # I subset J
        self.assertTrue(  aggr_func.propagate((Guard(RelOp.EQUAL, Number(1), True), None), element_instances, A, B) )
        # J subset I
        self.assertFalse( aggr_func.propagate((Guard(RelOp.EQUAL, Number(1), True), None), element_instances, B, A) )

        # !=
        # TODO: correct ???
        A = {PredicateLiteral('p', Number(0))}
        B = {PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))}
        # I subset J
        self.assertTrue(  aggr_func.propagate((Guard(RelOp.UNEQUAL, Number(1), True), None), element_instances, A, B) )
        # J subset I
        self.assertFalse( aggr_func.propagate((Guard(RelOp.UNEQUAL, Number(1), True), None), element_instances, B, A) )

        # TODO: two different guards at a time
        # TODO: special cases?

    def test_aggregate_sum(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        aggr_func = AggregateSum()
        # equality
        self.assertEqual(aggr_func, AggregateSum())
        # hashing
        self.assertEqual(hash(aggr_func), hash(AggregateSum()))
        # string representation
        self.assertEqual(str(aggr_func), '#sum')
        # base value
        self.assertEqual(aggr_func.base(), Number(0))
        # evaluation
        self.assertEqual(aggr_func.eval({TermTuple(Number(5)), TermTuple(Number(-3))}), Number(2))

        # ----- propagation -----
        element_instances = {
            AggregateElement(
                TermTuple(Number(0)),
                LiteralTuple(PredicateLiteral('p', Number(0)))
            ),
            AggregateElement(
                TermTuple(Number(1)),
                LiteralTuple(PredicateLiteral('p', Number(1))),
            )
        }

        # >, >=
        # TODO: correct ???
        I = {PredicateLiteral('p', Number(0))}
        J = {PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))}
        # I subset J
        self.assertFalse( aggr_func.propagate((Guard(RelOp.GREATER_OR_EQ, Number(1), True), None), element_instances, I, J) )
        self.assertFalse( aggr_func.propagate((Guard(RelOp.GREATER,       Number(1), True), None), element_instances, I, J) )
        # J subset I
        self.assertTrue(  aggr_func.propagate((Guard(RelOp.GREATER_OR_EQ, Number(1), True), None), element_instances, J, I) )
        self.assertFalse( aggr_func.propagate((Guard(RelOp.GREATER,       Number(1), True), None), element_instances, J, I) )

        # <, <=
        # TODO: correct ???
        I = {PredicateLiteral('p', Number(0))}
        J = {PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))}
        # I subset J
        self.assertTrue(  aggr_func.propagate((Guard(RelOp.LESS_OR_EQ, Number(1), True), None), element_instances, I, J) )
        self.assertTrue(  aggr_func.propagate((Guard(RelOp.LESS,       Number(1), True), None), element_instances, I, J) )
        # J subset I
        self.assertTrue(  aggr_func.propagate((Guard(RelOp.LESS_OR_EQ, Number(1), True), None), element_instances, J, I) )
        self.assertFalse( aggr_func.propagate((Guard(RelOp.LESS,       Number(1), True), None), element_instances, J, I) )

        # =
        # TODO: correct ???
        I = {PredicateLiteral('p', Number(0))}
        J = {PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))}
        # I subset J
        self.assertFalse( aggr_func.propagate((Guard(RelOp.EQUAL, Number(1), True), None), element_instances, I, J) )
        # J subset I
        self.assertTrue(  aggr_func.propagate((Guard(RelOp.EQUAL, Number(1), True), None), element_instances, J, I) )

        # !=
        # TODO: correct ???
        I = {PredicateLiteral('p', Number(0))}
        J = {PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))}
        # I subset J
        self.assertTrue(  aggr_func.propagate((Guard(RelOp.UNEQUAL, Number(1), True), None), element_instances, I, J) )
        # J subset I
        self.assertFalse( aggr_func.propagate((Guard(RelOp.UNEQUAL, Number(1), True), None), element_instances, J, I) )

        # TODO: two different guards at a time
        # TODO: special cases?

    def test_aggregate_max(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        aggr_func = AggregateMax()
        # equality
        self.assertEqual(aggr_func, AggregateMax())
        # hashing
        self.assertEqual(hash(aggr_func), hash(AggregateMax()))
        # string representation
        self.assertEqual(str(aggr_func), '#max')
        # base value
        self.assertEqual(aggr_func.base(), Infimum())
        # evaluation
        self.assertEqual(aggr_func.eval({TermTuple(Number(5)), TermTuple(Number(-3))}), Number(5))

        # ----- propagation -----
        element_instances = {
            AggregateElement(
                TermTuple(Number(0)),
                LiteralTuple(PredicateLiteral('p', Number(0)))
            ),
            AggregateElement(
                TermTuple(Number(1)),
                LiteralTuple(PredicateLiteral('p', Number(1))),
            )
        }

        # >, >=
        # TODO: correct ???
        A = {PredicateLiteral('p', Number(0))}
        B = {PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))}
        # I subset J
        self.assertTrue(  aggr_func.propagate((Guard(RelOp.GREATER_OR_EQ, Number(1), True), None), element_instances, A, B) )
        self.assertFalse( aggr_func.propagate((Guard(RelOp.GREATER,       Number(1), True), None), element_instances, A, B) )
        # J subset I
        self.assertFalse( aggr_func.propagate((Guard(RelOp.GREATER_OR_EQ, Number(1), True), None), element_instances, B, A) )
        self.assertFalse( aggr_func.propagate((Guard(RelOp.GREATER,       Number(1), True), None), element_instances, B, A) )

        # <, <=
        # TODO: correct ???
        A = {PredicateLiteral('p', Number(0))}
        B = {PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))}
        # I subset J
        self.assertTrue(  aggr_func.propagate((Guard(RelOp.LESS_OR_EQ, Number(1), True), None), element_instances, A, B) )
        self.assertTrue(  aggr_func.propagate((Guard(RelOp.LESS,       Number(1), True), None), element_instances, A, B) )
        # J subset I
        self.assertTrue(  aggr_func.propagate((Guard(RelOp.LESS_OR_EQ, Number(1), True), None), element_instances, B, A) )
        self.assertFalse( aggr_func.propagate((Guard(RelOp.LESS,       Number(1), True), None), element_instances, B, A) )

        # =
        # TODO: correct ???
        A = {PredicateLiteral('p', Number(0))}
        B = {PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))}
        # I subset J
        self.assertFalse( aggr_func.propagate((Guard(RelOp.EQUAL, Number(1), True), None), element_instances, A, B) )
        # J subset I
        self.assertFalse(  aggr_func.propagate((Guard(RelOp.EQUAL, Number(1), True), None), element_instances, B, A) )

        # !=
        # TODO: correct ???
        A = {PredicateLiteral('p', Number(0))}
        B = {PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))}
        # I subset J
        self.assertTrue(  aggr_func.propagate((Guard(RelOp.UNEQUAL, Number(1), True), None), element_instances, A, B) )
        # J subset I
        self.assertFalse( aggr_func.propagate((Guard(RelOp.UNEQUAL, Number(1), True), None), element_instances, B, A) )

        # TODO: two different guards at a time
        # TODO: special cases?

    def test_aggregate_min(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        aggr_func = AggregateMin()
        # equality
        self.assertEqual(aggr_func, AggregateMin())
        # hashing
        self.assertEqual(hash(aggr_func), hash(AggregateMin()))
        # string representation
        self.assertEqual(str(aggr_func), '#min')
        # base value
        self.assertEqual(aggr_func.base(), Supremum())
        # evaluation
        self.assertEqual(aggr_func.eval({TermTuple(Number(5)), TermTuple(Number(-3))}), Number(-3))

        # ----- propagation -----
        element_instances = {
            AggregateElement(
                TermTuple(Number(0)),
                LiteralTuple(PredicateLiteral('p', Number(0)))
            ),
            AggregateElement(
                TermTuple(Number(1)),
                LiteralTuple(PredicateLiteral('p', Number(1))),
            )
        }

        # >, >=
        # TODO: correct ???
        A = {PredicateLiteral('p', Number(0))}
        B = {PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))}
        # I subset J
        self.assertFalse( aggr_func.propagate((Guard(RelOp.GREATER_OR_EQ, Number(1), True), None), element_instances, A, B) )
        self.assertFalse( aggr_func.propagate((Guard(RelOp.GREATER,       Number(1), True), None), element_instances, A, B) )
        # J subset I
        self.assertFalse( aggr_func.propagate((Guard(RelOp.GREATER_OR_EQ, Number(1), True), None), element_instances, B, A) )
        self.assertFalse( aggr_func.propagate((Guard(RelOp.GREATER,       Number(1), True), None), element_instances, B, A) )

        # <, <=
        # TODO: correct ???
        A = {PredicateLiteral('p', Number(0))}
        B = {PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))}
        # I subset J
        self.assertTrue( aggr_func.propagate((Guard(RelOp.LESS_OR_EQ, Number(1), True), None), element_instances, A, B) )
        self.assertTrue( aggr_func.propagate((Guard(RelOp.LESS,       Number(1), True), None), element_instances, A, B) )
        # J subset I
        self.assertTrue( aggr_func.propagate((Guard(RelOp.LESS_OR_EQ, Number(1), True), None), element_instances, B, A) )
        self.assertTrue( aggr_func.propagate((Guard(RelOp.LESS,       Number(1), True), None), element_instances, B, A) )

        # =
        # TODO: correct ???
        A = {PredicateLiteral('p', Number(0))}
        B = {PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))}
        # I subset J
        self.assertFalse( aggr_func.propagate((Guard(RelOp.EQUAL, Number(1), True), None), element_instances, A, B) )
        # J subset I
        self.assertFalse( aggr_func.propagate((Guard(RelOp.EQUAL, Number(1), True), None), element_instances, B, A) )

        # !=
        # TODO: correct ???
        A = {PredicateLiteral('p', Number(0))}
        B = {PredicateLiteral('p', Number(0)), PredicateLiteral('p', Number(1))}
        # I subset J
        self.assertTrue( aggr_func.propagate((Guard(RelOp.UNEQUAL, Number(1), True), None), element_instances, A, B) )
        # J subset I
        self.assertTrue( aggr_func.propagate((Guard(RelOp.UNEQUAL, Number(1), True), None), element_instances, B, A) )

        # TODO: two different guards at a time
        # TODO: special cases?

    def test_aggregate_literal(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        ground_elements = (
            AggregateElement(
                TermTuple(Number(5)),
                LiteralTuple(PredicateLiteral('p', String('str')), Naf(PredicateLiteral('q')))
            ),
            AggregateElement(
                TermTuple(Number(-3)),
                LiteralTuple(Naf(PredicateLiteral('p', String('str'))))
            )
        )
        aggr_func = AggregateCount()

        # no guards
        self.assertRaises(ValueError, AggregateLiteral, aggr_func, ground_elements, tuple())
        # left guard only
        ground_literal = AggregateLiteral(aggr_func, ground_elements, guards=Guard(RelOp.LESS, Number(3), False))
        self.assertEqual(ground_literal.lguard, Guard(RelOp.LESS, Number(3), False))
        self.assertEqual(ground_literal.rguard, None)
        self.assertEqual(ground_literal.guards, (Guard(RelOp.LESS, Number(3), False), None))
        self.assertFalse(ground_literal.eval())
        self.assertEqual(str(ground_literal), '3 < #count{5:p("str"),not q;-3:not p("str")}')
        # right guard only
        ground_literal = AggregateLiteral(aggr_func, ground_elements, Guard(RelOp.LESS, Number(3), True), naf=True)
        self.assertEqual(ground_literal.lguard, None)
        self.assertEqual(ground_literal.rguard, Guard(RelOp.LESS, Number(3), True))
        self.assertEqual(ground_literal.guards, (None, Guard(RelOp.LESS, Number(3), True)))
        self.assertTrue(ground_literal.eval())
        self.assertEqual(str(ground_literal), 'not #count{5:p("str"),not q;-3:not p("str")} < 3')
        # both guards
        ground_literal = AggregateLiteral(aggr_func, ground_elements, guards=(Guard(RelOp.LESS, Number(3), False), Guard(RelOp.LESS, Number(3), True)))
        self.assertEqual(ground_literal.lguard, Guard(RelOp.LESS, Number(3), False))
        self.assertEqual(ground_literal.rguard, Guard(RelOp.LESS, Number(3), True))
        self.assertEqual(ground_literal.guards, (Guard(RelOp.LESS, Number(3), False), Guard(RelOp.LESS, Number(3), True)))
        self.assertFalse(ground_literal.eval())
        self.assertEqual(str(ground_literal), '3 < #count{5:p("str"),not q;-3:not p("str")} < 3')

        var_elements = (
            AggregateElement(
                TermTuple(Number(5)),
                LiteralTuple(PredicateLiteral('p', Variable('X')), Naf(PredicateLiteral('q')))
            ),
            AggregateElement(
                TermTuple(Number(-3)),
                LiteralTuple(Naf(PredicateLiteral('p', String('str'))))
            )
        )
        var_literal = AggregateLiteral(aggr_func, var_elements, guards=Guard(RelOp.LESS, Variable('Y'), False))

        # equality
        self.assertEqual(ground_literal, AggregateLiteral(aggr_func, ground_elements, guards=(Guard(RelOp.LESS, Number(3), False), Guard(RelOp.LESS, Number(3), True))))
        # hashing
        self.assertEqual(hash(ground_literal), hash(AggregateLiteral(aggr_func, ground_elements, guards=(Guard(RelOp.LESS, Number(3), False), Guard(RelOp.LESS, Number(3), True)))))
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
        self.assertTrue(ground_literal.invars() == ground_literal.outvars() == ground_literal.vars() == ground_literal.vars(True) == set())
        self.assertEqual(var_literal.invars(), {Variable('X')})
        self.assertEqual(var_literal.outvars(), {Variable('Y')})
        self.assertEqual(var_literal.vars(), {Variable('X'), Variable('Y')})
        self.assertEqual(var_literal.vars(True), {Variable('Y')})
        # positive/negative literal occurrences
        self.assertEqual(var_literal.pos_occ(), {PredicateLiteral('p', Variable('X'))})
        self.assertEqual(var_literal.neg_occ(), {PredicateLiteral('p', String('str')), PredicateLiteral('q')})

        # safety characterization
        self.assertEqual(var_literal.safety(global_vars={Variable('X')}), SafetyTriplet(unsafe={Variable('X')}))
        self.assertEqual(var_literal.safety(global_vars={Variable('Y')}), SafetyTriplet())
        self.assertEqual(AggregateLiteral(aggr_func, var_elements, Guard(RelOp.LESS, Variable('X'), False)).safety(global_vars={Variable('X')}), SafetyTriplet(unsafe={Variable('X')}))
        self.assertEqual(AggregateLiteral(aggr_func, var_elements, Guard(RelOp.LESS, Variable('X'), False)).safety(global_vars={Variable('Y')}), SafetyTriplet())
        # aggr_global_invars = {'X'}
        # aggr_global_vars = {'X','Y'} -> unsafe
        # rules = { ('Y', {'X'}) }
        self.assertEqual(AggregateLiteral(aggr_func, var_elements, guards=Guard(RelOp.EQUAL, Variable('Y'), False)).safety(global_vars={Variable('X'), Variable('Y')}), SafetyTriplet(unsafe={Variable('X'), Variable('Y')}, rules={SafetyRule(Variable('Y'), {Variable('X')})}))
        # aggr_global_invars = {}
        # aggr_global_vars = {'Y'} -> unsafe
        # rules = { ('Y', {}) } -> makes 'Y' safe
        self.assertEqual(AggregateLiteral(aggr_func, var_elements, guards=Guard(RelOp.EQUAL, Variable('Y'), False)).safety(global_vars={Variable('Y')}), SafetyTriplet(safe={Variable('Y')}))
        # aggr_global_invars = {'X'}
        # aggr_global_vars = {'X'} -> unsafe
        # rules = { ('X', {'X'}) } -> removes (without making 'X' safe)
        self.assertEqual(AggregateLiteral(aggr_func, var_elements, guards=Guard(RelOp.EQUAL, Variable('X'), False)).safety(global_vars={Variable('X')}), SafetyTriplet(unsafe={Variable('X')}))
        # aggr_global_invars = {}
        # aggr_global_vars = {'X'} -> unsafe
        # rules = { ('X', {}) } -> makes 'X' safe
        self.assertEqual(AggregateLiteral(aggr_func, var_elements, guards=Guard(RelOp.EQUAL, Variable('X'), False)).safety(global_vars={Variable('Y')}), SafetyTriplet(safe={Variable('X')}))
        # TODO: safety characterization for case with two guards

        # replace arithmetic terms
        arith_elements = ( AggregateElement(TermTuple(Number(5)), LiteralTuple(PredicateLiteral('p', Minus(Variable('X'))), Naf(PredicateLiteral('q')))), )
        arith_literal = Naf(AggregateLiteral(aggr_func, arith_elements, Guard(RelOp.EQUAL, Minus(Variable('X')), True)))
        self.assertEqual(arith_literal.replace_arith(VariableTable()),
            Naf(AggregateLiteral(
                aggr_func,
                ( AggregateElement(TermTuple(Number(5)), LiteralTuple(PredicateLiteral('p', ArithVariable(0, Minus(Variable('X')))), Naf(PredicateLiteral('q')))),  ),
                Guard(RelOp.EQUAL, ArithVariable(1, Minus(Variable('X'))), True)
            ))
        )
        
        # substitute
        var_literal = AggregateLiteral(aggr_func, var_elements, Guard(RelOp.LESS, Variable('X'), False))
        self.assertEqual(var_literal.substitute(Substitution({Variable('X'): Number(1), Number(-3): String('f')})), # NOTE: substitution is invalid
            AggregateLiteral(AggregateCount(), (
                AggregateElement(
                    TermTuple(Number(5)),
                    LiteralTuple(PredicateLiteral('p', Number(1)), Naf(PredicateLiteral('q')))
                ),
                AggregateElement(
                    TermTuple(Number(-3)),
                    LiteralTuple(Naf(PredicateLiteral('p', String('str'))))
                )
            ), guards=Guard(RelOp.LESS, Number(1), False)
        ))


if __name__ == "__main__":
    unittest.main()


