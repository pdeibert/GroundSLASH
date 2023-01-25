# Generated from ASP.g4 by ANTLR 4.11.1
import antlr4  # type: ignore

from ASPCoreParser import ASPCoreParser
from ASPCoreVisitor import ASPCoreVisitor

from typing import Tuple, Union

from atom import *
from term import *
from statement import *
from aggregate import *
from comparison import *
from disjunction import Disjunction
from conjunction import Conjunction
from tables import VariableTable, ConstantTable
from program import Program


class ProgramBuilder(ASPCoreVisitor):
    """Builds ASP program from ANTLR4 parse tree."""
    def __init__(self) -> None:
        self.const_table = ConstantTable()
        self.var_table = None

    # Visit a parse tree produced by ASPCoreParser#program.
    def visitProgram(self, ctx:ASPCoreParser.ProgramContext) -> Program:
        """Visits 'program'.
        
        Handles the following rule(s):

            program             :   statements? query? EOF
        """
        statements = tuple()
        query = None

        for child in ctx.children[:-1]:
            # statements
            if isinstance(child, ASPCoreParser.StatementsContext):
                statements += self.visitStatements(child)
                self.var_table = None
            # query
            elif isinstance(child, ASPCoreParser.QueryContext):
                query = self.visitQuery(child)

        return Program(statements, query, self.const_table)

    # Visit a parse tree produced by ASPCoreParser#statements.
    def visitStatements(self, ctx:ASPCoreParser.StatementsContext):
        """Visits 'statements'.

        Handles the following rule(s):

            statements          :   statement+
        """
        return tuple([self.visitStatement(child) for child in ctx.children])


    # Visit a parse tree produced by ASPCoreParser#query.
    def visitQuery(self, ctx:ASPCoreParser.QueryContext):
        """Visits 'query'.
        
        Handles the following rule(s):

            query               :   classical_literal QUERY_MARK
        """
        return self.visitClassical_literal(ctx.children[0])


    # Visit a parse tree produced by ASPCoreParser#statement.
    def visitStatement(self, ctx:ASPCoreParser.StatementContext):
        """Visits 'statement'.

        Handles the following rule(s):

            statement           :   CONS body? DOT
                                |   head (CONS body?)? DOT
                                |   WCONS body? DOT SQUARE_OPEN weight_at_level SQUARE_CLOSE
                                |   optimize DOT
        """
        n_children = len(ctx.children)

        # first child is a token
        if isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNode):

            # get token
            token = ctx.children[0].getSymbol()
            token_type = ASPCoreParser.symbolicNames[token.type]

            # CONS body? DOT (i.e., constraint)
            if(token_type == "CONS"):
                # body
                if n_children > 2:
                    body, variables = self.visitBody(ctx.children[1])
                    statement = Constraint(Conjunction(body))
                else:
                    # TODO: empty constraint?
                    raise Exception("Empty constraints not supported yet.")
            # WCONS body? DOT SQUARE_OPEN weight_at_level SQUARE_CLOSE (i.e., weak constraint)
            else:
                # body
                if n_children > 5:
                    # TODO: implement weak constraint
                    raise Exception("Weak constraints not supported yet.")
                else:
                    # TODO: implement empty weak constraint?
                    raise Exception("Empty weak constraints not supported yet.")
        # head (CONS body?)? DOT
        elif isinstance(ctx.children[0], ASPCoreParser.HeadContext):
            head, variables = self.visitHead(ctx.children[0])

            # head DOT | head CONS DOT (i.e., fact)
            if n_children < 4:
                if len(head) > 1:
                    statement = DisjunctiveFact(head)
                else:
                    statement = NormalFact(head)
            # head CONS body DOT (i.e., disjunctive rule)
            else:
                body, body_variables = self.visitBody(ctx.children[2])
                body = Conjunction(body)

                # merge variables
                variables.merge(body_variables)

                # disjunctive rule
                if len(head) > 1:
                    statement = DisjunctiveRule(head, body)
                # normal rule
                else:
                    statement = NormalRule(head.literals[0], body)
        # optimize DOT
        else:
            statement, variables = self.visitOptimize(ctx.children[0])

        statement.set_variable_table(variables)

        return statement


    # Visit a parse tree produced by ASPCoreParser#head.
    def visitHead(self, ctx:ASPCoreParser.HeadContext): # TODO: return typing
        """Visits 'head'.

        Handles the following rule(s):

            head                :   disjunction
                                |   choice
        """
        # disjunction
        if isinstance(ctx.children[0], ASPCoreParser.DisjunctionContext):
            head, variables = self.visitDisjunction(ctx.children[0])
            head = Disjunction(head)
        # choice
        else:
            head, variables = self.visitChoice(ctx.children[0])

        # set all variables in head to unsafe
        variables.set_safe(False)

        return (head, variables)


    # Visit a parse tree produced by ASPCoreParser#body.
    def visitBody(self, ctx:ASPCoreParser.BodyContext) -> Tuple[Conjunction, VariableTable]:
        """Visits 'body'.

        Handles the following rule(s):

            body                :   (naf_literal | NAF? aggregate) (COMMA body)?
        """
        # naf_literal
        if isinstance(ctx.children[0], ASPCoreParser.Naf_literalContext):
            literal, variables = self.visitNaf_literal(ctx.children[0])
            literals = tuple([literal])
        # NAF? aggregate
        else:
            # NAF aggregate (true) or aggregate (false)
            neg = True if isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNode) else False
            literal, variables = self.visitAggregate(ctx.children[1])
            literals = tuple([AggregateLiteral(literal, neg=neg)])
        # COMMA body
        if len(ctx.children) > 2:
            additional_literals, additional_variables = self.visitBody(ctx.children[-1])

            # append literals
            literals += additional_literals
            # merge variables
            variables.merge(additional_variables)

        return (tuple(literals), variables)


    # Visit a parse tree produced by ASPCoreParser#disjunction.
    def visitDisjunction(self, ctx:ASPCoreParser.DisjunctionContext) -> Tuple[Disjunction, VariableTable]:
        """Visits 'disjunction'.

        Handles the following rule(s):

            disjunction         :   classical_literal (OR disjunction)?
        """
        # classical_literal
        literal, variables = self.visitClassical_literal(ctx.children[0])
        literals = tuple([literal])

        # OR disjunction
        if len(ctx.children) > 1:
            additional_literals, additional_variables = self.visitDisjunction(ctx.children[2])

            # append literals
            literals += additional_literals
            # merge variables
            variables.merge(additional_variables)

        return (literals, variables)


    # Visit a parse tree produced by ASPCoreParser#choice.
    def visitChoice(self, ctx:ASPCoreParser.ChoiceContext): # TODO: return typing
        """Visits 'choice'.

        Handles the following rule(s):

            choice              :   (term compop)? CURLY_OPEN choice_elements? CURLY_CLOSE (compop term)?
        """
        # TODO: implement
        raise Exception("Choices are not supported yet.")


    # Visit a parse tree produced by ASPCoreParser#choice_elements.
    def visitChoice_elements(self, ctx:ASPCoreParser.Choice_elementsContext): # TODO: return typing
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


    # Visit a parse tree produced by ASPCoreParser#choice_element.
    def visitChoice_element(self, ctx:ASPCoreParser.Choice_elementContext): # TODO: return typing
        """Visits 'choice_element'.

        Handles the following rule(s):

            choice_element      :   classical_literal (COLON naf_literals?)?
        """
        # TODO: implement
        raise Exception("Choice elements not supported yet.")


    # Visit a parse tree produced by ASPCoreParser#aggregate.
    def visitAggregate(self, ctx:ASPCoreParser.AggregateContext): # TODO: return typing
        """Visits 'aggregate'.

        Handles the following rule(s):

            aggregate           :   (term compop)? aggregate_function CURLY_OPEN aggregate_elements? CURLY_CLOSE (compop term)?
        """
        # TODO: implement
        raise Exception("Aggregates not supported yet.")


    # Visit a parse tree produced by ASPCoreParser#aggregate_elements.
    def visitAggregate_elements(self, ctx:ASPCoreParser.Aggregate_elementsContext): # TODO: return typing
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


    # Visit a parse tree produced by ASPCoreParser#aggregate_element.
    def visitAggregate_element(self, ctx:ASPCoreParser.Aggregate_elementContext): # TODO: return typing
        """Visits 'aggregate_element'.

        Handles the following rule(s):

            aggregate_element   :   terms? (COLON naf_literals?)?
        """
        # TODO: implement
        raise Exception("Aggregate element not supported yet.")


    # Visit a parse tree produced by ASPCoreParser#aggregate_function.
    def visitAggregate_function(self, ctx:ASPCoreParser.Aggregate_functionContext) -> AggrOp:
        """Visits 'aggregate_function'.

        Handles the following rule(s):

            aggregate_function  :   COUNT
                                |   MAX
                                |   MIN
                                |   SUM
        """
        # get token
        token = ctx.children[0].getSymbol()
        token_type = ASPCoreParser.symbolicNames[token.type]

        return AggrOp[token_type]


    # Visit a parse tree produced by ASPCoreParser#optimize.
    def visitOptimize(self, ctx:ASPCoreParser.OptimizeContext): # TODO: return typing
        """Visits 'optimize'.
        
        Handles the following rule(s):

            optimize            :   optimize_function CURLY_OPEN optimize_elements? CURLY_CLOSE
        """
        # TODO: implement
        raise Exception("Optimization statements not supported yet.")


    # Visit a parse tree produced by ASPCoreParser#optimize_elements.
    def visitOptimize_elements(self, ctx:ASPCoreParser.Optimize_elementsContext): # TODO: return typing
        """Visits 'optimize_elements'.
        
        Handles the following rule(s):

            optimize_elements   :   optimize_element (SEMICOLON optimize_elements)?
        """
        # TODO: implement
        raise Exception("Optimization elements not supported yet.")


    # Visit a parse tree produced by ASPCoreParser#optimize_element.
    def visitOptimize_element(self, ctx:ASPCoreParser.Optimize_elementContext): # TODO: return typing
        """Visits 'optimize_element'.
        
        Handles the following rule(s):

            optimize_element    :   weight_at_level (COLON naf_literals?)?
        """
        # TODO: implement
        raise Exception("Optimization element not supported yet.")


    # Visit a parse tree produced by ASPCoreParser#optimize_function.
    def visitOptimize_function(self, ctx:ASPCoreParser.Optimize_functionContext): # TODO: return typing
        """Visits 'optimize_function'.
        
        Handles the following rule(s):

            optimize_function   :   MAXIMIZE
                    |   MINIMIZE
        """
        # TODO: implement
        raise Exception("Optimization functions not supported yet.")


    # Visit a parse tree produced by ASPCoreParser#weight_at_level.
    def visitWeight_at_level(self, ctx:ASPCoreParser.Weight_at_levelContext): # TODO: return typing
        """Visits 'weight_at_level'.

        Handles the following rule(s):

            weight_at_level     :   term (AT term)? (COMMA terms)?
        """
        # TODO: implement
        raise Exception("Weights and levels not supported yet.")


    # Visit a parse tree produced by ASPCoreParser#naf_literals.
    def visitNaf_literals(self, ctx:ASPCoreParser.Naf_literalsContext) -> Tuple[Tuple[NafLiteral, ...], VariableTable]:
        """Visits 'naf_literals'.

        Handles the following rule(s):

            naf_literals        :   naf_literal (COMMA naf_literals)?
        """
        # naf_literal
        literal, variables = self.visitNaf_literal(ctx.children[0])
        literals = tuple([literal])

        # COMMA naf_literals
        if len(ctx.children) > 1:
            additional_literals, additional_vars = self.visitNaf_literals(ctx.children[2])

            # append literals
            literals += additional_literals
            # merge variables
            variables.merge(additional_vars)

        return (literals, variables)


    # Visit a parse tree produced by ASPCoreParser#naf_literal.
    def visitNaf_literal(self, ctx:ASPCoreParser.Naf_literalContext) -> Tuple[NafLiteral, VariableTable]:
        """Visits 'naf_literal'.

        Handles the following rule(s):

            naf_literal         :   NAF? classical_literal
                                |   builtin_atom ;
        """
        # builtin_atom
        if isinstance(ctx.children[0], ASPCoreParser.Builtin_atomContext):
            return self.visitBuiltin_atom(ctx.children[0])
        # NAF? classical_literal
        else:
            literal, variables = self.visitClassical_literal(ctx.children[-1])

            # classical_literal
            if len(ctx.children) == 1:
                # mark all variables as safe
                variables.set_safe(True)
            # NAF classical_literal
            else:
                # wrap literal in default atom
                literal = DefaultAtom(literal, dneg=True)

            return (literal, variables)


    # Visit a parse tree produced by ASPCoreParser#classical_literal.
    def visitClassical_literal(self, ctx:ASPCoreParser.Classical_literalContext) -> Tuple[Union[Minus,PredicateAtom], VariableTable]:
        """Visits 'classical_literal'.

        Handles the following rule(s):

            classical_literal   :   MINUS? ID (PAREN_OPEN terms? PAREN_CLOSE)?
        """
        n_children = len(ctx.children)

        # get first token
        token = ctx.children[0].getSymbol()
        token_type = ASPCoreParser.symbolicNames[token.type]

        # MINUS ID (true) or ID (false)
        minus = True if(token_type == "MINUS") else False

        # PAREN_OPEN terms PAREN_CLOSE
        if n_children - (minus+1) > 2:
            # parse terms
            terms, variables = self.visitTerms(ctx.children[minus+2])
        else:
            # initialize empty term tuple and variable table
            terms, variables = tuple(), VariableTable()

        id = PredicateAtom(ctx.children[minus].getSymbol().text, terms)

        if minus:
            return ( Minus(id), variables)
        else:
            return ( id, variables )


    # Visit a parse tree produced by ASPCoreParser#builtin_atom.
    def visitBuiltin_atom(self, ctx:ASPCoreParser.Builtin_atomContext) -> Tuple[BuiltinAtom, VariableTable]:
        """Visits 'builtin_atom'.

        Handles the following rule(s):

            builtin_atom        :   term compop term
        """
        comp_op = self.visitCompop(ctx.children[1])

        # select correct comparison construct
        if(comp_op == CompOp.EQUAL):
            Comp = Equal
        if(comp_op == CompOp.UNEQUAL):
            Comp = Unequal
        if(comp_op == CompOp.LESS):
            Comp = Less
        if(comp_op == CompOp.GREATER):
            Comp = Greater
        if(comp_op == CompOp.LESS_OR_EQ):
            Comp = LessEqual
        else:
            Comp = GreaterEqual

        # parse terms
        lterm, lvariables = self.visitTerm(ctx.children[0])
        rterm, rvariables = self.visitTerm(ctx.children[2])

        return ( Comp(lterm, rterm), lvariables.merge(rvariables) )


    # Visit a parse tree produced by ASPCoreParser#compop.
    def visitCompop(self, ctx:ASPCoreParser.CompopContext) -> CompOp:
        """Visits 'compop'.

        Handles the following rule(s):

            compop               :   EQUAL
                                |   UNEQUAL
                                |   LESS
                                |   GREATER
                                |   LESS_OR_EQ
                                |   GREATER_OR_EQ
        """
        # get token
        token = ctx.children[0].getSymbol()
        token_type = ASPCoreParser.symbolicNames[token.type]

        return CompOp[token_type]


    # Visit a parse tree produced by ASPCoreParser#terms.
    def visitTerms(self, ctx:ASPCoreParser.TermsContext) -> Tuple[Tuple[Term, ...], VariableTable]:
        """Visits 'terms'.

        Handles the following rule(s):

            terms               :   term (COMMA terms)?
        """
        # term
        term, variables = self.visitTerm(ctx.children[0])
        terms = tuple([term])

        # COMMA terms
        if len(ctx.children) > 1:
            additional_terms, additional_vars = self.visitTerms(ctx.children[2])

            # append terms
            terms += additional_terms
            # merge variables
            variables.merge(additional_vars)

        return (terms, variables)


    # Visit a parse tree produced by ASPCoreParser#term.
    def visitTerm(self, ctx:ASPCoreParser.TermContext) -> Tuple[Term, VariableTable]:
        """Visits 'term'.
    
        Handles the following rule(s):

            term                :   ID
                                |   STRING
                                |   VARIABLE
                                |   ANONYMOUS_VARIABLE
                                |   PAREN_OPEN term PAREN_CLOSE
                                |   func_term
                                |   arith_term
        """
        # first child is a token
        if isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNode):

            # initialize new variable table
            variables = VariableTable()

            # get token
            token = ctx.children[0].getSymbol()
            token_type = ASPCoreParser.symbolicNames[token.type]

            # ID
            if(token_type == "ID"):
                return ( SymbolicConstant(token.text), variables ) # TODO: predicate or function ?!
            # STRING
            elif(token_type == "STRING"):
                return ( String(token.text), variables )
            # VARIABLE
            elif(token_type == "VARIABLE"):
                var = variables.register(token.text)
                return ( var, variables )
            # ANONYMOUS_VARIABLE
            elif(token_type == "ANONYMOUS_VARIABLE"):
                var = variables.register()
                return ( var, variables )
            # PAREN_OPEN term PAREN_CLOSE
            elif(token_type == "PAREN_OPEN"):
                return self.visitTerm(ctx.children[1]) # parse term
            else:
                raise Exception("TODO: REMOVE RULE.")
        # func_term
        elif isinstance(ctx.children[0], ASPCoreParser.Func_termContext):
            return self.visitFunc_term(ctx.children[0])
        # arith_term
        else:
            return self.visitArith_term(ctx.children[0])


    # Visit a parse tree produced by ASPCoreParser#func_term.
    def visitFunc_term(self, ctx:ASPCoreParser.Func_termContext) -> Tuple[Term, VariableTable]:
        """Visits 'func_term'.

        Handles the following rule(s):

            func_term           :   ID PAREN_OPEN terms PAREN_CLOSE
        """
        # parse terms
        terms, variables = self.visitTerms(ctx.children[2])

        return ( Functional(ctx.children[0].getSymbol().text, terms), variables )


    # Visit a parse tree produced by ASPCoreParser#arith_term.
    def visitArith_term(self, ctx:ASPCoreParser.Arith_termContext) -> Tuple[Term, VariableTable]:
        """Visits 'arith_term'.

        Handles the following rule(s):

            arith_term          :   arith_sum
        """
        # TODO: eliminate rule from grammar?
        return self.visitArith_sum(ctx.children[0])


    # Visit a parse tree produced by ASPCoreParser#arith_sum.
    def visitArith_sum(self, ctx:ASPCoreParser.Arith_sumContext) -> Tuple[Term, VariableTable]:
        """Visits 'arith_sum'.

        Handles the following rule(s):

            arith_sum           :   arith_prod
                                |   arith_sum PLUS arith_prod
                                |   arith_sum MINUS arith_prod
        """
        # arith_sum (PLUS | MINUS) arith_prod
        if len(ctx.children) > 1:

            # get operator token
            token = ctx.children[1].getSymbol()
            token_type = ASPCoreParser.symbolicNames[token.type]

            loperand, lvariables = self.visitArith_sum(ctx.children[0])
            roperand, rvariables = self.visitArith_prod(ctx.children[2])

            # PLUS
            if(ArithOp[token_type] == ArithOp.PLUS):
                return ( Add(loperand, roperand), lvariables.merge(rvariables) )
            # MINUS
            else:
                return ( Sub(loperand, roperand), lvariables.merge(rvariables) )
        # arith_prod
        else:
            return self.visitArith_prod(ctx.children[0]) # (prod, variables)


    # Visit a parse tree produced by ASPCoreParser#arith_prod.
    def visitArith_prod(self, ctx:ASPCoreParser.Arith_prodContext) -> Tuple[Term, VariableTable]:
        """Visits 'arith_prod'.

        Handles the following rule(s):

            arith_prod          :   arith_atom
                                |   arith_prod TIMES arith_atom
                                |   arith_prod DIV arith_atom 
        """
        # arith_prod (TIMES | DIV) arith_atom
        if len(ctx.children) > 1:

            # get operator token
            token = ctx.children[1].getSymbol()
            token_type = ASPCoreParser.symbolicNames[token.type]

            loperand, lvariables = self.visitArith_prod(ctx.children[0])
            roperand, rvariables = self.visitArith_atom(ctx.children[2])

            # TIMES
            if(ArithOp[token_type] == ArithOp.TIMES):
                return ( Mult(loperand, roperand), lvariables.merge(rvariables) )
            # DIV
            else:
                return ( Div(loperand, roperand), lvariables.merge(rvariables) )
        # arith_atom
        else:
            return self.visitArith_atom(ctx.children[0]) # (atom, variables)


    # Visit a parse tree produced by ASPCoreParser#arith_atom.
    def visitArith_atom(self, ctx:ASPCoreParser.Arith_atomContext) -> Tuple[Term, VariableTable]:
        """Visits 'arith_atom'.

        Handles the following rule(s):

            arith_atom          :   (PLUS | MINUS)* (NUMBER | VARIABLE)
                                |   PAREN_OPEN arith_sum PAREN_CLOSE
        """
        # TODO: what about anonymous variables ?

        # get first token
        token = ctx.children[0].getSymbol()
        token_type = ASPCoreParser.symbolicNames[token.type]

        # PAREN_OPEN arith_sum PAREN_CLOSE
        if(token_type == "PAREN_OPEN"):
            return self.visitArith_sum(ctx.children[1]) # (sum, variables)
        # (PLUS | MINUS)* (NUMBER | VARIABLE)
        else:
            # initialize new variable table
            variables = VariableTable()

            # get all tokens (avoid getting first token again)
            tokens = [token] + [child.getSymbol() for child in ctx.children[1:]]

            # TODO: remove?
            # count minuses (pluses can be ignored)
            n_minuses = 0

            for sign in tokens[:-1]:
                sign_type = ASPCoreParser.symbolicNames[sign.type]

                if(sign_type == "MINUS"):
                    n_minuses = 0

            # NUMBER
            if(ASPCoreParser.symbolicNames[tokens[-1].type] == "NUMBER"):
                operand = Number(int(tokens[-1].text))
            # VARIABLE
            else:
                operand = variables.register(tokens[-1].text)

            # odd number of minuses
            if(n_minuses % 2 > 0):
                operand = Minus(operand)

            return (operand, variables)