import unittest

import ground_slash
from ground_slash.program.literals import Naf, PredLiteral
from ground_slash.program.statements import NormalRule
from ground_slash.program.symbols import SpecialChar
from ground_slash.program.terms import AnonVariable, ArithVariable, Minus, Variable
from ground_slash.program.variable_table import VariableTable


class TestVariableTable(unittest.TestCase):
    def test_variable_table(self):

        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        statement = NormalRule(
            PredLiteral("p", Variable("X")),
            [
                Naf(PredLiteral("q", AnonVariable(0))),
                PredLiteral("u", AnonVariable(1)),
                PredLiteral("v", Variable("Y")),
                PredLiteral("q", ArithVariable(0, Variable("Z"))),
            ],
        )

        var_table = statement.var_table
        # variables
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
            == {
                Variable("X"),
                Variable("Y"),
                AnonVariable(0),
                AnonVariable(1),
                ArithVariable(0, Variable("Z")),
            }
        )
        self.assertEqual(var_table.arith_vars(), {ArithVariable(0, Variable("Z"))})
        # counters
        self.assertEqual(var_table.anon_counter, 2)
        self.assertEqual(var_table.arith_counter, 1)

        # set global
        var_table[Variable("X")] = False
        # string representation
        table_str = str(var_table)
        self.assertTrue(table_str.startswith("{"))
        self.assertTrue(table_str.endswith("}"))
        self.assertEqual(
            set(table_str[1:-1].split(",")),
            {"X", "Y*", "_0*", "_1*", f"{SpecialChar.TAU.value}0*"},
        )
        # contains
        self.assertTrue(Variable("X") in var_table)
        self.assertFalse(Variable("Z") in var_table)
        # add
        var_table = VariableTable()  # init new empty table
        var_table.register(Variable("X"))
        var_table.register(Variable("Y"), True)
        var_table.register(AnonVariable(0))
        self.assertFalse(var_table[Variable("X")])
        self.assertTrue(var_table[Variable("Y")])
        self.assertFalse(var_table[AnonVariable(0)])
        # update
        var_table.update({Variable("Z")})
        self.assertFalse(var_table[Variable("Z")])
        var_table.update({Variable("U"): True})
        self.assertTrue(var_table[Variable("U")])
        # create
        self.assertEqual(var_table.create("X", register=False), Variable("X"))
        self.assertEqual(var_table.create("_", register=False), AnonVariable(1))
        self.assertRaises(ValueError, var_table.create, SpecialChar.TAU.value)
        self.assertEqual(
            var_table.create(
                SpecialChar.TAU.value,
                orig_term=Minus(Variable("A")),
                register=True,
            ),
            ArithVariable(0, Minus(Variable("A"))),
        )
        self.assertTrue(ArithVariable(0, Minus(Variable("A"))) in var_table)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
