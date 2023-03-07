import unittest

import aspy
from aspy.grounding.graphs import topological_sort


class TestSCC(unittest.TestCase):
    def test_topological_sort_acyclic(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        nodes = {"A", "B", "C", "D", "E"}
        edges = {("A", "C"), ("B", "C"), ("B", "E"), ("C", "D")}

        sequence = topological_sort(nodes, edges)
        valid_sequences = [
            ["A", "B", "C", "D", "E"],
            ["A", "B", "E", "C", "D"],
            ["B", "E", "A", "C", "D"],
        ]

        self.assertTrue(sequence in valid_sequences)

    def test_topological_sort_cyclic(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        nodes = {"A", "B", "C", "D", "E"}
        edges = {("A", "C"), ("B", "C"), ("C", "D"), ("C", "E"), ("E", "B")}

        self.assertRaises(ValueError, topological_sort, nodes, edges)


if __name__ == "__main__":
    unittest.main()
