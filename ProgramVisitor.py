# Generated from ASP.g4 by ANTLR 4.11.1
import antlr4

from ASPParser import ASPParser
from ASPVisitor import ASPVisitor
from AST import *


class ProgramVisitor(ASPVisitor):

    def __init__(self, verbose: bool=False):
        super().__init__()
        self.verbose = verbose


    def logging(self, msg: str):
        if self.verbose:
            print(msg)


    # Visit a parse tree produced by ASPParser#program.
    def visitProgram(self, ctx:ASPParser.ProgramContext):
        """Visits 'program'.
        
        Handles the following rule(s):

            program             :   statements? query? EOF
        """
        statements = tuple()
        query = None

        for child in ctx.children[:-1]:
            # statements
            if isinstance(child, ASPParser.StatementsContext):
                self.logging("statements")
                statements += self.visitStatements(child)
            # query
            elif isinstance(child, ASPParser.QueryContext):
                self.logging("query")
                query = self.visitQuery(child)

        return (statements, query)


    # Visit a parse tree produced by ASPParser#statements.
    def visitStatements(self, ctx:ASPParser.StatementsContext):
        """Visits 'statements'.

        Handles the following rule(s):

            statements          :   statement+
        """
        self.logging("statements+")
        return tuple([self.visitStatement(child) for child in ctx.children])


    # Visit a parse tree produced by ASPParser#query.
    def visitQuery(self, ctx:ASPParser.QueryContext):
        """Visits 'query'.
        
        Handles the following rule(s):

            query               :   classical_literal QUERY_MARK
        """
        self.logging("query")
        return self.visitClassical_literal(ctx.children[0])


    # Visit a parse tree produced by ASPParser#statement.
    def visitStatement(self, ctx:ASPParser.StatementContext):
        """Visits 'statement'.

        Handles the following rule(s):

            statement           :   CONS body? DOT
                                |   head (CONS body?)? DOT
                                |   WCONS body? DOT SQUARE_OPEN weight_at_level SQUARE_CLOSE
        """
        n_children = len(ctx.children)

        # first child is a token
        if isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNode):

            # get token
            token = ctx.children[0].getSymbol()
            token_type = ASPParser.symbolicNames[token.type]

            # CONS body? DOT (i.e., constraint)
            if(token_type == "CONS"):
                # body
                if n_children > 2:
                    return Constraint(self.visitBody(ctx.children[1]))
                else:
                    # TODO: empty constraint?
                    raise Exception("Empty constraints not supported yet.")
            # WCONS body? DOT SQUARE_OPEN weight_at_level SQUARE_CLOSE (i.e., weak constraint)
            else:
                # body
                if n_children > 5:
                    # TODO: weak constraint
                    raise Exception("Weak constraints not supported yet.")
                else:
                    # TODO: empty weak constraint?
                    raise Exception("Empty weak constraints not supported yet.")
        # head (CONS body?)? DOT
        else:
            head = self.visitHead(ctx.children[0])

            # head DOT | head CONS DOT (i.e., fact)
            if n_children < 4:
                return Fact(self.visitHead(ctx.children[0]))
            # head CONS body DOT (i.e., disjunctive rule)
            else:
                body = self.visitBody(ctx.children[2])

                # disjunctive rule
                if len(head) > 1:
                    return DisjunctiveRule(head, body)
                # normal rule
                else:
                    return NormalRule(head.literals[0], body)


    # Visit a parse tree produced by ASPParser#head.
    def visitHead(self, ctx:ASPParser.HeadContext):
        """Visits 'head'.

        Handles the following rule(s):

            head                :   disjunction
                                |   choice
        """
        # disjunction
        if isinstance(ctx.children[0], ASPParser.DisjunctionContext):
            return self.visitDisjunction(ctx.children[0])
        # choice
        else:
            return self.visitChoice(ctx.children[0])


    # Visit a parse tree produced by ASPParser#body.
    def visitBody(self, ctx:ASPParser.BodyContext):
        """Visits 'body'.

        Handles the following rule(s):

            body                :   (naf_literal | NAF? aggregate) (COMMA body)?
        """
        # naf_literal
        if isinstance(ctx.children[0], ASPParser.Naf_literalContext):
            literals = [self.visitNaf_literal(ctx.children[0])]
        # NAF? aggregate
        else:
            # NAF aggregate (true) or aggregate (false)
            neg = True if isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNode) else False
            literals = [AggrLiteral(self.visitAggregate(ctx.children[1]), neg=neg)]

        # COMMA body
        if len(ctx.children) > 2:
            literals + self.visitBody(ctx.children[-1])

        return Conjunction(literals)


    # Visit a parse tree produced by ASPParser#disjunction.
    def visitDisjunction(self, ctx:ASPParser.DisjunctionContext):
        """Visits 'disjunction'.

        Handles the following rule(s):

            disjunction         :   classical_literal (OR disjunction)?
        """
        # classical_literal
        literals = [self.visitClassical_literal(ctx.children[0])]

        # OR disjunction
        if len(ctx.children) > 1:
            # append disjunction literals recursively
            literals += self.visitDisjunction(ctx.children[2])

        return Disjunction(literals)


    # Visit a parse tree produced by ASPParser#choice.
    def visitChoice(self, ctx:ASPParser.ChoiceContext):
        # TODO
        raise Exception("Choices are not supported yet.")


    # Visit a parse tree produced by ASPParser#choice_elements.
    def visitChoice_elements(self, ctx:ASPParser.Choice_elementsContext):
        """Visits 'choice_elements'.

        Handles the following rule(s):

            choice_elements     :   choice_element (SEMICOLON choice_elements)?
        """
        # choice_element
        elements = tuple(self.visitChoice_element(ctx.children[0]))

        # SEMICOLON choice_elements
        if len(ctx.children) > 1:
            elements += self.visitChoice_elements(ctx.children[2])

        return elements


    # Visit a parse tree produced by ASPParser#choice_element.
    def visitChoice_element(self, ctx:ASPParser.Choice_elementContext):
        # TODO
        raise Exception("Choice elements not supported yet.")


    # Visit a parse tree produced by ASPParser#aggregate.
    def visitAggregate(self, ctx:ASPParser.AggregateContext):
        # TODO
        raise Exception("Aggregates not supported yet.")


    # Visit a parse tree produced by ASPParser#aggregate_elements.
    def visitAggregate_elements(self, ctx:ASPParser.Aggregate_elementsContext):
        """Visits 'aggregate_elements'.

        Handles the following rule(s):

            aggregate_elements  :   aggregate_element (SEMICOLON aggregate_elements)?
        """
        # aggregate_element
        elements = tuple(self.visitAggregate_element(ctx.children[0]))

        # SEMICOLON aggregate_elements
        if len(ctx.children) > 1:
            elements += self.visitAggregate_elements(ctx.children[2])

        return elements


    # Visit a parse tree produced by ASPParser#aggregate_element.
    def visitAggregate_element(self, ctx:ASPParser.Aggregate_elementContext):
        # TODO
        raise Exception("Aggregate elements not supported yet.")


    # Visit a parse tree produced by ASPParser#aggregate_function.
    def visitAggregate_function(self, ctx:ASPParser.Aggregate_functionContext):
        """Visits 'aggregate_function'.

        Handles the following rule(s):

            aggregate_function  :   COUNT
                                |   MAX
                                |   MIN
                                |   SUM
        """
        # get token
        token = ctx.children[0].getSymbol()
        token_type = ASPParser.symbolicNames[token.type]

        return AggrOp[token_type]


    # Visit a parse tree produced by ASPParser#weight_at_level.
    def visitWeight_at_level(self, ctx:ASPParser.Weight_at_levelContext):
        # TODO
        raise Exception("Weights and leves not supported yet.")


    # Visit a parse tree produced by ASPParser#naf_literals.
    def visitNaf_literals(self, ctx:ASPParser.Naf_literalsContext):
        """Visits 'naf_literals'.

        Handles the following rule(s):

            naf_literals        :   naf_literal (COMMA naf_literals)?
        """
        # naf_literal
        literals = tuple(self.visitNaf_literal(ctx.children[0]))

        # COMMA naf_literals
        if len(ctx.children) > 1:
            literals += self.visitNaf_literals(ctx.children[2])

        return literals


    # Visit a parse tree produced by ASPParser#naf_literal.
    def visitNaf_literal(self, ctx:ASPParser.Naf_literalContext):
        """Visits 'naf_literal'.

        Handles the following rule(s):

            naf_literal         :   NAF? classical_literal | builtin_atom ;
        """

        # builtin_atom
        if isinstance(ctx.children[0], ASPParser.Builtin_atomContext):
            return self.visitBuiltin_atom(ctx.children[0])
        # NAF? classical_literal
        else:
            # classical_literal
            if len(ctx.children) == 1:
                return self.visitClassical_literal(ctx.children[0])
            # NAF classical
            else:
                return DefaultAtom(
                    self.visitClassical_literal(ctx.children[1])
                )


    # Visit a parse tree produced by ASPParser#classical_literal.
    def visitClassical_literal(self, ctx:ASPParser.Classical_literalContext):
        """Visits 'classical_literal'.

        Handles the following rule(s):

            classical_literal   :   MINUS? ID (PAREN_OPEN terms? PAREN_CLOSE)?
        """
        n_children = len(ctx.children)

        # get first token
        token = ctx.children[0].getSymbol()
        token_type = ASPParser.symbolicNames[token.type]

        # MINUS ID (true) or ID (false)
        minus = True if(token_type == "MINUS") else False

        # PAREN_OPEN terms PAREN_CLOSE
        if n_children - (minus+1) > 2:
            # parse terms
            terms = self.visitTerms(ctx.children[minus+2])
        else:
            terms = tuple()

        id = Id(ctx.children[minus], terms)

        if minus:
            return UnaryArithTerm(id)
        else:
            return id


    # Visit a parse tree produced by ASPParser#builtin_atom.
    def visitBuiltin_atom(self, ctx:ASPParser.Builtin_atomContext):
        """Visits 'builtin_atom'.

        Handles the following rule(s):

            builtin_atom        :   term binop term
        """
        return BuiltinAtom(
                self.visitBinop(ctx.children[1]), # parse binary relation operator
                self.visitTerm(ctx.children[0]), # parse left term
                self.visitTerm(ctx.children[2]), # parse right term
            )


    # Visit a parse tree produced by ASPParser#binop.
    def visitBinop(self, ctx:ASPParser.BinopContext):
        """Visits 'binop'.

        Handles the following rule(s):

            binop               :   EQUAL
                                |   UNEQUAL
                                |   LESS
                                |   GREATER
                                |   LESS_OR_EQ
                                |   GREATER_OR_EQ
        """
        # get token
        token = ctx.children[0].getSymbol()
        token_type = ASPParser.symbolicNames[token.type]

        return RelOp[token_type]


    # Visit a parse tree produced by ASPParser#terms.
    def visitTerms(self, ctx:ASPParser.TermsContext):
        """Visits 'terms'.

        Handles the following rule(s):

            terms               :   term (COMMA terms)?
        """
        # basic_term
        terms = tuple([self.visitTerm(ctx.children[0])])

        # COMMA terms
        if len(ctx.children) > 1:
            terms += self.visitTerms(ctx.children[2])

        return terms


    # Visit a parse tree produced by ASPParser#term.
    def visitTerm(self, ctx:ASPParser.TermContext):
        """Visits 'term'.
    
        Handles the following rule(s):

            term                :   ID (PAREN_OPEN terms? PAREN_CLOSE)?
                                |   NUMBER
                                |   STRING
                                |   VARIABLE
                                |   ANONYMOUS_VARIABLE
                                |   PAREN_OPEN term PAREN_CLOSE
                                |   MINUS term
                                |   term arithop term
        """
        # first child is a token
        if isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNode):

            # get token
            token = ctx.children[0].getSymbol()
            token_type = ASPParser.symbolicNames[token.type]

            # ID (PAREN_OPEN terms? PAREN_CLOSE)?
            if(token_type == "ID"):
                # PAREN_OPEN terms PAREN_CLOSE
                if len(ctx.children) > 3:
                    # parse terms
                    terms = self.visitTerms(ctx.children[2])
                # also handles PAREN_OPEN PAREN_CLOSE
                else:
                    # no terms
                    terms = tuple()
                return Id(token.text, terms)
            # NUMBER
            elif(token_type == "NUMBER"):
                return int(token.text)
            # STRING
            elif(token_type == "STRING"):
                return token.text
            # VARIABLE
            elif(token_type == "VARIABLE"):
                return Variable(token.text)
            # ANONYMOUS_VARIABLE
            elif(token_type == "ANONYMOUS_VARIABLE"):
                return AnonVariable()
            # PAREN_OPEN term PAREN_CLOSE
            elif(token_type == "PAREN_OPEN"):
                return self.visitTerm(ctx.children[1]) # parse term
            # MINUS term
            else:
                return UnaryArithTerm(
                    self.visitTerm(ctx.children[1]) # parse term
                )
        # term arithop term
        else:
            return BinaryArithTerm(
                self.visitArithop(ctx.children[1]), # parse binary arithmetical operator
                self.visitTerm(ctx.children[0]), # parse left term
                self.visitTerm(ctx.children[2]), # parse right term
            )


    # Visit a parse tree produced by ASPParser#basic_terms.
    def visitBasic_terms(self, ctx:ASPParser.Basic_termsContext):
        """Visits 'basic_terms'.

        Handles the following rule(s):

            basic_terms         :   basic_term (COMMA basic_terms)?
        """
        # basic_term
        terms = tuple([self.visitBasic_term(ctx.children[0])])

        # COMMA basic_terms
        if len(ctx.children) > 1:
            terms += self.visitBasic_terms(ctx.children[2])

        return terms


    # Visit a parse tree produced by ASPParser#basic_term.
    def visitBasic_term(self, ctx:ASPParser.Basic_termContext):
        # TODO
        raise Exception("Basic terms not supported yet.")


    # Visit a parse tree produced by ASPParser#ground_term.
    def visitGround_term(self, ctx:ASPParser.Ground_termContext):
        # TODO
        raise Exception("Ground terms not supported yet.")


    # Visit a parse tree produced by ASPParser#variable_term.
    def visitVariable_term(self, ctx:ASPParser.Variable_termContext):
        """Visits 'variable_term'.

        Handles the following rule(s):

            variable_term       :   VARIABLE
                                |   ANONYMOUS_VARIABLE
        """
        # get token
        token = ctx.children[0].getSymbol()
        token_type = ASPParser.symbolicNames[token.type]

        # VARIABLE
        if(token_type == "VARIABLE"):
            return Variable(token.text)
        # ANONYMOUS_VARIABLE
        else:
            return AnonVariable()


    # Visit a parse tree produced by ASPParser#arithop.
    def visitArithop(self, ctx:ASPParser.ArithopContext):
        """Visits 'arithop'.

        Handles the following rule(s):

            arithop             :   PLUS
                                |   MINUS
                                |   TIMES
                                |   DIV
        """
        # get token
        token = ctx.children[0].getSymbol()
        token_type = ASPParser.symbolicNames[token.type]

        return ArithOp[token_type]