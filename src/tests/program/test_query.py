import unittest

import aspy
from aspy.program.literals import LiteralTuple, PredicateLiteral
from aspy.program.query import Query
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.substitution import Substitution
from aspy.program.terms import Number, String, Variable


class TestQuery(unittest.TestCase):
    def test_query(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        ground_query = Query(PredicateLiteral("p", Number(0)))
        var_query = Query(PredicateLiteral("p", Variable("X")))

        # string representation
        self.assertEqual(str(ground_query), "p(0) ?")
        # equality
        self.assertEqual(ground_query, Query(PredicateLiteral("p", Number(0))))
        # head
        self.assertEqual(
            ground_query.head, LiteralTuple(PredicateLiteral("p", Number(0)))
        )
        # body
        self.assertEqual(ground_query.body, LiteralTuple())
        # hashing
        self.assertEqual(
            hash(ground_query), hash(Query(PredicateLiteral("p", Number(0))))
        )
        # ground
        self.assertTrue(ground_query.ground)
        self.assertFalse(var_query.ground)
        # variables
        self.assertTrue(ground_query.vars() == ground_query.global_vars() == set())
        self.assertTrue(var_query.vars() == var_query.global_vars() == {Variable("X")})
        # safety characterization
        self.assertEqual(ground_query.safety(), SafetyTriplet())
        self.assertEqual(var_query.safety(), SafetyTriplet(safe={Variable("X")}))

        # substitute
        self.assertEqual(
            var_query.substitute(
                Substitution({Variable("X"): Number(1), Number(0): String("f")})
            ),
            Query(PredicateLiteral("p", Number(1))),
        )  # NOTE: substitution is invalid


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
