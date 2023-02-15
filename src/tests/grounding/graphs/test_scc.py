import unittest
from aspy.grounding.graphs import compute_SCCs


class TestSCC(unittest.TestCase):
    def test_compute_SCCs(self):

        nodes = {'A', 'B', 'C', 'D', 'E'}
        edges = {
            ('A', 'B'),
            ('B', 'C'),
            ('C', 'B'),
            ('D', 'C')
        }
        target_SCCs = [{'A'}, {'B','C'}, {'D'}, {'E'}]
        graph_SCCs = compute_SCCs(nodes, edges)

        self.assertEqual(len(target_SCCs), len(graph_SCCs)) # no extra SCCs

        for scc in target_SCCs:
            self.assertTrue(scc in graph_SCCs)


if __name__ == "__main__":
    unittest.main()