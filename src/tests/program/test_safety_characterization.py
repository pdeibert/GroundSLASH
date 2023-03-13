import unittest

import aspy
from aspy.program.safety_characterization import SafetyRule, SafetyTriplet
from aspy.program.terms import Variable


class TestSafetyCharacterization(unittest.TestCase):
    def test_safety_rule(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        rule = SafetyRule(Variable("X"), {Variable("Y")})

        # equality
        self.assertEqual(rule, SafetyRule(Variable("X"), {Variable("Y")}))
        # hashing
        self.assertEqual(hash(rule), hash(SafetyRule(Variable("X"), {Variable("Y")})))

    def test_safety_triple(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        # TODO


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
