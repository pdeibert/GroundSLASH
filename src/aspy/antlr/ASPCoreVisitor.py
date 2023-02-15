# Generated from ASPCore.g4 by ANTLR 4.11.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .ASPCoreParser import ASPCoreParser
else:
    from ASPCoreParser import ASPCoreParser

# This class defines a complete generic visitor for a parse tree produced by ASPCoreParser.

class ASPCoreVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ASPCoreParser#program.
    def visitProgram(self, ctx:ASPCoreParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#statements.
    def visitStatements(self, ctx:ASPCoreParser.StatementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#query.
    def visitQuery(self, ctx:ASPCoreParser.QueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#statement.
    def visitStatement(self, ctx:ASPCoreParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#head.
    def visitHead(self, ctx:ASPCoreParser.HeadContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#body.
    def visitBody(self, ctx:ASPCoreParser.BodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#disjunction.
    def visitDisjunction(self, ctx:ASPCoreParser.DisjunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#choice.
    def visitChoice(self, ctx:ASPCoreParser.ChoiceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#choice_elements.
    def visitChoice_elements(self, ctx:ASPCoreParser.Choice_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#choice_element.
    def visitChoice_element(self, ctx:ASPCoreParser.Choice_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#aggregate.
    def visitAggregate(self, ctx:ASPCoreParser.AggregateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#aggregate_elements.
    def visitAggregate_elements(self, ctx:ASPCoreParser.Aggregate_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#aggregate_element.
    def visitAggregate_element(self, ctx:ASPCoreParser.Aggregate_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#aggregate_function.
    def visitAggregate_function(self, ctx:ASPCoreParser.Aggregate_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#optimize.
    def visitOptimize(self, ctx:ASPCoreParser.OptimizeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#optimize_elements.
    def visitOptimize_elements(self, ctx:ASPCoreParser.Optimize_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#optimize_element.
    def visitOptimize_element(self, ctx:ASPCoreParser.Optimize_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#optimize_function.
    def visitOptimize_function(self, ctx:ASPCoreParser.Optimize_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#weight_at_level.
    def visitWeight_at_level(self, ctx:ASPCoreParser.Weight_at_levelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#naf_literals.
    def visitNaf_literals(self, ctx:ASPCoreParser.Naf_literalsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#naf_literal.
    def visitNaf_literal(self, ctx:ASPCoreParser.Naf_literalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#classical_literal.
    def visitClassical_literal(self, ctx:ASPCoreParser.Classical_literalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#builtin_atom.
    def visitBuiltin_atom(self, ctx:ASPCoreParser.Builtin_atomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#relop.
    def visitRelop(self, ctx:ASPCoreParser.RelopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#terms.
    def visitTerms(self, ctx:ASPCoreParser.TermsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#term.
    def visitTerm(self, ctx:ASPCoreParser.TermContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#func_term.
    def visitFunc_term(self, ctx:ASPCoreParser.Func_termContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#arith_term.
    def visitArith_term(self, ctx:ASPCoreParser.Arith_termContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#arith_sum.
    def visitArith_sum(self, ctx:ASPCoreParser.Arith_sumContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#arith_prod.
    def visitArith_prod(self, ctx:ASPCoreParser.Arith_prodContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPCoreParser#arith_atom.
    def visitArith_atom(self, ctx:ASPCoreParser.Arith_atomContext):
        return self.visitChildren(ctx)



del ASPCoreParser