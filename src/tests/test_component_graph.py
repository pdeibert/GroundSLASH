import unittest

from antlr4 import * # type: ignore
from aspy.antlr.ASPCoreLexer import ASPCoreLexer
from aspy.antlr.ASPCoreParser import ASPCoreParser
from aspy.program.ProgramBuilder import ProgramBuilder
from aspy.grounder.component_graph import ComponentGraph


def parse(input: str):

    input_stream = InputStream(input) # type: ignore

    # tokenize input program
    lexer = ASPCoreLexer(input_stream)
    stream = CommonTokenStream(lexer) # type: ignore
    stream.fill()

    parser = ASPCoreParser(stream)
    tree = parser.program()

    # traverse parse tree using visitor
    visitor = ProgramBuilder()
    prog = visitor.visitProgram(tree)

    return prog


class TestComponentGraph(unittest.TestCase):
    def test_component_graph(self):

        # example from Faber et.al. (2012): "The Intelligent Grounder of DLV"
        input = r"""
        a(g(1)).
        t(X,f(Y)) :- p(X,Y), a(Y).
        p(X,Y) :- r(X), t(X,Y).
        p(g(X),Y) | s(Y) :- r(X), r(Y).
        r(X) :- a(g(X)), not t(X,f(X)).
        """
        prog = parse(input)

        # create dependency graph
        graph = ComponentGraph(prog)

        print("Nodes:")
        for node in graph.nodes:
            print("\t", node)
        print("Positive edges:")
        for edge in graph.pos_edges:
            print("\t", edge[0], "->", edge[1])
        print("Negative edges:")
        for edge in graph.neg_edges:
            print("\t", edge[0], "->", edge[1])


if __name__ == "__main__":
    unittest.main()