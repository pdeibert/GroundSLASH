from typing import Tuple, Union, List, Optional, TYPE_CHECKING

import antlr4  # type: ignore
from aspy.antlr.ASPCoreLexer import ASPCoreLexer
from aspy.antlr.ASPCoreParser import ASPCoreParser
from aspy.antlr.ASPCoreVisitor import ASPCoreVisitor

from aspy.program.terms import TermTuple, Number, String, SymbolicConstant, Functional, Minus
from aspy.program.literals import LiteralTuple, Naf, Neg, PredicateLiteral, Guard, AggregateElement, AggregateLiteral
from aspy.program.statements import Statement, NormalFact, NormalRule, DisjunctiveFact, DisjunctiveRule, ChoiceElement, Choice, Constraint, OptimizeElement, MaximizeStatement, MinimizeStatement, ChoiceFact, ChoiceRule
from aspy.program.operators import ArithOp, RelOp, AggrOp
from aspy.program.literals.builtin import op2rel
from aspy.program.literals.aggregate import op2aggr
from aspy.program.terms.arithmetic import op2arith
from aspy.program.variable_table import VariableTable

if TYPE_CHECKING:
    from aspy.program.terms import Term
    from aspy.program.literals import Literal, BuiltinLiteral
    from aspy.program.statements import OptimizeStatement


