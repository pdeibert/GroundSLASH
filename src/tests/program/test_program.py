import unittest

import aspy
from aspy.grounding import Grounder
from aspy.program.terms import Variable, Number, Add, ArithVariable, TermTuple
from aspy.program.literals import Neg, Naf, LiteralTuple, PredicateLiteral, Equal, AggregateLiteral, AggregateCount, AggregateSum, AggregateElement, Guard
from aspy.program.operators import RelOp
from aspy.program.substitution import Substitution
from aspy.program.statements import NormalFact, NormalRule
from aspy.program.program import Program


class TestProgram(unittest.TestCase):
    def test_program(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        prog = Program((
            NormalRule(PredicateLiteral('a'), Naf(PredicateLiteral('b'))),
            NormalRule(PredicateLiteral('b'), Naf(PredicateLiteral('a'))),
            NormalFact(PredicateLiteral('c')),
            NormalRule(PredicateLiteral('d'), AggregateLiteral(AggregateSum(), (AggregateElement(TermTuple(Number(1)), LiteralTuple(PredicateLiteral('a'))), AggregateElement(TermTuple(Number(1)), LiteralTuple(PredicateLiteral('c')))), Guard(RelOp.EQUAL, Number(1), True))),
            NormalRule(PredicateLiteral('e'), Naf(PredicateLiteral('d'))),
        ))
        # TODO: query!

        # string representation
        self.assertEqual(str(prog), '\n'.join(tuple(str(statement) for statement in prog.statements)))
        # safety
        self.assertTrue(prog.safe)
        # reduct
        self.assertEqual(prog.reduct({('c', 0)}), prog)
        self.assertEqual(
            prog.reduct({('a', 0), ('d', 0)}),
            Program((
                NormalRule(PredicateLiteral('a'), Naf(PredicateLiteral('b'))),
                NormalFact(PredicateLiteral('c')),
                NormalRule(PredicateLiteral('d'), AggregateLiteral(AggregateSum(), (AggregateElement(TermTuple(Number(1)), LiteralTuple(PredicateLiteral('a'))), AggregateElement(TermTuple(Number(1)), LiteralTuple(PredicateLiteral('c')))), Guard(RelOp.EQUAL, Number(1), True))),
            ))
        )
        # replace arithmetic terms
        # rewrite aggregates


if __name__ == "__main__":
    unittest.main()