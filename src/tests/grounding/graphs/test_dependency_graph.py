import unittest

import aspy
from aspy.grounding.graphs import DependencyGraph
from aspy.program import Program


class TestDependencyGraph(unittest.TestCase):
    def test_dependency_graph(self):

        # make sure debug mode is enabled
        self.assertTrue(aspy.debug())

        # example from Example 17 in Kaminski, Schaub (2022):
        # "On the Foundations of Grounding in Answer Set Programming".
        input = r"""
        u(1).
        u(2).
        v(2).
        v(3).

        p(X) :- not q(X), u(X).
        q(X) :- not p(X), v(X).
        x :- not p(1).
        y :- not q(3).
        """

        prog = Program.from_string(input)

        self.assertEqual(
            len(prog.statements), 8
        )  # make sure we have no extra statements
        u1, u2, v2, v3, pX, qX, x, y = prog.statements

        # create dependency graph
        graph = DependencyGraph(prog.statements)

        # check nodes
        self.assertTrue(u1 in graph.nodes)
        self.assertTrue(u2 in graph.nodes)
        self.assertTrue(v2 in graph.nodes)
        self.assertTrue(v3 in graph.nodes)
        self.assertTrue(pX in graph.nodes)
        self.assertTrue(qX in graph.nodes)
        self.assertTrue(x in graph.nodes)
        self.assertTrue(y in graph.nodes)

        self.assertEqual(len(graph.nodes), 8)  # no extra nodes

        # check positive edges
        self.assertTrue((pX, u1) in graph.pos_edges)
        self.assertTrue((pX, u2) in graph.pos_edges)
        self.assertTrue((qX, v2) in graph.pos_edges)
        self.assertTrue((qX, v3) in graph.pos_edges)
        # check negative edges
        self.assertTrue((pX, qX) in graph.neg_edges)
        self.assertTrue((qX, pX) in graph.neg_edges)
        self.assertTrue((x, pX) in graph.neg_edges)
        self.assertTrue((y, qX) in graph.neg_edges)

        self.assertEqual(len(graph.edges), 8)  # no extra edges


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
