try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

import ground_slash
from ground_slash.program.safety_characterization import SafetyRule
from ground_slash.program.terms import Variable


class TestSafetyCharacterization:
    def test_safety_rule(self: Self):
        # make sure debug mode is enabled
        assert ground_slash.debug()

        rule = SafetyRule(Variable("X"), {Variable("Y")})

        # equality
        assert rule == SafetyRule(Variable("X"), {Variable("Y")})
        # hashing
        assert hash(rule) == hash(SafetyRule(Variable("X"), {Variable("Y")}))

    def test_safety_triple(self: Self):
        # make sure debug mode is enabled
        assert ground_slash.debug()

        # TODO
