import unittest

import aspy
from aspy.program.literals import (
    AggregateCount,
    AggregateElement,
    AggregateLiteral,
    AggregateMax,
    AggregateMin,
    AggregateSum,
    Equal,
    Greater,
    GreaterEqual,
    Guard,
    Less,
    LessEqual,
    LiteralTuple,
    Naf,
    Neg,
    PredicateLiteral,
    Unequal,
)
from aspy.program.operators import RelOp
from aspy.program.program import Program
from aspy.program.statements import (
    Choice,
    ChoiceElement,
    ChoiceFact,
    ChoiceRule,
    Constraint,
    DisjunctiveFact,
    DisjunctiveRule,
    NormalFact,
    NormalRule,
)
from aspy.program.terms import (
    Add,
    AnonVariable,
    Div,
    Functional,
    Mult,
    Number,
    String,
    Sub,
    SymbolicConstant,
    TermTuple,
    Variable,
)


class TestProgram(unittest.TestCase):
    def test_program(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        prog = Program(
            (
                NormalRule(PredicateLiteral("a"), Naf(PredicateLiteral("b"))),
                NormalRule(PredicateLiteral("b"), Naf(PredicateLiteral("a"))),
                NormalFact(PredicateLiteral("c")),
                NormalRule(
                    PredicateLiteral("d"),
                    AggregateLiteral(
                        AggregateSum(),
                        (
                            AggregateElement(
                                TermTuple(Number(1)),
                                LiteralTuple(PredicateLiteral("a")),
                            ),
                            AggregateElement(
                                TermTuple(Number(1)),
                                LiteralTuple(PredicateLiteral("c")),
                            ),
                        ),
                        Guard(RelOp.EQUAL, Number(1), True),
                    ),
                ),
                NormalRule(PredicateLiteral("e"), Naf(PredicateLiteral("d"))),
            )
        )
        # TODO: query!

        # string representation
        self.assertEqual(
            str(prog), "\n".join(tuple(str(statement) for statement in prog.statements))
        )
        # safety
        self.assertTrue(prog.safe)
        # reduct
        self.assertEqual(prog.reduct({("c", 0)}), prog)
        self.assertEqual(
            prog.reduct({("a", 0), ("d", 0)}),
            Program(
                (
                    NormalRule(PredicateLiteral("a"), Naf(PredicateLiteral("b"))),
                    NormalFact(PredicateLiteral("c")),
                    NormalRule(
                        PredicateLiteral("d"),
                        AggregateLiteral(
                            AggregateSum(),
                            (
                                AggregateElement(
                                    TermTuple(Number(1)),
                                    LiteralTuple(PredicateLiteral("a")),
                                ),
                                AggregateElement(
                                    TermTuple(Number(1)),
                                    LiteralTuple(PredicateLiteral("c")),
                                ),
                            ),
                            Guard(RelOp.EQUAL, Number(1), True),
                        ),
                    ),
                )
            ),
        )
        # TODO: replace arithmetic terms
        # TODO: rewrite aggregates

    def test_from_string(self):

        # ----- terms -----
        # NOTE: use normal facts and predicate literals to check
        # (somewhat of a circular test)

        # variable
        self.assertEqual(
            Program.from_string("p(X).").statements[0].atom.terms[0], Variable("X")
        )
        # anonymous variable
        self.assertEqual(
            Program.from_string("p(_).").statements[0].atom.terms[0], AnonVariable(0)
        )
        self.assertEqual(
            Program.from_string("p(_, _).")
            .statements[0]
            .atom.terms,  # multiple anonymous variables should get distinct ids
            TermTuple(AnonVariable(0), AnonVariable(1)),
        )
        # string
        self.assertEqual(
            Program.from_string(r'p("string: \"internal string\" ").')
            .statements[0]
            .atom.terms[0],  # includes escaped string
            String(r"string: \"internal string\" "),
        )
        self.assertEqual(
            Program.from_string(r'p("10").').statements[0].atom.terms[0], String("10")
        )
        # number
        self.assertEqual(
            Program.from_string("p(-10).").statements[0].atom.terms[0], Number(-10)
        )
        # symbolic constant
        self.assertEqual(
            Program.from_string("p(p).").statements[0].atom.terms[0],
            SymbolicConstant("p"),
        )
        # functional term (empty vs. symbolic constant)
        self.assertEqual(
            Program.from_string("p(p()).").statements[0].atom.terms[0], Functional("p")
        )  # empty
        self.assertEqual(
            Program.from_string('p(p("string", 10)).').statements[0].atom.terms[0],
            Functional("p", String("string"), Number(10)),
        )
        # arithmetic term (add, sub, mult, div, minus)
        self.assertEqual(
            Program.from_string("p(3+X).").statements[0].atom.terms[0],
            Add(Number(3), Variable("X")),  # add
        )
        self.assertEqual(
            Program.from_string("p(3-X).").statements[0].atom.terms[0],
            Sub(Number(3), Variable("X")),  # sub
        )
        self.assertEqual(
            Program.from_string("p(3*X).").statements[0].atom.terms[0],
            Mult(Number(3), Variable("X")),  # mult
        )
        self.assertEqual(
            Program.from_string("p(3/X).").statements[0].atom.terms[0],
            Div(Number(3), Variable("X")),  # div
        )
        self.assertEqual(
            Program.from_string("p(3+-5*(10-3)).")
            .statements[0]
            .atom.terms[0],  # order of operations
            Number(3 + (-5 * (10 - 3))),
        )

        # ----- literals -----
        # NOTE: use normal facts and rules to check (somewhat of a circular test)

        # predicate literal
        self.assertEqual(
            Program.from_string("p().").statements[0].atom, PredicateLiteral("p")
        )  # zero-ary predicate
        self.assertEqual(
            Program.from_string("p.").statements[0].atom,  # dropped parentheses
            Program.from_string("p().").statements[0].atom,
        )
        self.assertEqual(
            Program.from_string("-p.").statements[0].atom,
            Neg(PredicateLiteral("p")),  # classical negation
        )
        self.assertEqual(
            Program.from_string("a :- not p.")
            .statements[0]
            .body[0],  # negation as failure (NAF)
            Naf(PredicateLiteral("p")),
        )

        # builtin literal
        self.assertEqual(
            Program.from_string("a :- 1 = 2.").statements[0].body[0],
            Equal(Number(1), Number(2)),
        )  # equal
        self.assertEqual(
            Program.from_string("a :- 1 != 2.").statements[0].body[0],
            Unequal(Number(1), Number(2)),  # unequal
        )
        self.assertEqual(
            Program.from_string("a :- 1 < 2.").statements[0].body[0],
            Less(Number(1), Number(2)),  # less than
        )
        self.assertEqual(
            Program.from_string("a :- 1 > 2.").statements[0].body[0],
            Greater(Number(1), Number(2)),  # greater than
        )
        self.assertEqual(
            Program.from_string("a :- 1 <= 2.")
            .statements[0]
            .body[0],  # less than or equal
            LessEqual(Number(1), Number(2)),
        )
        self.assertEqual(
            Program.from_string("a :- 1 >= 2.")
            .statements[0]
            .body[0],  # greater than or equal
            GreaterEqual(Number(1), Number(2)),
        )

        # aggregate literal
        self.assertEqual(
            Program.from_string(r"a :- 3 = #count{X: p(X)}.")
            .statements[0]
            .body[0],  # only left guard
            AggregateLiteral(
                AggregateCount(),
                (
                    AggregateElement(
                        TermTuple(Variable("X")),
                        LiteralTuple(PredicateLiteral("p", Variable("X"))),
                    ),
                ),
                (Guard(RelOp.EQUAL, Number(3), False), None),
            ),
        )
        self.assertEqual(
            Program.from_string(r"a :- #count{X: p(X)} = 3.")
            .statements[0]
            .body[0],  # only right guard
            AggregateLiteral(
                AggregateCount(),
                (
                    AggregateElement(
                        TermTuple(Variable("X")),
                        LiteralTuple(PredicateLiteral("p", Variable("X"))),
                    ),
                ),
                (None, Guard(RelOp.EQUAL, Number(3), True)),
            ),
        )
        self.assertEqual(
            Program.from_string(r"a :- 5 < #count{X: p(X)} = 3.")
            .statements[0]
            .body[0],  # only right guard
            AggregateLiteral(
                AggregateCount(),
                (
                    AggregateElement(
                        TermTuple(Variable("X")),
                        LiteralTuple(PredicateLiteral("p", Variable("X"))),
                    ),
                ),
                (
                    Guard(RelOp.LESS, Number(5), False),
                    Guard(RelOp.EQUAL, Number(3), True),
                ),
            ),
        )
        self.assertEqual(
            Program.from_string(r"a :- 5 < #count{} = 3.")
            .statements[0]
            .body[0],  # no elements
            AggregateLiteral(
                AggregateCount(),
                tuple(),
                (
                    Guard(RelOp.LESS, Number(5), False),
                    Guard(RelOp.EQUAL, Number(3), True),
                ),
            ),
        )
        self.assertEqual(
            Program.from_string(r"a :- 5 < #count{X:} = 3.")
            .statements[0]
            .body[0],  # element without literals (i.e., condition)
            AggregateLiteral(
                AggregateCount(),
                (AggregateElement(TermTuple(Variable("X")), LiteralTuple()),),
                (
                    Guard(RelOp.LESS, Number(5), False),
                    Guard(RelOp.EQUAL, Number(3), True),
                ),
            ),
        )
        self.assertEqual(
            Program.from_string(r"a :- 5 < #count{:p(X)} = 3.")
            .statements[0]
            .body[0],  # element without terms
            AggregateLiteral(
                AggregateCount(),
                (
                    AggregateElement(
                        TermTuple(), LiteralTuple(PredicateLiteral("p", Variable("X")))
                    ),
                ),
                (
                    Guard(RelOp.LESS, Number(5), False),
                    Guard(RelOp.EQUAL, Number(3), True),
                ),
            ),
        )
        self.assertEqual(
            Program.from_string(r"a :- 5 < #count{:} = 3.")
            .statements[0]
            .body[0],  # element without terms or literals
            AggregateLiteral(
                AggregateCount(),
                tuple(),
                (
                    Guard(RelOp.LESS, Number(5), False),
                    Guard(RelOp.EQUAL, Number(3), True),
                ),
            ),
        )
        self.assertEqual(
            Program.from_string(r"a :- 5 < #count{X: p(X); X: q(X)} = 3.")
            .statements[0]
            .body[0],  # multiple elements
            AggregateLiteral(
                AggregateCount(),
                (
                    AggregateElement(
                        TermTuple(Variable("X")),
                        LiteralTuple(PredicateLiteral("p", Variable("X"))),
                    ),
                    AggregateElement(
                        TermTuple(Variable("X")),
                        LiteralTuple(PredicateLiteral("q", Variable("X"))),
                    ),
                ),
                (
                    Guard(RelOp.LESS, Number(5), False),
                    Guard(RelOp.EQUAL, Number(3), True),
                ),
            ),
        )
        self.assertEqual(
            Program.from_string(r"a :- 5 < #sum{} = 3.").statements[0].body[0],  # sum
            AggregateLiteral(
                AggregateSum(),
                tuple(),
                (
                    Guard(RelOp.LESS, Number(5), False),
                    Guard(RelOp.EQUAL, Number(3), True),
                ),
            ),
        )
        self.assertEqual(
            Program.from_string(r"a :- 5 < #min{} = 3.").statements[0].body[0],  # min
            AggregateLiteral(
                AggregateMin(),
                tuple(),
                (
                    Guard(RelOp.LESS, Number(5), False),
                    Guard(RelOp.EQUAL, Number(3), True),
                ),
            ),
        )
        self.assertEqual(
            Program.from_string(r"a :- 5 < #max{} = 3.").statements[0].body[0],  # max
            AggregateLiteral(
                AggregateMax(),
                tuple(),
                (
                    Guard(RelOp.LESS, Number(5), False),
                    Guard(RelOp.EQUAL, Number(3), True),
                ),
            ),
        )

        # ----- normal facts -----'
        self.assertEqual(
            Program.from_string("p.").statements[0], NormalFact(PredicateLiteral("p"))
        )

        # ----- normal rules -----
        self.assertEqual(
            Program.from_string("p :- q.").statements[0],
            NormalRule(PredicateLiteral("p"), PredicateLiteral("q")),
        )

        # ----- disjunctive facts -----
        self.assertEqual(
            Program.from_string("p | u | v.").statements[0],
            DisjunctiveFact(
                PredicateLiteral("p"), PredicateLiteral("u"), PredicateLiteral("v")
            ),
        )

        # ----- disjunctive rules -----
        self.assertEqual(
            Program.from_string("p | u | v :- q.").statements[0],
            DisjunctiveRule(
                (PredicateLiteral("p"), PredicateLiteral("u"), PredicateLiteral("v")),
                (PredicateLiteral("q"),),
            ),
        )

        # ----- choice facts -----
        self.assertEqual(
            Program.from_string(r"3 < {u:p;v:q} > 5.").statements[0],
            ChoiceFact(
                Choice(
                    (
                        ChoiceElement(PredicateLiteral("u"), (PredicateLiteral("p"),)),
                        ChoiceElement(PredicateLiteral("v"), (PredicateLiteral("q"),)),
                    ),
                    (
                        Guard(RelOp.LESS, Number(3), False),
                        Guard(RelOp.GREATER, Number(5), True),
                    ),
                )
            ),
        )

        # ----- choice rules -----
        self.assertEqual(
            Program.from_string(r"3 < {u:p;v:q} > 5 :- r, s.").statements[0],
            ChoiceRule(
                Choice(
                    (
                        ChoiceElement(PredicateLiteral("u"), (PredicateLiteral("p"),)),
                        ChoiceElement(PredicateLiteral("v"), (PredicateLiteral("q"),)),
                    ),
                    (
                        Guard(RelOp.LESS, Number(3), False),
                        Guard(RelOp.GREATER, Number(5), True),
                    ),
                ),
                (PredicateLiteral("r"), PredicateLiteral("s")),
            ),
        )

        # ----- constraint -----
        self.assertEqual(
            Program.from_string(":- p, q.").statements[0],
            Constraint(PredicateLiteral("p"), PredicateLiteral("q")),
        )

        # ----- weak constraint -----
        # TODO

        # ----- optimize statements -----
        # TODO


if __name__ == "__main__":
    unittest.main()
