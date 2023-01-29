import unittest

from antlr4 import * # type: ignore
from aspy.antlr.ASPCoreLexer import ASPCoreLexer
from aspy.antlr.ASPCoreParser import ASPCoreParser
from aspy.program.ProgramBuilder import ProgramBuilder


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


class TestSafety(unittest.TestCase):
    def test_safety(self):

        input = r"""
        % safe facts
        head(const).
        head1(const) | head2(const).
        % TODO: choice

        % unsafe fact
        head(X).
        head1(const) | head2(X).
        % TODO: choice

        % safe rules w/o aggregates
        head(const) :- body(const).
        head(const) :- not body(const).
        head(const) :- body(X).
        head(const) :- body1(X), not body2(X).
        head(X) :- body(X).
        head(X) :- body1(X), not body2(X).
        head(const) :- body1(X), X = 3.
        % TODO: choice
        % TODO: aggregates

        % unsafe rules w/o aggregates
        head(const) :- not body(X).
        head(const) :- body1(const), not body2(X).
        head(X) :- body(const).
        head(X) :- body1(const), not body2(X).
        head(const) :- X = 3.
        head(X) :- X = 3.
        % TODO: choice
        % TODO: aggregates

        % safe constraints w/o aggregates
        :- head(const).
        :- head(X).
        :- head(X), not head(X).
        % TODO: aggregates

        % unsafe constraints w/o aggregates
        :- not head(X).
        :- X = 3.
        % TODO: aggregates

        % safe weak constraints w/o aggregates
        % TODO

        % unsafe weak constraints w/o aggregates
        % TODO

        % safe optimize statements
        % TODO

        % unsafe optimize statements
        % TODO
        """
        prog = parse(input)
        statement_iter = iter(prog.statements)

        """ safe facts """
        # head(const).
        self.assertTrue(next(statement_iter).is_safe)
        # head1(const) | head2(const).
        self.assertTrue(next(statement_iter).is_safe)

        """ unsafe facts """
        # head(X).
        self.assertFalse(next(statement_iter).is_safe)
        # head1(const) | head2(X).
        self.assertFalse(next(statement_iter).is_safe)

        """ safe rules w/o aggregates """
        # head(const) :- body(const).
        self.assertTrue(next(statement_iter).is_safe)
        # head(const) :- not body(const).
        self.assertTrue(next(statement_iter).is_safe)
        # head(const) :- body(X).
        self.assertTrue(next(statement_iter).is_safe)
        # head(const) :- body1(X), not body2(X).
        self.assertTrue(next(statement_iter).is_safe)
        # head(X) :- body(X).
        self.assertTrue(next(statement_iter).is_safe)
        # head(X) :- body1(X), not body2(X).
        self.assertTrue(next(statement_iter).is_safe)
        # head(const) :- body1(X), X = 3.
        self.assertTrue(next(statement_iter).is_safe)

        """ unsafe rules w/o aggregates """
        # head(const) :- not body(X).
        self.assertFalse(next(statement_iter).is_safe)
        # head(const) :- body1(const), not body2(X).
        self.assertFalse(next(statement_iter).is_safe)
        # head(X) :- body(const).
        self.assertFalse(next(statement_iter).is_safe)
        # head(X) :- body1(const), not body2(X).
        self.assertFalse(next(statement_iter).is_safe)
        # head(const) :- X = 3.
        self.assertFalse(next(statement_iter).is_safe)
        # head(X) :- X = 3.
        self.assertFalse(next(statement_iter).is_safe)

        """ safe constraints w/o aggregates """
        # :- head(const).
        self.assertTrue(next(statement_iter).is_safe)
        # :- head(X).
        self.assertTrue(next(statement_iter).is_safe)
        # :- head(X), not head(X).
        self.assertTrue(next(statement_iter).is_safe)

        """ unsafe constraints w/o aggregates """
        # :- not head(X).
        self.assertFalse(next(statement_iter).is_safe)
        # :- X = 3.
        self.assertFalse(next(statement_iter).is_safe)


if __name__ == "__main__":
    unittest.main()