# Generated from ASP.g4 by ANTLR 4.11.1
import antlr4  # type: ignore

from antlr.ASPCoreParser import ASPCoreParser
from antlr.ASPCoreVisitor import ASPCoreVisitor

from typing import Tuple, Union

from .atom import *
from .term import *
from .choice import *
from .statement import *
from .aggregate import *
from .comparison import *
from .tables import VariableTable, ConstantTable
from .program import Program


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
                    statement = Constraint(body)
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
                    statement = NormalFact(head[0])
            # head CONS body DOT (i.e., disjunctive rule)
            else:
                body, body_variables = self.visitBody(ctx.children[2])

                # merge variables
                variables.merge(body_variables)

                # disjunctive rule
                if len(head) > 1:
                    statement = DisjunctiveRule(head, body)
                # normal rule
                else:
                    statement = NormalRule(head[0], body)
        # optimize DOT
        else:
            statement, variables = self.visitOptimize(ctx.children[0])

        statement.set_variable_table(variables)

        return statement


    # Visit a parse tree produced by ASPCoreParser#head.
    def visitHead(self, ctx:ASPCoreParser.HeadContext) -> Tuple[Union[Choice, Tuple[ClassicalAtom, ...]], VariableTable]:
        """Visits 'head'.

        Handles the following rule(s):

            head                :   disjunction
                                |   choice
        """
        # disjunction
        if isinstance(ctx.children[0], ASPCoreParser.DisjunctionContext):
            head, variables = self.visitDisjunction(ctx.children[0])
        # choice
        else:
            head, variables = self.visitChoice(ctx.children[0])

        # set all variables in head to unsafe
        variables.set_safe(False)

        return (head, variables)


    # Visit a parse tree produced by ASPCoreParser#body.
    def visitBody(self, ctx:ASPCoreParser.BodyContext) -> Tuple[Tuple[Literal, ...], VariableTable]:
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
    def visitDisjunction(self, ctx:ASPCoreParser.DisjunctionContext) -> Tuple[Tuple[ClassicalAtom, ...], VariableTable]:
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
    def visitChoice(self, ctx:ASPCoreParser.ChoiceContext) -> Tuple[Choice, VariableTable]:
        """Visits 'choice'.

        Handles the following rule(s):

            choice              :   (term compop)? CURLY_OPEN choice_elements? CURLY_CLOSE (compop term)?
        """
        moving_index = 0
        variables = None
        lcomp, rcomp = None, None

        # term compop
        if isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNode):
            lterm, variables = self.visitTerm(self[0]) # since this is the first parsed part, we can safely directly assign to 'variables'
            lop = self.visitCompop(ctx.children[1])
            lcomp = (lop, lterm)

            moving_index += 3 # skip CURLY_OPEN as well

        # CURLY_OPEN CURLY_CLOSE
        if isinstance(ctx.children[moving_index], antlr4.tree.Tree.TerminalNode):
            elements = tuple()
            moving_index += 1
        # CURLY_OPEN choice_elements CURLY_CLOSE
        else:
            elements, choice_variables = self.visitChoice_elements(ctx.children[moving_index+1])
            # update variable table
            variables = variables.merge(choice_variables) if variables else choice_variables
            moving_index += 2

        # compop term
        if moving_index < len(ctx.children)-1:
            rterm, rvariables = self.visitTerm(self[moving_index+1])
            rop = self.visitCompop(ctx.children[moving_index])
            rcomp = (rop, rterm)

            # update variable table
            variables = variables.merge(rvariables) if variables else rvariables

        return (Choice(elements, lcomp, rcomp), variables)


    # Visit a parse tree produced by ASPCoreParser#choice_elements.
    def visitChoice_elements(self, ctx:ASPCoreParser.Choice_elementsContext) -> Tuple[Tuple[ChoiceElement, ...], VariableTable]:
        """Visits 'choice_elements'.

        Handles the following rule(s):

            choice_elements     :   choice_element (SEMICOLON choice_elements)?
        """
        # choice_element
        element, variables = self.visitChoice_element(ctx.children[0])
        elements = tuple([element])

        # SEMICOLON choice_elements
        if len(ctx.children) > 1:
            additional_elements, additional_variables = self.visitChoice_elements(ctx.children[2])

            # append literals
            elements += additional_elements
            # merge variables
            variables.merge(additional_variables)            

        return (elements, variables)


    # Visit a parse tree produced by ASPCoreParser#choice_element.
    def visitChoice_element(self, ctx:ASPCoreParser.Choice_elementContext) -> Tuple[ChoiceElement, VariableTable]:
        """Visits 'choice_element'.

        Handles the following rule(s):

            choice_element      :   classical_literal (COLON naf_literals?)?
        """
        # classical_literal
        atom, variables = self.visitClassical_literal(ctx.children[0])

        # COLON naf_literals
        if len(ctx.children) > 2:
            literals, literal_variables = self.visitNaf_literals(ctx.children[2])
            variables.merge(literal_variables)
        # COLON?
        else:
            literals = tuple()

        return ( ChoiceElement(atom, literals), variables )


    # Visit a parse tree produced by ASPCoreParser#aggregate.
    def visitAggregate(self, ctx:ASPCoreParser.AggregateContext) -> Tuple[AggregateFunction, VariableTable]:
        """Visits 'aggregate'.

        Handles the following rule(s):

            aggregate           :   (term compop)? aggregate_function CURLY_OPEN aggregate_elements? CURLY_CLOSE (compop term)?
        """
        moving_index = 0
        variables = None
        lcomp, rcomp = None, None

        # term compop
        if isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNode):
            lterm, variables = self.visitTerm(self[0]) # since this is the first parsed part, we can safely directly assign to 'variables'
            lop = self.visitCompop(ctx.children[1])
            lcomp = (lop, lterm)

            moving_index += 2
        
        # aggregate_function
        aggregate_function = self.visitAggregate_function(ctx.children[moving_index])
        moving_index += 2 # skip CURLY_OPEN as well

        # CURLY_OPEN CURLY_CLOSE
        if isinstance(ctx.children[moving_index], antlr4.tree.Tree.TerminalNode):
            elements = tuple()
            moving_index += 1
        # CURLY_OPEN choice_elements CURLY_CLOSE
        else:
            elements, choice_variables = self.visitAggregate_elements(ctx.children[moving_index+1])
            # update variable table
            # TODO: how to handle variables in aggregates?
            variables = variables.merge(choice_variables) if variables else choice_variables
            moving_index += 2

        # compop term
        if moving_index < len(ctx.children)-1:
            rterm, rvariables = self.visitTerm(self[moving_index+1])
            rop = self.visitCompop(ctx.children[moving_index])
            rcomp = (rop, rterm)

            # update variable table
            # TODO: how to handle variables in aggregates?
            variables = variables.merge(rvariables) if variables else rvariables

        if(aggregate_function == "COUNT"):
            Aggregate = AggregateCount
        elif(aggregate_function == "SUM"):
            Aggregate = AggregateSum
        elif(aggregate_function == "MAX"):
            Aggregate = AggregateMax
        else:
            Aggregate = AggregateMin

        return (Aggregate(elements, lcomp, rcomp), variables)


    # Visit a parse tree produced by ASPCoreParser#aggregate_elements.
    def visitAggregate_elements(self, ctx:ASPCoreParser.Aggregate_elementsContext) -> Tuple[Tuple[AggregateElement, ...], VariableTable]:
        """Visits 'aggregate_elements'.

        Handles the following rule(s):

            aggregate_elements  :   aggregate_element (SEMICOLON aggregate_elements)?
        """
        # aggregate_element
        element, variables = self.visitAggregate_element(ctx.children[0])
        elements = tuple([element])

        # SEMICOLON aggregate_elements
        if len(ctx.children) > 1:
            additional_elements, additional_variables = self.visitAggregate_elements(ctx.children[2])

            # append literals
            elements += additional_elements
            # merge variables
            # TODO: how to handle variables in aggregates?
            variables.merge(additional_variables)            

        return (elements, variables)


    # Visit a parse tree produced by ASPCoreParser#aggregate_element.
    def visitAggregate_element(self, ctx:ASPCoreParser.Aggregate_elementContext) -> Tuple[AggregateElement, VariableTable]:
        """Visits 'aggregate_element'.

        Handles the following rule(s):

            aggregate_element   :   terms? (COLON naf_literals?)?
        """
        # terms
        terms, variables = self.visitTerms(ctx.children[0])

        # COLON naf_literals
        if len(ctx.children) > 2:
            literals, literal_variables = self.visitNaf_literals(ctx.children[2])

            # TODO: how to handle variables in aggregate element?
            # merge variables
            variables.merge(literal_variables)
        # COLON?
        else:
            literals = tuple()

        return (AggregateElement(terms, literals), variables)


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
    def visitOptimize(self, ctx:ASPCoreParser.OptimizeContext) -> Tuple[OptimizeStatement, VariableTable]:
        """Visits 'optimize'.
        
        Handles the following rule(s):

            optimize            :   optimize_function CURLY_OPEN optimize_elements? CURLY_CLOSE
        """
        optimization_function = self.visitOptimize_function(ctx.children[0])
    
        # CURLY_OPEN optimize_elements CURLY_CLOSE
        if len(ctx.children) > 3:
            elements, variables = self.visitOptimize_elements(ctx.children[2])
        # CURLY_OPEN CURLY_CLOSE
        else:
            elements, variables = tuple(), VariableTable()

        if optimization_function == "MINIMIZE":
            return (MinimizeStatement(elements), variables)
        else:
            return (MaximizeStatement(elements), variables)


    # Visit a parse tree produced by ASPCoreParser#optimize_elements.
    def visitOptimize_elements(self, ctx:ASPCoreParser.Optimize_elementsContext) -> Tuple[Tuple[OptimizeElement, ...], VariableTable]:
        """Visits 'optimize_elements'.
        
        Handles the following rule(s):

            optimize_elements   :   optimize_element (SEMICOLON optimize_elements)?
        """
        # optimize_element
        element, variables = self.visitOptimize_element(ctx.children[0])
        elements = tuple([element])

        # SEMICOLON optimize_elements
        if len(ctx.children) > 1:
            additional_elements, additional_variables = self.visitOptimize_elements(ctx.children[2])

            # append literals
            elements += additional_elements
            # merge variables
            # TODO: how to handle variables in optimizations?
            variables.merge(additional_variables)  

        return (elements, variables)


    # Visit a parse tree produced by ASPCoreParser#optimize_element.
    def visitOptimize_element(self, ctx:ASPCoreParser.Optimize_elementContext) -> Tuple[OptimizeElement, VariableTable]:
        """Visits 'optimize_element'.
        
        Handles the following rule(s):

            optimize_element    :   weight_at_level (COLON naf_literals?)?
        """
        # weight_at_level
        weight, level, terms, variables = self.visitWeight_at_level(ctx.children[0])

        # COLON naf_literals
        if len(ctx.children) > 2:
            literals, literals_variables = self.visitNaf_literals(ctx.children[2])

            # merge variables
            # TODO: how to handle variables in optimize elements?
            variables.merge(literals_variables)
        # COLON?
        else:
            literals = tuple()

        return (OptimizeElement(weight, level, terms, literals), variables)


    # Visit a parse tree produced by ASPCoreParser#optimize_function.
    def visitOptimize_function(self, ctx:ASPCoreParser.Optimize_functionContext) -> str:
        """Visits 'optimize_function'.
        
        Handles the following rule(s):

            optimize_function   :   MAXIMIZE
                                |   MINIMIZE
        """
        return ASPCoreParser.symbolicNames[ctx.getSymbol().type]


    # Visit a parse tree produced by ASPCoreParser#weight_at_level.
    def visitWeight_at_level(self, ctx:ASPCoreParser.Weight_at_levelContext) -> Tuple[Term, Term, Tuple[Term, ...], VariableTable]:
        """Visits 'weight_at_level'.

        Handles the following rule(s):

            weight_at_level     :   term (AT term)? (COMMA terms)?
        """
        # weight
        weight, variables = self.visitTerm(ctx.children[0])

        if len(ctx.children) > 0:
            # get next token
            token = ctx.children[1].getSymbol()
            token_type = ASPCoreParser.symbolicNames[token.type]

            moving_index = 2

            # AT term
            if(token_type == "AT"):
                level, level_variables = self.visitTerm(ctx.children[moving_index])

                # TODO: how to handle variables in weight at level?
                # merge variables
                variables.merge(level_variables)

                moving_index += 2
            else:
                level = Number(0)

            # COMMA terms
            if moving_index < len(ctx.children):
                terms, terms_variables = self.visitTerms(ctx.children[moving_index])

                # merge variavles
                # TODO: how to handle variables in weight at level?
                variables.merge(terms_variables)
            else:
                terms = tuple()
        else:
            level = Number(0)
            terms = tuple()
        
        return (weight, level, terms, variables)


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
            
                # wrap literal in default atom
                literal = DefaultAtom(literal, dneg=False)
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