import unittest

import ground_slash
from ground_slash.grounding.graphs import compute_SCCs


class TestSCC(unittest.TestCase):
    def test_compute_SCCs(self):

        # make sure debug mode is enabled
        self.assertTrue(ground_slash.debug())

        nodes = {"A", "B", "C", "D", "E"}
        edges = {("A", "B"), ("B", "C"), ("C", "B"), ("D", "C")}
        target_SCCs = [{"A"}, {"B", "C"}, {"D"}, {"E"}]
        graph_SCCs = compute_SCCs(nodes, edges)

        self.assertEqual(len(target_SCCs), len(graph_SCCs))  # no extra SCCs

        for scc in target_SCCs:
            self.assertTrue(scc in graph_SCCs)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
