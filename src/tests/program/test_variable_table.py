import unittest

import aspy
from aspy.program import Program
from aspy.program.literals import Naf, PredicateLiteral
from aspy.program.statements import NormalRule
from aspy.program.terms import AnonVariable, ArithVariable, Variable


class TestVariableTable(unittest.TestCase):
    def test_variable_table_from_string(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        input = r"""p(X) :- not q(_), u(_), v(Y)."""  # , Z < #count{A}."""

        prog = Program.from_string(input)

        self.assertEqual(len(prog.statements), 1)  # make sure we have no extra statements

        statement = prog.statements[0]

        var_table = statement.var_table

        self.assertTrue(
            all(
                var in var_table and var_table[var] == is_global
                for (var, is_global) in [
                    (Variable("X"), True),
                    (Variable("Y"), True),
                    (AnonVariable(0), True),
                    (AnonVariable(1), True),
                ]
            )
        )
        self.assertTrue(
            var_table.vars() == var_table.global_vars() == {Variable("X"), Variable("Y"), AnonVariable(0), AnonVariable(1)}
        )
        self.assertEqual(var_table.arith_vars(), set())
        self.assertEqual(var_table.anon_counter, 2)

    def test_variable_table_manual(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        statement = NormalRule(
            PredicateLiteral("p", Variable("X")),
            Naf(PredicateLiteral("q", AnonVariable(0))),
            PredicateLiteral("u", AnonVariable(1)),
            PredicateLiteral("v", Variable("Y")),
            PredicateLiteral("q", ArithVariable(0, Variable("Z"))),
        )

        var_table = statement.var_table

        self.assertTrue(
            all(
                var in var_table and var_table[var] == is_global
                for (var, is_global) in [
                    (Variable("X"), True),
                    (Variable("Y"), True),
                    (AnonVariable(0), True),
                    (AnonVariable(1), True),
                    (ArithVariable(0, Variable("Z")), True),
                ]
            )
        )
        self.assertTrue(
            var_table.vars()
            == var_table.global_vars()
            == {Variable("X"), Variable("Y"), AnonVariable(0), AnonVariable(1), ArithVariable(0, Variable("Z"))}
        )
        self.assertEqual(var_table.arith_vars(), {ArithVariable(0, Variable("Z"))})
        self.assertEqual(var_table.anon_counter, 2)
        self.assertEqual(var_table.arith_counter, 1)

        # TODO: local variables!


if __name__ == "__main__":
    unittest.main()
