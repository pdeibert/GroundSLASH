import unittest

import aspy
from aspy.program.substitution import Substitution
from aspy.program.variable_table import VariableTable
from aspy.program.symbol_table import SpecialChar
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.literals import Naf, AlphaLiteral, EpsLiteral, EtaLiteral
from aspy.program.terms import Variable, Number, String, TermTuple


class TestSpecial(unittest.TestCase):
    def test_alpha_literal(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        vars = TermTuple(Variable('X'), Variable('Y'))
        literal = AlphaLiteral(1, vars, TermTuple(Number(1), Variable('Y')))
        naf_literal = Naf(AlphaLiteral(1, vars, TermTuple(Number(1), Variable('Y'))))

        # check initialization
        self.assertTrue(literal.aggr_id == naf_literal.aggr_id == 1)
        self.assertTrue(literal.global_vars == naf_literal.global_vars == vars)
        self.assertTrue(literal.terms == naf_literal.terms == TermTuple(Number(1), Variable('Y')))
        # string representation
        self.assertEqual(str(literal), f'{SpecialChar.ALPHA}{1}(1,Y)')
        self.assertEqual(str(naf_literal), f'not {SpecialChar.ALPHA}{1}(1,Y)')
        # equality
        self.assertEqual(literal, AlphaLiteral(1, vars, TermTuple(Number(1), Variable('Y'))))
        # hashing
        self.assertEqual(hash(literal), hash(AlphaLiteral(1, vars, TermTuple(Number(1), Variable('Y')))))
        # arity
        self.assertEqual(literal.arity, 2)
        # predicate tuple
        self.assertEqual(literal.pred(), (f'{SpecialChar.ALPHA}{1}', 2))
        # ground
        self.assertTrue(literal.ground == naf_literal.ground == False)
        # TODO: variables
        # replace arithmetic terms
        self.assertEqual(literal.replace_arith(VariableTable()), literal)
        # positive/negative literal occurrences
        self.assertEqual(literal.pos_occ(), {AlphaLiteral(1, vars, TermTuple(Number(1), Variable('Y')))})
        self.assertEqual(literal.neg_occ(), set())
        self.assertEqual(naf_literal.pos_occ(), set())
        self.assertEqual(naf_literal.neg_occ(), {AlphaLiteral(1, vars, TermTuple(Number(1), Variable('Y')))})
        # safety characterization
        self.assertEqual(literal.safety(), SafetyTriplet({Variable('Y')}))

        # classical negation and negation-as-failure
        self.assertTrue(literal.naf == (not naf_literal.naf) == literal.neg == False)
        self.assertRaises(Exception, literal.set_neg)
        literal.set_naf(True)
        self.assertTrue(literal.naf == True)

        # substitute
        self.assertEqual(AlphaLiteral(1, vars, TermTuple(Number(1), Variable('Y'))).substitute(Substitution({Variable('Y'): Number(0), Number(1): String('f')})), AlphaLiteral(1, vars, TermTuple(Number(1), Number(0)))) # NOTE: substitution is invalid
        # match
        self.assertEqual(AlphaLiteral(1, vars, TermTuple(Variable('X'), Variable('Y'))).match(AlphaLiteral(1, vars, TermTuple(Number(1), Variable('Y')))), Substitution({Variable('X'): Number(1)}))
        self.assertEqual(Naf(AlphaLiteral(1, vars, TermTuple(Variable('X'), String('f')))).match(Naf(AlphaLiteral(1, vars, TermTuple(Number(1), String('g'))))), None) # ground terms don't match

        # gather variable assignment
        self.assertEqual(AlphaLiteral(1, vars, TermTuple(Number(1), Variable('Y'))).gather_var_assignment(), Substitution({Variable('X'): Number(1)}))

    def test_eps_literal(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        vars = TermTuple(Variable('X'), Variable('Y'))
        literal = EpsLiteral(1, vars, TermTuple(Number(1), Variable('Y')))

        # check initialization
        self.assertTrue(literal.aggr_id == 1)
        self.assertEqual(literal.global_vars, vars)
        self.assertEqual(literal.terms, TermTuple(Number(1), Variable('Y')))
        # string representation
        self.assertEqual(str(literal), f'{SpecialChar.EPS}{1}(1,Y)')
        # equality
        self.assertEqual(literal, EpsLiteral(1, vars, TermTuple(Number(1), Variable('Y'))))
        # hashing
        self.assertEqual(hash(literal), hash(EpsLiteral(1, vars, TermTuple(Number(1), Variable('Y')))))
        # arity
        self.assertEqual(literal.arity, 2)
        # predicate tuple
        self.assertEqual(literal.pred(), (f'{SpecialChar.EPS}{1}', 2))
        # ground
        self.assertFalse(literal.ground, False)
        # TODO: variables
        # replace arithmetic terms
        self.assertEqual(literal.replace_arith(VariableTable()), literal)
        # positive/negative literal occurrences
        self.assertEqual(literal.pos_occ(), {EpsLiteral(1, vars, TermTuple(Number(1), Variable('Y')))})
        self.assertEqual(literal.neg_occ(), set())
        # safety characterization
        self.assertEqual(literal.safety(), SafetyTriplet({Variable('Y')}))

        # classical negation and negation-as-failure
        self.assertTrue(literal.naf == literal.neg == False)
        self.assertRaises(Exception, literal.set_neg)
        self.assertRaises(Exception, literal.set_naf)

        # substitute
        self.assertEqual(EpsLiteral(1, vars, TermTuple(Number(1), Variable('Y'))).substitute(Substitution({Variable('X'): Number(1), Number(0): String('f')})), EpsLiteral(1, vars, TermTuple(Number(1), Variable('Y')))) # NOTE: substitution is invalid
        # match
        self.assertEqual(EpsLiteral(1, vars, TermTuple(Variable('X'), Variable('Y'))).match(EpsLiteral(1, vars, TermTuple(Number(1), Variable('Y')))), Substitution({Variable('X'): Number(1)}))
        self.assertEqual(EpsLiteral(1, vars, TermTuple(Variable('X'), String('f'))).match(EpsLiteral(1, vars, TermTuple(Number(1), String('g')))), None) # ground terms don't match

        # gather variable assignment
        self.assertEqual(EpsLiteral(1, vars, TermTuple(Number(1), Variable('Y'))).gather_var_assignment(), Substitution({Variable('X'): Number(1)}))

    def test_eta_literal(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        global_vars = TermTuple(Variable('L'))
        local_vars = TermTuple(Variable('X'), Variable('Y'))
        literal = EtaLiteral(1, 3, local_vars, global_vars, TermTuple(Variable('L'), Number(1), Variable('Y')))

        # check initialization
        self.assertTrue(literal.aggr_id == 1)
        self.assertTrue(literal.element_id == 3)
        self.assertEqual(literal.local_vars, local_vars)
        self.assertEqual(literal.global_vars, global_vars)
        self.assertEqual(literal.terms, TermTuple(Variable('L'), Number(1), Variable('Y')))
        # string representation
        self.assertEqual(str(literal), f'{SpecialChar.ETA}{1}_{3}(L,1,Y)')
        # equality
        self.assertEqual(literal, EtaLiteral(1, 3, local_vars, global_vars, TermTuple(Variable('L'), Number(1), Variable('Y'))))
        # hashing
        self.assertEqual(hash(literal), hash(EtaLiteral(1, 3, local_vars, global_vars, TermTuple(Variable('L'), Number(1), Variable('Y')))))
        # arity
        self.assertEqual(literal.arity, 3)
        # predicate tuple
        self.assertEqual(literal.pred(), (f'{SpecialChar.ETA}{1}_{3}', 3))
        # ground
        self.assertFalse(literal.ground, False)
        # TODO: variables
        # replace arithmetic terms
        self.assertEqual(literal.replace_arith(VariableTable()), literal)
        # positive/negative literal occurrences
        self.assertEqual(literal.pos_occ(), {EtaLiteral(1, 3, local_vars, global_vars, TermTuple(Variable('L'), Number(1), Variable('Y')))})
        self.assertEqual(literal.neg_occ(), set())
        # safety characterization
        self.assertEqual(literal.safety(), SafetyTriplet({Variable('L'), Variable('Y')}))

        # classical negation and negation-as-failure
        self.assertTrue(literal.naf == literal.neg == False)
        self.assertRaises(Exception, literal.set_neg)
        self.assertRaises(Exception, literal.set_naf)

        # substitute
        self.assertEqual(EtaLiteral(1, 3, local_vars, global_vars, TermTuple(Variable('L'), Variable('X'), Variable('Y'))).substitute(Substitution({Variable('X'): Number(1), Number(0): String('f')})), EtaLiteral(1, 3, local_vars, global_vars, TermTuple(Variable('L'), Number(1), Variable('Y')))) # NOTE: substitution is invalid
        # match
        self.assertEqual(EtaLiteral(1, 3, local_vars, global_vars, TermTuple(Variable('L'), Variable('X'), Variable('Y'))).match(EtaLiteral(1, 3, local_vars, global_vars, TermTuple(Number(1), Variable('X'), String('f')))), Substitution({Variable('L'): Number(1), Variable('Y'): String('f')}))
        self.assertEqual(EtaLiteral(1, 3, local_vars, global_vars, TermTuple(Variable('L'), Variable('X'), String('f'))).match(EtaLiteral(1, 3, local_vars, global_vars, TermTuple(Number(1), Number(0), String('g')))), None) # ground terms don't match


if __name__ == "__main__":
    unittest.main()