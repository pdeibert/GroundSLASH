# Generated from SLASH.g4 by ANTLR 4.11.1
from antlr4 import *

if __name__ is not None and "." in __name__:
    from .SLASHParser import SLASHParser
else:
    from SLASHParser import SLASHParser

# This class defines a complete generic visitor for a parse tree produced by SLASHParser.


class SLASHVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by SLASHParser#program.
    def visitProgram(self, ctx: SLASHParser.ProgramContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#statements.
    def visitStatements(self, ctx: SLASHParser.StatementsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#query.
    def visitQuery(self, ctx: SLASHParser.QueryContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#statement.
    def visitStatement(self, ctx: SLASHParser.StatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#head.
    def visitHead(self, ctx: SLASHParser.HeadContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#body.
    def visitBody(self, ctx: SLASHParser.BodyContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#disjunction.
    def visitDisjunction(self, ctx: SLASHParser.DisjunctionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#choice.
    def visitChoice(self, ctx: SLASHParser.ChoiceContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#choice_elements.
    def visitChoice_elements(self, ctx: SLASHParser.Choice_elementsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#choice_element.
    def visitChoice_element(self, ctx: SLASHParser.Choice_elementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#aggregate.
    def visitAggregate(self, ctx: SLASHParser.AggregateContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#aggregate_elements.
    def visitAggregate_elements(self, ctx: SLASHParser.Aggregate_elementsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#aggregate_element.
    def visitAggregate_element(self, ctx: SLASHParser.Aggregate_elementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#aggregate_function.
    def visitAggregate_function(self, ctx: SLASHParser.Aggregate_functionContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#naf_literals.
    def visitNaf_literals(self, ctx: SLASHParser.Naf_literalsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#naf_literal.
    def visitNaf_literal(self, ctx: SLASHParser.Naf_literalContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#classical_literal.
    def visitClassical_literal(self, ctx: SLASHParser.Classical_literalContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#builtin_atom.
    def visitBuiltin_atom(self, ctx: SLASHParser.Builtin_atomContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#relop.
    def visitRelop(self, ctx: SLASHParser.RelopContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#terms.
    def visitTerms(self, ctx: SLASHParser.TermsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#term.
    def visitTerm(self, ctx: SLASHParser.TermContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#func_term.
    def visitFunc_term(self, ctx: SLASHParser.Func_termContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#arith_term.
    def visitArith_term(self, ctx: SLASHParser.Arith_termContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#arith_sum.
    def visitArith_sum(self, ctx: SLASHParser.Arith_sumContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#arith_prod.
    def visitArith_prod(self, ctx: SLASHParser.Arith_prodContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by SLASHParser#arith_atom.
    def visitArith_atom(self, ctx: SLASHParser.Arith_atomContext):
        return self.visitChildren(ctx)


del SLASHParser
