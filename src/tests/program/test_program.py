try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

import ground_slash
from ground_slash.program.literals import (
    AggrCount,
    AggrElement,
    AggrLiteral,
    AggrMax,
    AggrMin,
    AggrSum,
    Equal,
    Greater,
    GreaterEqual,
    Guard,
    Less,
    LessEqual,
    LiteralCollection,
    Naf,
    Neg,
    PredLiteral,
    Unequal,
)
from ground_slash.program.operators import RelOp
from ground_slash.program.program import Program
from ground_slash.program.statements import (
    NPP,
    Choice,
    ChoiceElement,
    ChoiceRule,
    Constraint,
    DisjunctiveRule,
    NormalRule,
    NPPRule,
)
from ground_slash.program.terms import (
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


class TestProgram:
    def test_program(self: Self):
        # make sure debug mode is enabled
        assert ground_slash.debug()

        prog = Program(
            (
                NormalRule(PredLiteral("a"), [Naf(PredLiteral("b"))]),
                NormalRule(PredLiteral("b"), [Naf(PredLiteral("a"))]),
                NormalRule(PredLiteral("c")),
                NormalRule(
                    PredLiteral("d"),
                    [
                        AggrLiteral(
                            AggrSum(),
                            (
                                AggrElement(
                                    TermTuple(Number(1)),
                                    LiteralCollection(PredLiteral("a")),
                                ),
                                AggrElement(
                                    TermTuple(Number(1)),
                                    LiteralCollection(PredLiteral("c")),
                                ),
                            ),
                            Guard(RelOp.EQUAL, Number(1), True),
                        )
                    ],
                ),
                NormalRule(PredLiteral("e"), [Naf(PredLiteral("d"))]),
            )
        )
        # TODO: query!

        # string representation
        assert str(prog) == "\n".join(
            tuple(str(statement) for statement in prog.statements)
        )
        # safety
        assert prog.safe
        # reduct
        assert prog.reduct({("c", 0)}) == prog
        assert prog.reduct({("a", 0), ("d", 0)}) == Program(
            (
                NormalRule(PredLiteral("a"), [Naf(PredLiteral("b"))]),
                NormalRule(PredLiteral("c")),
                NormalRule(
                    PredLiteral("d"),
                    [
                        AggrLiteral(
                            AggrSum(),
                            (
                                AggrElement(
                                    TermTuple(Number(1)),
                                    LiteralCollection(PredLiteral("a")),
                                ),
                                AggrElement(
                                    TermTuple(Number(1)),
                                    LiteralCollection(PredLiteral("c")),
                                ),
                            ),
                            Guard(RelOp.EQUAL, Number(1), True),
                        )
                    ],
                ),
            )
        )
        # TODO: replace arithmetic terms
        # TODO: rewrite aggregates

    def test_from_string(self: Self):
        # ----- terms -----
        # NOTE: use normal facts and predicate literals to check
        # (somewhat of a circular test)

        # variable
        assert Program.from_string("p(X).").statements[0].atom.terms[0] == Variable("X")
        # anonymous variable
        assert Program.from_string("p(_).").statements[0].atom.terms[0] == AnonVariable(
            0
        )
        assert Program.from_string("p(_, _).").statements[0].atom.terms == TermTuple(
            AnonVariable(0), AnonVariable(1)
        )  # multiple anonymous variables should get distinct ids
        # string
        assert Program.from_string(r'p("string: \"internal string\" ").').statements[
            0
        ].atom.terms[0] == String(
            r"string: \"internal string\" "
        )  # includes escaped string
        assert Program.from_string(r'p("10").').statements[0].atom.terms[0] == String(
            "10"
        )
        # number
        assert Program.from_string("p(-10).").statements[0].atom.terms[0] == Number(-10)
        # symbolic constant
        assert Program.from_string("p(p).").statements[0].atom.terms[
            0
        ] == SymbolicConstant("p")
        # functional term (empty vs. symbolic constant)
        assert Program.from_string("p(p()).").statements[0].atom.terms[0] == Functional(
            "p"
        )  # empty
        assert Program.from_string('p(p("string", 10)).').statements[0].atom.terms[
            0
        ] == Functional("p", String("string"), Number(10))
        # arithmetic term (add, sub, mult, div, minus)
        assert Program.from_string("p(3+X).").statements[0].atom.terms[0] == Add(
            Number(3), Variable("X")
        )  # add
        assert Program.from_string("p(3-X).").statements[0].atom.terms[0] == Sub(
            Number(3), Variable("X")
        )  # sub
        assert Program.from_string("p(3*X).").statements[0].atom.terms[0] == Mult(
            Number(3), Variable("X")
        )  # mult
        assert Program.from_string("p(3/X).").statements[0].atom.terms[0] == Div(
            Number(3), Variable("X")
        )  # div
        assert Program.from_string("p(3+-5*(10-3)).").statements[0].atom.terms[
            0
        ] == Number(
            3 + (-5 * (10 - 3))
        )  # order of operations

        # ----- literals -----
        # NOTE: use normal facts and rules to check (somewhat of a circular test)

        # predicate literal
        assert Program.from_string("p().").statements[0].atom == PredLiteral(
            "p"
        )  # zero-ary predicate
        assert (
            Program.from_string("p.").statements[0].atom
            == Program.from_string("p().").statements[0].atom
        )  # dropped parentheses
        assert Program.from_string("-p.").statements[0].atom == Neg(
            PredLiteral("p")
        )  # classical negation
        assert Program.from_string("a :- not p.").statements[0].body[0] == Naf(
            PredLiteral("p")
        )  # negation as failure (NAF)

        # builtin literal
        assert Program.from_string("a :- 1 = 2.").statements[0].body[0] == Equal(
            Number(1), Number(2)
        )  # equal
        assert Program.from_string("a :- 1 != 2.").statements[0].body[0] == Unequal(
            Number(1), Number(2)
        )  # unequal
        assert Program.from_string("a :- 1 < 2.").statements[0].body[0] == Less(
            Number(1), Number(2)
        )  # less than
        assert Program.from_string("a :- 1 > 2.").statements[0].body[0] == Greater(
            Number(1), Number(2)
        )  # greater than
        assert Program.from_string("a :- 1 <= 2.").statements[0].body[0] == LessEqual(
            Number(1), Number(2)
        )  # less than or equal
        assert Program.from_string("a :- 1 >= 2.").statements[0].body[
            0
        ] == GreaterEqual(
            Number(1), Number(2)
        )  # greater than or equal

        # aggregate literal
        assert Program.from_string(r"a :- 3 = #count{X: p(X)}.").statements[0].body[
            0
        ] == AggrLiteral(
            AggrCount(),
            (
                AggrElement(
                    TermTuple(Variable("X")),
                    LiteralCollection(PredLiteral("p", Variable("X"))),
                ),
            ),
            (Guard(RelOp.EQUAL, Number(3), False), None),
        )  # only left guard
        assert Program.from_string(r"a :- #count{X: p(X)} = 3.").statements[0].body[
            0
        ] == AggrLiteral(
            AggrCount(),
            (
                AggrElement(
                    TermTuple(Variable("X")),
                    LiteralCollection(PredLiteral("p", Variable("X"))),
                ),
            ),
            (None, Guard(RelOp.EQUAL, Number(3), True)),
        )  # only right guard
        assert Program.from_string(r"a :- 5 < #count{X: p(X)} = 3.").statements[0].body[
            0
        ] == AggrLiteral(
            AggrCount(),
            (
                AggrElement(
                    TermTuple(Variable("X")),
                    LiteralCollection(PredLiteral("p", Variable("X"))),
                ),
            ),
            (
                Guard(RelOp.LESS, Number(5), False),
                Guard(RelOp.EQUAL, Number(3), True),
            ),
        )  # only right guard
        assert Program.from_string(r"a :- 5 < #count{} = 3.").statements[0].body[
            0
        ] == AggrLiteral(
            AggrCount(),
            tuple(),
            (
                Guard(RelOp.LESS, Number(5), False),
                Guard(RelOp.EQUAL, Number(3), True),
            ),
        )  # no elements
        assert Program.from_string(r"a :- 5 < #count{X:} = 3.").statements[0].body[
            0
        ] == AggrLiteral(
            AggrCount(),
            (AggrElement(TermTuple(Variable("X")), LiteralCollection()),),
            (
                Guard(RelOp.LESS, Number(5), False),
                Guard(RelOp.EQUAL, Number(3), True),
            ),
        )  # element without literals (i.e., condition)
        assert Program.from_string(r"a :- 5 < #count{:p(X)} = 3.").statements[0].body[
            0
        ] == AggrLiteral(
            AggrCount(),
            (
                AggrElement(
                    TermTuple(), LiteralCollection(PredLiteral("p", Variable("X")))
                ),
            ),
            (
                Guard(RelOp.LESS, Number(5), False),
                Guard(RelOp.EQUAL, Number(3), True),
            ),
        )  # element without terms
        assert Program.from_string(r"a :- 5 < #count{:} = 3.").statements[0].body[
            0
        ] == AggrLiteral(
            AggrCount(),
            tuple(),
            (
                Guard(RelOp.LESS, Number(5), False),
                Guard(RelOp.EQUAL, Number(3), True),
            ),
        )  # element without terms or literals
        assert Program.from_string(
            r"a :- 5 < #count{X: p(X); X: q(X)} = 3."
        ).statements[0].body[0] == AggrLiteral(
            AggrCount(),
            (
                AggrElement(
                    TermTuple(Variable("X")),
                    LiteralCollection(PredLiteral("p", Variable("X"))),
                ),
                AggrElement(
                    TermTuple(Variable("X")),
                    LiteralCollection(PredLiteral("q", Variable("X"))),
                ),
            ),
            (
                Guard(RelOp.LESS, Number(5), False),
                Guard(RelOp.EQUAL, Number(3), True),
            ),
        )  # multiple elements
        assert Program.from_string(r"a :- 5 < #sum{} = 3.").statements[0].body[
            0
        ] == AggrLiteral(
            AggrSum(),
            tuple(),
            (
                Guard(RelOp.LESS, Number(5), False),
                Guard(RelOp.EQUAL, Number(3), True),
            ),
        )  # sum
        assert Program.from_string(r"a :- 5 < #min{} = 3.").statements[0].body[
            0
        ] == AggrLiteral(
            AggrMin(),
            tuple(),
            (
                Guard(RelOp.LESS, Number(5), False),
                Guard(RelOp.EQUAL, Number(3), True),
            ),
        )  # min
        assert Program.from_string(r"a :- 5 < #max{} = 3.").statements[0].body[
            0
        ] == AggrLiteral(
            AggrMax(),
            tuple(),
            (
                Guard(RelOp.LESS, Number(5), False),
                Guard(RelOp.EQUAL, Number(3), True),
            ),
        )  # max

        # ----- normal facts -----'
        assert Program.from_string("p.").statements[0], NormalRule(PredLiteral("p"))

        # ----- normal rules -----
        assert Program.from_string("p :- q.").statements[0] == NormalRule(
            PredLiteral("p"), [PredLiteral("q")]
        )

        # ----- disjunctive facts -----
        assert Program.from_string("p | u | v.").statements[0] == DisjunctiveRule(
            (PredLiteral("p"), PredLiteral("u"), PredLiteral("v"))
        )

        # ----- disjunctive rules -----
        assert Program.from_string("p | u | v :- q.").statements[0] == DisjunctiveRule(
            (PredLiteral("p"), PredLiteral("u"), PredLiteral("v")),
            (PredLiteral("q"),),
        )

        # ----- choice facts -----
        assert Program.from_string(r"3 < {u:p;v:q} > 5.").statements[0] == ChoiceRule(
            Choice(
                (
                    ChoiceElement(PredLiteral("u"), (PredLiteral("p"),)),
                    ChoiceElement(PredLiteral("v"), (PredLiteral("q"),)),
                ),
                (
                    Guard(RelOp.LESS, Number(3), False),
                    Guard(RelOp.GREATER, Number(5), True),
                ),
            )
        )

        # ----- choice rules -----
        assert Program.from_string(r"3 < {u:p;v:q} > 5 :- r, s.").statements[
            0
        ] == ChoiceRule(
            Choice(
                (
                    ChoiceElement(PredLiteral("u"), (PredLiteral("p"),)),
                    ChoiceElement(PredLiteral("v"), (PredLiteral("q"),)),
                ),
                (
                    Guard(RelOp.LESS, Number(3), False),
                    Guard(RelOp.GREATER, Number(5), True),
                ),
            ),
            (PredLiteral("r"), PredLiteral("s")),
        )

        # ----- constraint -----
        assert Program.from_string(":- p, q.").statements[0] == Constraint(
            PredLiteral("p"), PredLiteral("q")
        )

        # ----- NPP fact -----
        assert Program.from_string("#npp(h,[]).").statements[0] == NPPRule(
            NPP("h", TermTuple(), TermTuple())
        )
        assert Program.from_string("#npp(h(),[p,0]):-.").statements[0] == NPPRule(
            NPP("h", TermTuple(), TermTuple(SymbolicConstant("p"), Number(0)))
        )
        assert Program.from_string('#npp(h("f"),[p,0]).').statements[0] == NPPRule(
            NPP(
                "h",
                TermTuple(String("f")),
                TermTuple(SymbolicConstant("p"), Number(0)),
            )
        )

        # ----- NPP rule -----
        assert Program.from_string('#npp(h("f"),[p,0]) :- p, q.').statements[
            0
        ] == NPPRule(
            NPP(
                "h",
                TermTuple(String("f")),
                TermTuple(SymbolicConstant("p"), Number(0)),
            ),
            (PredLiteral("p"), PredLiteral("q")),
        )
