import unittest

import ground_slash
from ground_slash.program.safety_characterization import SafetyRule, SafetyTriplet
from ground_slash.program.terms import Variable


class TestSafetyCharacterization(unittest.TestCase):
    def test_safety_rule(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        rule = SafetyRule(Variable("X"), {Variable("Y")})

        # equality
        self.assertEqual(rule, SafetyRule(Variable("X"), {Variable("Y")}))
        # hashing
        self.assertEqual(hash(rule), hash(SafetyRule(Variable("X"), {Variable("Y")})))

    def test_safety_triple(self):
        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        # TODO


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