class ProgramBuilder(ASPCoreVisitor):
    """Builds ASP program from ANTLR4 parse tree."""
    def __init__(self, simplify_arithmetic: bool=True) -> None:
        self.simplify_arithmetic = simplify_arithmetic

    # Visit a parse tree produced by ASPCoreParser#program.
    def visitProgram(self, ctx:ASPCoreParser.ProgramContext) -> Tuple[List[Statement], Optional[PredicateLiteral]]:
        """Visits 'program'.
        
        Handles the following rule(s):

            program             :   statements? query? EOF
        """
        statements = []
        query = None

        for child in ctx.children[:-1]:
            # statements
            if isinstance(child, ASPCoreParser.StatementsContext):
                statements += self.visitStatements(child)
            # query
            elif isinstance(child, ASPCoreParser.QueryContext):
                query = self.visitQuery(child)

        return (statements, query)


    # Visit a parse tree produced by ASPCoreParser#statements.
    def visitStatements(self, ctx:ASPCoreParser.StatementsContext):
        """Visits 'statements'.

        Handles the following rule(s):

            statements          :   statement+
        """
        return tuple([self.visitStatement(child) for child in ctx.children])


    # Visit a parse tree produced by ASPCoreParser#query.
    def visitQuery(self, ctx:ASPCoreParser.QueryContext) -> PredicateLiteral:
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
        # initialize empty variable table (for special counters)
        self.var_table = VariableTable()

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
                    statement = Constraint(self.visitBody(ctx.children[1]))
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
            # TODO: what about choice rule???
            head = self.visitHead(ctx.children[0])

            # head DOT | head CONS DOT (i.e., fact)
            if n_children < 4:
                # disjunctive fact
                if len(head) > 1:
                    statement = DisjunctiveFact(head)
                # normal fact
                elif isinstance(head[0], PredicateLiteral):
                    statement = NormalFact(head[0])
                # choice fact
                else:
                    statement = ChoiceFact(head[0])
            # head CONS body DOT (i.e., disjunctive rule)
            else:
                body = self.visitBody(ctx.children[2])

                # disjunctive rule
                if len(head) > 1:
                    statement = DisjunctiveRule(TermTuple(*head), *body)
                # normal rule
                elif isinstance(head[0], PredicateLiteral):
                    statement = NormalRule(head[0], *body)
                else:
                    statement = ChoiceRule(head[0], *body)
        # optimize DOT
        else:
            statement = self.visitOptimize(ctx.children[0])

        return statement


    # Visit a parse tree produced by ASPCoreParser#head.
    def visitHead(self, ctx:ASPCoreParser.HeadContext) -> Union[Choice, Tuple[PredicateLiteral, ...]]:
        """Visits 'head'.

        Handles the following rule(s):

            head                :   disjunction
                                |   choice
        """
        # disjunction
        if isinstance(ctx.children[0], ASPCoreParser.DisjunctionContext):
            return self.visitDisjunction(ctx.children[0])
        # choice
        else:
            return self.visitChoice(ctx.children[0])


    # Visit a parse tree produced by ASPCoreParser#body.
    def visitBody(self, ctx:ASPCoreParser.BodyContext) -> Tuple["Literal", ...]:
        """Visits 'body'.

        Handles the following rule(s):

            body                :   (naf_literal | NAF? aggregate) (COMMA body)?
        """
        # naf_literal
        if isinstance(ctx.children[0], ASPCoreParser.Naf_literalContext):
            literals = tuple([self.visitNaf_literal(ctx.children[0])])
        # NAF aggregate
        elif isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNode):
            literals = tuple([ Naf(self.visitAggregate(ctx.children[1])) ])
        # aggregate
        else:
            literals = tuple([ self.visitAggregate(ctx.children[0]) ])
            
        # COMMA body
        if len(ctx.children) > 2:
            # append literals
            literals += self.visitBody(ctx.children[-1])

        return tuple(literals)


    # Visit a parse tree produced by ASPCoreParser#disjunction.
    def visitDisjunction(self, ctx:ASPCoreParser.DisjunctionContext) -> List[PredicateLiteral]:
        """Visits 'disjunction'.

        Handles the following rule(s):

            disjunction         :   classical_literal (OR disjunction)?
        """
        # classical_literal
        literals = [self.visitClassical_literal(ctx.children[0])]

        # OR disjunction
        if len(ctx.children) > 1:
            # append literals
            literals += self.visitDisjunction(ctx.children[2])

        return literals


    # Visit a parse tree produced by ASPCoreParser#choice.
    def visitChoice(self, ctx:ASPCoreParser.ChoiceContext) -> Choice:
        """Visits 'choice'.

        Handles the following rule(s):

            choice              :   (term relop)? CURLY_OPEN choice_elements? CURLY_CLOSE (relop term)?
        """
        moving_index = 0
        lguard, rguard = None, None

        # term relop
        if isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNode):
            lguard = Guard(self.visitRelop(ctx.children[1]), self.visitTerm(self.children[0]), False)
            moving_index += 3 # skip CURLY_OPEN as well

        # CURLY_OPEN CURLY_CLOSE
        if isinstance(ctx.children[moving_index], antlr4.tree.Tree.TerminalNode):
            elements = tuple()
            moving_index += 1
        # CURLY_OPEN choice_elements CURLY_CLOSE
        else:
            elements = self.visitChoice_elements(ctx.children[moving_index+1])
            moving_index += 2

        # relop term
        if moving_index < len(ctx.children)-1:
            rguard = Guard(self.visitRelop(ctx.children[moving_index]), self.visitTerm(self.children[moving_index+1]), True)

        return Choice(elements, lguard, rguard)


    # Visit a parse tree produced by ASPCoreParser#choice_elements.
    def visitChoice_elements(self, ctx:ASPCoreParser.Choice_elementsContext) -> Tuple[ChoiceElement, ...]:
        """Visits 'choice_elements'.

        Handles the following rule(s):

            choice_elements     :   choice_element (SEMICOLON choice_elements)?
        """
        # choice_element
        elements = tuple([self.visitChoice_element(ctx.children[0])])

        # SEMICOLON choice_elements
        if len(ctx.children) > 1:
            # append literals
            elements += self.visitChoice_elements(ctx.children[2])

        return elements


    # Visit a parse tree produced by ASPCoreParser#choice_element.
    def visitChoice_element(self, ctx:ASPCoreParser.Choice_elementContext) -> ChoiceElement:
        """Visits 'choice_element'.

        Handles the following rule(s):

            choice_element      :   classical_literal (COLON naf_literals?)?
        """
        # classical_literal
        atom = self.visitClassical_literal(ctx.children[0])

        # COLON naf_literals
        if len(ctx.children) > 2:
            literals = self.visitNaf_literals(ctx.children[2])
        # COLON?
        else:
            literals = tuple()

        return ChoiceElement(atom, literals)


    # Visit a parse tree produced by ASPCoreParser#aggregate.
    def visitAggregate(self, ctx:ASPCoreParser.AggregateContext) -> "AggregateLiteral":
        """Visits 'aggregate'.

        Handles the following rule(s):

            aggregate           :   (term relop)? aggregate_function CURLY_OPEN aggregate_elements? CURLY_CLOSE (relop term)?
        """
        moving_index = 0
        lguard, rguard = None, None

        # term relop
        if isinstance(ctx.children[0], ASPCoreParser.TermContext):
            lguard = Guard(self.visitRelop(ctx.children[1]), self.visitTerm(ctx.children[0]), False)
            moving_index += 2 # should now point to 'aggregate_function'

        # aggregate_function
        func = op2aggr[self.visitAggregate_function(ctx.children[moving_index])]()
        moving_index += 2 # skip CURLY_OPEN as well; should now point to 'aggregate_elements' or 'CURLY_CLOSE'

        # CURLY_OPEN CURLY_CLOSE
        if isinstance(ctx.children[moving_index], antlr4.tree.Tree.TerminalNode):
            elements = tuple()
            moving_index += 1 # should now point to 'relop' or be out of bounds
        # CURLY_OPEN choice_elements CURLY_CLOSE
        else:
            elements = self.visitAggregate_elements(ctx.children[moving_index])
            moving_index += 2 # skip CURLY_OPEN as well; should now point to 'relop' or be out of bounds

        # relop term
        if moving_index < len(ctx.children)-1:
            rguard = Guard(self.visitRelop(ctx.children[moving_index]), self.visitTerm(ctx.children[moving_index+1]), True)

        return AggregateLiteral(func, elements, (lguard, rguard))


    # Visit a parse tree produced by ASPCoreParser#aggregate_elements.
    def visitAggregate_elements(self, ctx:ASPCoreParser.Aggregate_elementsContext) -> Tuple[AggregateElement, ...]:
        """Visits 'aggregate_elements'.

        Handles the following rule(s):

            aggregate_elements  :   aggregate_element (SEMICOLON aggregate_elements)?
        """
        # aggregate_element
        elements = tuple([self.visitAggregate_element(ctx.children[0])])

        # SEMICOLON aggregate_elements
        if len(ctx.children) > 1:
            # append literals
            elements += self.visitAggregate_elements(ctx.children[2])

        return elements


    # Visit a parse tree produced by ASPCoreParser#aggregate_element.
    def visitAggregate_element(self, ctx:ASPCoreParser.Aggregate_elementContext) -> AggregateElement:
        """Visits 'aggregate_element'.

        Handles the following rule(s):

            aggregate_element   :   terms? (COLON naf_literals?)?
        """
        # terms
        terms = self.visitTerms(ctx.children[0])

        # COLON naf_literals
        if len(ctx.children) > 2:
            literals = self.visitNaf_literals(ctx.children[2])
        # COLON?
        else:
            literals = tuple()

        return AggregateElement(TermTuple(*terms), LiteralTuple(*literals))


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

        return AggrOp(token.text)


    # Visit a parse tree produced by ASPCoreParser#optimize.
    def visitOptimize(self, ctx:ASPCoreParser.OptimizeContext) -> "OptimizeStatement":
        """Visits 'optimize'.
        
        Handles the following rule(s):

            optimize            :   optimize_function CURLY_OPEN optimize_elements? CURLY_CLOSE
        """
        optimization_function = self.visitOptimize_function(ctx.children[0])
    
        # CURLY_OPEN optimize_elements CURLY_CLOSE
        if len(ctx.children) > 3:
            elements = self.visitOptimize_elements(ctx.children[2])
        # CURLY_OPEN CURLY_CLOSE
        else:
            elements = tuple()

        if optimization_function == "MINIMIZE":
            return MinimizeStatement(elements)
        else:
            return MaximizeStatement(elements)


    # Visit a parse tree produced by ASPCoreParser#optimize_elements.
    def visitOptimize_elements(self, ctx:ASPCoreParser.Optimize_elementsContext) -> Tuple[OptimizeElement, ...]:
        """Visits 'optimize_elements'.
        
        Handles the following rule(s):

            optimize_elements   :   optimize_element (SEMICOLON optimize_elements)?
        """
        # optimize_element
        elements = tuple([self.visitOptimize_element(ctx.children[0])])

        # SEMICOLON optimize_elements
        if len(ctx.children) > 1:
            # append literals
            elements += self.visitOptimize_elements(ctx.children[2])

        return elements


    # Visit a parse tree produced by ASPCoreParser#optimize_element.
    def visitOptimize_element(self, ctx:ASPCoreParser.Optimize_elementContext) -> OptimizeElement:
        """Visits 'optimize_element'.
        
        Handles the following rule(s):

            optimize_element    :   weight_at_level (COLON naf_literals?)?
        """
        # weight_at_level
        weight, level, terms = self.visitWeight_at_level(ctx.children[0])

        # COLON naf_literals
        if len(ctx.children) > 2:
            literals = self.visitNaf_literals(ctx.children[2])
        # COLON?
        else:
            literals = tuple()

        return OptimizeElement(weight, level, terms, literals)


    # Visit a parse tree produced by ASPCoreParser#optimize_function.
    def visitOptimize_function(self, ctx:ASPCoreParser.Optimize_functionContext) -> str:
        """Visits 'optimize_function'.
        
        Handles the following rule(s):

            optimize_function   :   MAXIMIZE
                                |   MINIMIZE
        """
        return ASPCoreParser.symbolicNames[ctx.getSymbol().type]


    # Visit a parse tree produced by ASPCoreParser#weight_at_level.
    def visitWeight_at_level(self, ctx:ASPCoreParser.Weight_at_levelContext) -> Tuple["Term", "Term", Tuple["Term", ...]]:
        """Visits 'weight_at_level'.

        Handles the following rule(s):

            weight_at_level     :   term (AT term)? (COMMA terms)?
        """
        # weight
        weight = self.visitTerm(ctx.children[0])

        if len(ctx.children) > 0:
            # get next token
            token = ctx.children[1].getSymbol()
            token_type = ASPCoreParser.symbolicNames[token.type]

            moving_index = 2

            # AT term
            if(token_type == "AT"):
                level = self.visitTerm(ctx.children[moving_index])
                moving_index += 2
            else:
                level = Number(0)

            # COMMA terms
            if moving_index < len(ctx.children):
                terms = self.visitTerms(ctx.children[moving_index])
            else:
                terms = tuple()
        else:
            level = Number(0)
            terms = tuple()
        
        return (weight, level, terms)


    # Visit a parse tree produced by ASPCoreParser#naf_literals.
    def visitNaf_literals(self, ctx:ASPCoreParser.Naf_literalsContext) -> Tuple["Literal", ...]:
        """Visits 'naf_literals'.

        Handles the following rule(s):

            naf_literals        :   naf_literal (COMMA naf_literals)?
        """
        # naf_literal
        literals = tuple([self.visitNaf_literal(ctx.children[0])])

        # COMMA naf_literals
        if len(ctx.children) > 1:
            # append literals
            literals += self.visitNaf_literals(ctx.children[2])

        return literals


    # Visit a parse tree produced by ASPCoreParser#naf_literal.
    def visitNaf_literal(self, ctx:ASPCoreParser.Naf_literalContext) -> "Literal":
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
            literal = self.visitClassical_literal(ctx.children[-1])

            # NAF classical_literal
            if len(ctx.children) > 1:
                # set NaF to true
                literal = Naf(literal)

            return literal


    # Visit a parse tree produced by ASPCoreParser#classical_literal.
    def visitClassical_literal(self, ctx:ASPCoreParser.Classical_literalContext) -> PredicateLiteral:
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
            terms = self.visitTerms(ctx.children[minus+2])
        else:
            # initialize empty term tuple
            terms = tuple()

        return Neg(PredicateLiteral(ctx.children[minus].getSymbol().text, *terms), minus)


    # Visit a parse tree produced by ASPCoreParser#builtin_atom.
    def visitBuiltin_atom(self, ctx:ASPCoreParser.Builtin_atomContext) -> "BuiltinLiteral":
        """Visits 'builtin_atom'.

        Handles the following rule(s):

            builtin_atom        :   term relop term
        """
        comp_op = self.visitRelop(ctx.children[1])

        return op2rel[comp_op](self.visitTerm(ctx.children[0]), self.visitTerm(ctx.children[2]))


    # Visit a parse tree produced by ASPCoreParser#relop.
    def visitRelop(self, ctx:ASPCoreParser.RelopContext) -> RelOp:
        """Visits 'relop'.

        Handles the following rule(s):

            relop               :   EQUAL
                                |   UNEQUAL
                                |   LESS
                                |   GREATER
                                |   LESS_OR_EQ
                                |   GREATER_OR_EQ
        """
        # get token
        token = ctx.children[0].getSymbol()

        return RelOp(token.text)


    # Visit a parse tree produced by ASPCoreParser#terms.
    def visitTerms(self, ctx:ASPCoreParser.TermsContext) -> Tuple["Term", ...]:
        """Visits 'terms'.

        Handles the following rule(s):

            terms               :   term (COMMA terms)?
        """
        # term
        terms = tuple([self.visitTerm(ctx.children[0])])

        # COMMA terms
        if len(ctx.children) > 1:
            # append terms
            terms += self.visitTerms(ctx.children[2])

        return terms


    # Visit a parse tree produced by ASPCoreParser#term.
    def visitTerm(self, ctx:ASPCoreParser.TermContext) -> "Term":
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

            # get token
            token = ctx.children[0].getSymbol()
            token_type = ASPCoreParser.symbolicNames[token.type]

            # ID
            if(token_type == "ID"):
                return SymbolicConstant(token.text) # TODO: predicate or function ?!
            # STRING
            elif(token_type == "STRING"):
                return String(token.text)
            # VARIABLE
            elif(token_type == "VARIABLE"):
                return self.var_table.create(token.text, register=False)
            # ANONYMOUS_VARIABLE
            elif(token_type == "ANONYMOUS_VARIABLE"):
                return self.var_table.create(register=False)
            # PAREN_OPEN term PAREN_CLOSE
            elif(token_type == "PAREN_OPEN"):
                return self.visitTerm(ctx.children[1]) # parse term
            else:
                raise Exception(f"TODO: REMOVE RULE: TOKEN {token_type}.")
        # func_term
        elif isinstance(ctx.children[0], ASPCoreParser.Func_termContext):
            return self.visitFunc_term(ctx.children[0])
        # arith_term
        else:
            # parse arithmetic term
            arith_term = self.visitArith_term(ctx.children[0])

            # return (simplified arithmetic term)
            return arith_term.simplify() if self.simplify_arithmetic else arith_term


    # Visit a parse tree produced by ASPCoreParser#func_term.
    def visitFunc_term(self, ctx:ASPCoreParser.Func_termContext) -> "Term":
        """Visits 'func_term'.

        Handles the following rule(s):

            func_term           :   ID PAREN_OPEN terms PAREN_CLOSE
        """
        # parse terms
        terms = self.visitTerms(ctx.children[2])

        return Functional(ctx.children[0].getSymbol().text, terms)


    # Visit a parse tree produced by ASPCoreParser#arith_term.
    def visitArith_term(self, ctx:ASPCoreParser.Arith_termContext) -> "Term":
        """Visits 'arith_term'.

        Handles the following rule(s):

            arith_term          :   arith_sum
        """
        # TODO: eliminate rule from grammar?
        return self.visitArith_sum(ctx.children[0])


    # Visit a parse tree produced by ASPCoreParser#arith_sum.
    def visitArith_sum(self, ctx:ASPCoreParser.Arith_sumContext) -> "Term":
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

            loperand = self.visitArith_sum(ctx.children[0])
            roperand = self.visitArith_prod(ctx.children[2])

            # PLUS | MINUS
            return op2arith[ArithOp(token.text)](loperand, roperand)
        # arith_prod
        else:
            return self.visitArith_prod(ctx.children[0])


    # Visit a parse tree produced by ASPCoreParser#arith_prod.
    def visitArith_prod(self, ctx:ASPCoreParser.Arith_prodContext) -> "Term":
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

            loperand = self.visitArith_prod(ctx.children[0])
            roperand = self.visitArith_atom(ctx.children[2])

            # TIMES | DIV
            return op2arith[ArithOp(token.text)](loperand, roperand)
        # arith_atom
        else:
            return self.visitArith_atom(ctx.children[0])


    # Visit a parse tree produced by ASPCoreParser#arith_atom.
    def visitArith_atom(self, ctx:ASPCoreParser.Arith_atomContext) -> "Term":
        """Visits 'arith_atom'.

        Handles the following rule(s):

            arith_atom          :   NUMBER
                                |   VARIABLE
                                |   MINUS arith_atom
                                |   PAREN_OPEN arith_sum PAREN_CLOSE
        """
        # TODO: what about anonymous variables ?

        # get first token
        token = ctx.children[0].getSymbol()
        token_type = ASPCoreParser.symbolicNames[token.type]

        # NUMBER
        if(token_type == "NUMBER"):
            return Number(int(token.text))
        # VARIABLE
        elif(token_type == "VARIABLE"):
            return self.var_table.create(token.text, register=False)
        # MINUS arith_atom
        elif(token_type == "MINUS"):
            return Minus(self.visitArith_atom(ctx.children[1]))
        # PAREN_OPEN arith_sum PAREN_CLOSE
        else:
            return self.visitArith_sum(ctx.children[1])