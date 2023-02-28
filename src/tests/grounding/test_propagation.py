import unittest

import aspy
from aspy.grounding.propagation import Propagator
from aspy.program.literals import AggregateLiteral, AlphaLiteral, EpsLiteral, EtaLiteral, AggregateElement, AggregateCount, LiteralTuple, PredicateLiteral, Guard, Equal, GreaterEqual, LessEqual
from aspy.program.terms import Variable, Number, TermTuple
from aspy.program.statements import NormalFact, NormalRule, EpsRule, EtaRule



from aspy.program.terms import Variable, Number, Add, ArithVariable
from aspy.program.operators import RelOp
from aspy.program.substitution import Substitution


class TestPropagation(unittest.TestCase):
    def test_propagator(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        elements_1 = (AggregateElement(TermTuple(Variable('Y')), LiteralTuple(PredicateLiteral('p', Variable('Y')))), AggregateElement(TermTuple(Number(0)), LiteralTuple(PredicateLiteral('p', Number(0)))))
        elements_2 = (AggregateElement(TermTuple(Number(0)), LiteralTuple(PredicateLiteral('q', Number(0)))),)

        # initialization of propagator
        aggr_map = {
            1: (
                AggregateLiteral(AggregateCount(), 
                    elements_1,
                    Guard(RelOp.GREATER_OR_EQ, Variable('X'), True)
                ),
                AlphaLiteral(1, TermTuple(Variable('X')), TermTuple(Variable('X'))),
                EpsRule(
                    EpsLiteral(1, TermTuple(Variable('X')), TermTuple(Variable('X'))),
                    Guard(RelOp.GREATER_OR_EQ, Variable('X'), True),
                    None,
                    LiteralTuple(
                        GreaterEqual(AggregateCount().base(), Variable('X')),
                        PredicateLiteral('q', Variable('X')),
                        Equal(Number(0), Variable('X'))
                    )
                ),
                [
                    EtaRule(
                        EtaLiteral(1, 0, TermTuple(Variable('Y')), TermTuple(Variable('X')), TermTuple(Variable('Y'), Variable('X'))),
                        elements_1[0],
                        LiteralTuple(
                            PredicateLiteral('p', Variable('Y')),
                            PredicateLiteral('q', Variable('X')),
                            Equal(Number(0), Variable('X'))
                        )
                    ),
                    EtaRule(
                        EtaLiteral(1, 1, TermTuple(), TermTuple(Variable('X')), TermTuple(Variable('X'))),
                        elements_1[1],
                        LiteralTuple(
                            PredicateLiteral('p', Number(0)),
                            PredicateLiteral('q', Variable('X')),
                            Equal(Number(0), Variable('X'))
                        )
                    )
                ]
            ),
            2: (
                AggregateLiteral(AggregateCount(), 
                    elements_2,
                    Guard(RelOp.LESS_OR_EQ, Number(0), False)
                ),
                AlphaLiteral(2, TermTuple(), TermTuple()),
                EpsRule(
                    EpsLiteral(2, TermTuple(), TermTuple()),
                    None,
                    Guard(RelOp.LESS_OR_EQ, Number(0), False),
                    LiteralTuple(
                        LessEqual(Number(0), AggregateCount().base()),
                        PredicateLiteral('q', Variable('X')),
                        Equal(Number(0), Variable('X'))
                    )
                ),
                [
                    EtaRule(
                        EtaLiteral(2, 0, TermTuple(), TermTuple(), TermTuple()),
                        elements_2[0],
                        LiteralTuple(
                            PredicateLiteral('q', Number(0)),
                            PredicateLiteral('q', Variable('X')),
                            Equal(Number(0), Variable('X'))
                        )
                    )
                ]
            )
        }
        propagator = Propagator(aggr_map)
        self.assertEqual(propagator.aggr_map, aggr_map)
        self.assertEqual(propagator.instance_map, dict())

        # propagation
        eps_instances = {
            # aggregate 1
            EpsRule(
                EpsLiteral(1, TermTuple(Variable('X')), TermTuple(Number(0))),
                Guard(RelOp.GREATER_OR_EQ, Variable('X'), True),
                None,
                LiteralTuple(
                    GreaterEqual(AggregateCount().base(), Number(0)),
                    PredicateLiteral('q', Number(0)),
                    Equal(Number(0), Number(0))
                )
            ),
            # aggregate 2
            EpsRule(
                EpsLiteral(2, TermTuple(), TermTuple()),
                None,
                Guard(RelOp.LESS_OR_EQ, Number(0), False),
                LiteralTuple(
                    LessEqual(Number(0), AggregateCount().base()),
                    PredicateLiteral('q', Number(0)),
                    Equal(Number(0), Number(0))
                )
            )
        }
        eta_instances = {
            # aggregate 1
            # element 0
            EtaRule(
                EtaLiteral(1, 0, TermTuple(Variable('Y')), TermTuple(Variable('X')), TermTuple(Number(0), Number(0))),
                elements_1[0],
                LiteralTuple(
                    PredicateLiteral('p', Number(0)),
                    PredicateLiteral('q', Number(0)),
                    Equal(Number(0), Number(0))
                )
            ),
            EtaRule(
                EtaLiteral(1, 0, TermTuple(Variable('Y')), TermTuple(Variable('X')), TermTuple(Number(1), Number(0))),
                elements_1[0],
                LiteralTuple(
                    PredicateLiteral('p', Number(1)),
                    PredicateLiteral('q', Number(0)),
                    Equal(Number(0), Number(0))
                )
            ),
            # element 1
            EtaRule(
                EtaLiteral(1, 1, TermTuple(), TermTuple(Variable('X')), TermTuple(Number(0))),
                elements_1[1],
                LiteralTuple(
                    PredicateLiteral('p', Number(0)),
                    PredicateLiteral('q', Number(0)),
                    Equal(Number(0), Number(0))
                )
            ),
            # aggregate 2
            EtaRule(
                EtaLiteral(2, 0, TermTuple(), TermTuple(), TermTuple()),
                elements_2[0],
                LiteralTuple(
                    PredicateLiteral('q', Number(0)),
                    PredicateLiteral('q', Number(0)),
                    Equal(Number(0), Number(0))
                )
            )
        }

        domain = {
            PredicateLiteral('p', Number(0)),
            PredicateLiteral('p', Number(1)),
            PredicateLiteral('q', Number(0)),
            PredicateLiteral('q', Number(1))
        }
        J_alpha = propagator.propagate(eps_instances, eta_instances, domain, domain)
        self.assertEqual(J_alpha,
            {
                AlphaLiteral(1, TermTuple(Variable('X')), TermTuple(Number(0))),
                AlphaLiteral(2, TermTuple(), TermTuple()),
            }
        )

        # assembling
        rule = NormalRule(
            PredicateLiteral('p', Variable('X'), Number(0)),
            AlphaLiteral(1, TermTuple(Variable('X')), TermTuple(Variable('X'))),
            PredicateLiteral('q', Variable('X')),
            Equal(Number(0), Variable('X')),
            AlphaLiteral(2, TermTuple(), TermTuple())
        )
        rules = propagator.assemble({rule})
        self.assertEqual(len(rules), 1)
        self.assertTrue(rules.pop() == \
            NormalRule(
                PredicateLiteral('p', Variable('X'), Number(0)),
                AggregateLiteral(
                    AggregateCount(),
                    (AggregateElement(Number(0), PredicateLiteral('p', Number(0))), AggregateElement(Number(1), PredicateLiteral('p', Number(1)))), # first possible element order
                    Guard(RelOp.GREATER_OR_EQ, Variable('X'), True)
                ),
                PredicateLiteral('q', Number(0)),
                Equal(Number(0), Number(0)),
                AggregateLiteral(AggregateCount(), 
                    (AggregateElement(TermTuple(Number(0)), LiteralTuple(PredicateLiteral('q', Number(0)))),),
                    Guard(RelOp.LESS_OR_EQ, Number(0), False)
                )
            ) or \
            NormalRule(
                PredicateLiteral('p', Variable('X'), Number(0)),
                AggregateLiteral(
                    AggregateCount(),
                    (AggregateElement(Number(1), PredicateLiteral('p', Number(1))), AggregateElement(Number(0), PredicateLiteral('p', Number(0)))), # second possible element order
                    Guard(RelOp.GREATER_OR_EQ, Variable('X'), True)
                ),
                PredicateLiteral('q', Number(0)),
                Equal(Number(0), Number(0)),
                AggregateLiteral(AggregateCount(), 
                    (AggregateElement(TermTuple(Number(0)), LiteralTuple(PredicateLiteral('q', Number(0)))),),
                    Guard(RelOp.LESS_OR_EQ, Number(0), False)
                )
            )
        )


if __name__ == "__main__":
    unittest.main()