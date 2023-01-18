# Generated from ASP.g4 by ANTLR 4.11.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .ASPParser import ASPParser
else:
    from ASPParser import ASPParser

# This class defines a complete generic visitor for a parse tree produced by ASPParser.

class ASPVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ASPParser#program.
    def visitProgram(self, ctx:ASPParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#statements.
    def visitStatements(self, ctx:ASPParser.StatementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#query.
    def visitQuery(self, ctx:ASPParser.QueryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#statement.
    def visitStatement(self, ctx:ASPParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#head.
    def visitHead(self, ctx:ASPParser.HeadContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#body.
    def visitBody(self, ctx:ASPParser.BodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#disjunction.
    def visitDisjunction(self, ctx:ASPParser.DisjunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#choice.
    def visitChoice(self, ctx:ASPParser.ChoiceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#choice_elements.
    def visitChoice_elements(self, ctx:ASPParser.Choice_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#choice_element.
    def visitChoice_element(self, ctx:ASPParser.Choice_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#aggregate.
    def visitAggregate(self, ctx:ASPParser.AggregateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#aggregate_elements.
    def visitAggregate_elements(self, ctx:ASPParser.Aggregate_elementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#aggregate_element.
    def visitAggregate_element(self, ctx:ASPParser.Aggregate_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#aggregate_function.
    def visitAggregate_function(self, ctx:ASPParser.Aggregate_functionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#weight_at_level.
    def visitWeight_at_level(self, ctx:ASPParser.Weight_at_levelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#naf_literals.
    def visitNaf_literals(self, ctx:ASPParser.Naf_literalsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#naf_literal.
    def visitNaf_literal(self, ctx:ASPParser.Naf_literalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#classical_literal.
    def visitClassical_literal(self, ctx:ASPParser.Classical_literalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#builtin_atom.
    def visitBuiltin_atom(self, ctx:ASPParser.Builtin_atomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#binop.
    def visitBinop(self, ctx:ASPParser.BinopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#terms.
    def visitTerms(self, ctx:ASPParser.TermsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#term.
    def visitTerm(self, ctx:ASPParser.TermContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#basic_terms.
    def visitBasic_terms(self, ctx:ASPParser.Basic_termsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#basic_term.
    def visitBasic_term(self, ctx:ASPParser.Basic_termContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#ground_term.
    def visitGround_term(self, ctx:ASPParser.Ground_termContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#variable_term.
    def visitVariable_term(self, ctx:ASPParser.Variable_termContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASPParser#arithop.
    def visitArithop(self, ctx:ASPParser.ArithopContext):
        return self.visitChildren(ctx)



del ASPParser