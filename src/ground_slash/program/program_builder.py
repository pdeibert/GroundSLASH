from typing import TYPE_CHECKING, List, Optional, Tuple, Union

import antlr4  # type: ignore

from ground_slash.parser.SLASHParser import SLASHParser
from ground_slash.parser.SLASHVisitor import SLASHVisitor
from ground_slash.program.literals import (
    AggrElement,
    AggrLiteral,
    Guard,
    LiteralCollection,
    Naf,
    Neg,
    PredLiteral,
)
from ground_slash.program.literals.aggregate import op2aggr
from ground_slash.program.literals.builtin import op2rel
from ground_slash.program.operators import AggrOp, ArithOp, RelOp
from ground_slash.program.query import Query
from ground_slash.program.statements import (  # ChoiceFact,; DisjunctiveFact,; NormalFact,
    NPP,
    Choice,
    ChoiceElement,
    ChoiceRule,
    Constraint,
    DisjunctiveRule,
    NormalRule,
    NPPRule,
    Statement,
)
from ground_slash.program.terms import (
    Functional,
    Minus,
    Number,
    String,
    SymbolicConstant,
    TermTuple,
)
from ground_slash.program.terms.arithmetic import op2arith
from ground_slash.program.variable_table import VariableTable

if TYPE_CHECKING:  # pragma: no cover
    from ground_slash.program.literals import BuiltinLiteral, Literal
    from ground_slash.program.terms import Term


class ProgramBuilder(SLASHVisitor):
    """Builds Answer Set program from ANTLR4 parse tree.

    Attributes:
        simplify_arithmetic:
        TODO
    """

    def __init__(self, simplify_arithmetic: bool = True) -> None:
        """Initializes the program builder instance.

        Args:
            simplify_arithmetic: Boolean indicating whether or not to simplify
                arithmetic terms while building the program. Defaults to `True`.
        """
        self.simplify_arithmetic = simplify_arithmetic

    # Visit a parse tree produced by SLASHParser#program.
    def visitProgram(
        self, ctx: SLASHParser.ProgramContext
    ) -> Tuple[List[Statement], Optional[PredLiteral]]:
        """Visits 'program' context.

        Handles the following rule(s):

            program             :   statements? query? EOF
        """
        statements = []
        query = None

        for child in ctx.children[:-1]:
            # statements
            if isinstance(child, SLASHParser.StatementsContext):
                statements += self.visitStatements(child)
            # query
            elif isinstance(child, SLASHParser.QueryContext):
                query = self.visitQuery(child)

        return (statements, query)

    # Visit a parse tree produced by SLASHParser#statements.
    def visitStatements(
        self, ctx: SLASHParser.StatementsContext
    ) -> Tuple["Statement", ...]:
        """Visits 'statements'.

        Handles the following rule(s):
            statements          :   statement+

        Args:
            ctx: `SLASHParser.StatementsContext` to be visited.

        Returns:
            Tuple of `Statement` instances.
        """
        return tuple([self.visitStatement(child) for child in ctx.children])

    # Visit a parse tree produced by SLASHParser#query.
    def visitQuery(self, ctx: SLASHParser.QueryContext) -> Query:
        """Visits 'query'.

        Handles the following rule(s):
            query               :   classical_literal QUERY_MARK

        Args:
            ctx: `SLASHParser.QueryContext` to be visited.

        Returns:
            `Query` instance.
        """
        return Query(self.visitClassical_literal(ctx.children[0]))

    # Visit a parse tree produced by SLASHParser#statement.
    def visitStatement(self, ctx: SLASHParser.StatementContext) -> "Statement":
        """Visits 'statement'.

        Handles the following rule(s):
            statement           :   CONS body? DOT
                                |   head (CONS body?)? DOT

        Args:
            ctx: `SLASHParser.StatementContext` to be visited.

        Returns:
            `Statement` instance.
        """  # noqa
        # initialize empty variable table (for special counters)
        self.var_table = VariableTable()

        n_children = len(ctx.children)

        # first child is a token
        # CONS body? DOT (i.e., constraint)
        if isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNode):
            # body
            if n_children > 2:
                statement = Constraint(*self.visitBody(ctx.children[1]))
            else:
                # TODO: empty constraint?
                raise Exception("Empty constraints not supported yet.")
        # head (CONS body?)? DOT
        else:
            # TODO: what about choice rule???
            head = self.visitHead(ctx.children[0])
            body = self.visitBody(ctx.children[2]) if n_children >= 4 else tuple()

            if isinstance(head, Choice):
                statement = ChoiceRule(head, body)
            elif isinstance(head, NPP):
                statement = NPPRule(head, body)
            elif len(head) > 1:
                statement = DisjunctiveRule(head, body)
            else:
                statement = NormalRule(head[0], body)

        return statement

    # Visit a parse tree produced by SLASHParser#head.
    def visitHead(
        self, ctx: SLASHParser.HeadContext
    ) -> Union[Choice, Tuple[PredLiteral, ...], NPP]:
        """Visits 'head'.

        Handles the following rule(s):
            head                :   disjunction
                                |   choice
                                |   npp_declaration

        Args:
            ctx: `SLASHParser.HeadContext` to be visited.

        Returns:
            `Choice` instance or tuple of `PredicateLiteral` instances.
        """
        # disjunction
        if isinstance(ctx.children[0], SLASHParser.DisjunctionContext):
            return self.visitDisjunction(ctx.children[0])
        # choice
        elif isinstance(ctx.children[0], SLASHParser.ChoiceContext):
            return self.visitChoice(ctx.children[0])
        # npp_declaration
        else:
            return self.visitNpp_declaration(ctx.children[0])

    # Visit a parse tree produced by SLASHParser#body.
    def visitBody(self, ctx: SLASHParser.BodyContext) -> Tuple["Literal", ...]:
        """Visits 'body'.

        Handles the following rule(s):
            body                :   (naf_literal | NAF? aggregate) (COMMA body)?

        Args:
            ctx: `SLASHParser.BodyContext` to be visited.

        Returns:
            Tuple of `Literal` instances.
        """
        # naf_literal
        if isinstance(ctx.children[0], SLASHParser.Naf_literalContext):
            literals = tuple([self.visitNaf_literal(ctx.children[0])])
        # NAF aggregate
        elif isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNode):
            literals = tuple([Naf(self.visitAggregate(ctx.children[1]))])
        # aggregate
        else:
            literals = tuple([self.visitAggregate(ctx.children[0])])

        # COMMA body
        if len(ctx.children) > 2:
            # append literals
            literals += self.visitBody(ctx.children[-1])

        return tuple(literals)

    # Visit a parse tree produced by SLASHParser#disjunction.
    def visitDisjunction(
        self, ctx: SLASHParser.DisjunctionContext
    ) -> List[PredLiteral]:
        """Visits 'disjunction'.

        Handles the following rule(s):
            disjunction         :   classical_literal (OR disjunction)?

        Args:
            ctx: `SLASHParser.DisjunctionContext` to be visited.

        Returns:
            List of `PredicateLiteral` instances.
        """
        # classical_literal
        literals = [self.visitClassical_literal(ctx.children[0])]

        # OR disjunction
        if len(ctx.children) > 1:
            # append literals
            literals += self.visitDisjunction(ctx.children[2])

        return literals

    # Visit a parse tree produced by SLASHParser#choice.
    def visitChoice(self, ctx: SLASHParser.ChoiceContext) -> Choice:
        """Visits 'choice'.

        Handles the following rule(s):
            choice              :   (term relop)? CURLY_OPEN choice_elements? CURLY_CLOSE (relop term)?

        Args:
            ctx: `SLASHParser.ChoiceContext` to be visited.

        Returns:
            `Choice` instance.
        """  # noqa
        moving_index = 0
        lguard, rguard = None, None

        # term relop
        if isinstance(ctx.children[0], SLASHParser.TermContext):
            lguard = Guard(
                self.visitRelop(ctx.children[1]),
                self.visitTerm(ctx.children[0]),
                False,
            )
            moving_index += 3  # should now point to 'choice_elements' of 'CURLY_CLOSE'
        else:
            moving_index += 1

        # CURLY_OPEN CURLY_CLOSE
        if isinstance(ctx.children[moving_index], antlr4.tree.Tree.TerminalNode):
            elements = tuple()
            moving_index += 1  # should now point to 'relop' or be out of bounds
        # CURLY_OPEN choice_elements CURLY_CLOSE
        else:
            elements = self.visitChoice_elements(ctx.children[moving_index])
            moving_index += 2  # skip CURLY_OPEN as well; should now point to 'relop' or be out of bounds # noqa

        # relop term
        if moving_index < len(ctx.children) - 1:
            rguard = Guard(
                self.visitRelop(ctx.children[moving_index]),
                self.visitTerm(ctx.children[moving_index + 1]),
                True,
            )

        return Choice(elements, (lguard, rguard))

    # Visit a parse tree produced by SLASHParser#choice_elements.
    def visitChoice_elements(
        self, ctx: SLASHParser.Choice_elementsContext
    ) -> Tuple[ChoiceElement, ...]:
        """Visits 'choice_elements'.

        Handles the following rule(s):
            choice_elements     :   choice_element (SEMICOLON choice_elements)?

        Args:
            ctx: `SLASHParser.Choice_elementsContext` to be visited.

        Returns:
            Tuple of `ChoiceElement` instances.
        """
        # choice_element
        elements = tuple([self.visitChoice_element(ctx.children[0])])

        # SEMICOLON choice_elements
        if len(ctx.children) > 1:
            # append literals
            elements += self.visitChoice_elements(ctx.children[2])

        return elements

    # Visit a parse tree produced by SLASHParser#choice_element.
    def visitChoice_element(
        self, ctx: SLASHParser.Choice_elementContext
    ) -> ChoiceElement:
        """Visits 'choice_element'.

        Handles the following rule(s):
            choice_element      :   classical_literal (COLON naf_literals?)?

        Args:
            ctx: `SLASHParser.Choice_elementContext` to be visited.

        Returns:
            `ChoiceElement` instance.
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

    # Visit a parse tree produced by SLASHParser#aggregate.
    def visitAggregate(self, ctx: SLASHParser.AggregateContext) -> "AggrLiteral":
        """Visits 'aggregate'.

        Handles the following rule(s):
            aggregate           :   (term relop)? aggregate_function CURLY_OPEN aggregate_elements? CURLY_CLOSE (relop term)?

        Args:
            ctx: `SLASHParser.AggregateContext` to be visited.

        Returns:
            `AggrLiteral` instance.
        """  # noqa
        moving_index = 0
        lguard, rguard = None, None

        # term relop
        if isinstance(ctx.children[0], SLASHParser.TermContext):
            lguard = Guard(
                self.visitRelop(ctx.children[1]), self.visitTerm(ctx.children[0]), False
            )
            moving_index += 2  # should now point to 'aggregate_function'

        # aggregate_function
        func = op2aggr[self.visitAggregate_function(ctx.children[moving_index])]()
        moving_index += 2  # skip CURLY_OPEN as well; should now point to 'aggregate_elements' or 'CURLY_CLOSE' # noqa

        # CURLY_OPEN CURLY_CLOSE
        if isinstance(ctx.children[moving_index], antlr4.tree.Tree.TerminalNode):
            elements = tuple()
            moving_index += 1  # should now point to 'relop' or be out of bounds
        # CURLY_OPEN choice_elements CURLY_CLOSE
        else:
            elements = self.visitAggregate_elements(ctx.children[moving_index])
            moving_index += 2  # skip CURLY_OPEN as well; should now point to 'relop' or be out of bounds # noqa

        # relop term
        if moving_index < len(ctx.children) - 1:
            rguard = Guard(
                self.visitRelop(ctx.children[moving_index]),
                self.visitTerm(ctx.children[moving_index + 1]),
                True,
            )

        return AggrLiteral(func, elements, (lguard, rguard))

    # Visit a parse tree produced by SLASHParser#aggregate_elements.
    def visitAggregate_elements(
        self, ctx: SLASHParser.Aggregate_elementsContext
    ) -> Tuple[AggrElement, ...]:
        """Visits 'aggregate_elements'.

        Handles the following rule(s):
            aggregate_elements  :   aggregate_element (SEMICOLON aggregate_elements)?

        Args:
            ctx: `SLASHParser.Aggregate_elementsContext` to be visited.

        Returns:
            Tuple of `AggrElement` instances.
        """
        # aggregate_element
        element = self.visitAggregate_element(ctx.children[0])
        elements = tuple([element]) if element is not None else tuple()

        # SEMICOLON aggregate_elements
        if len(ctx.children) > 1:
            # append literals
            elements += self.visitAggregate_elements(ctx.children[2])

        return elements

    # Visit a parse tree produced by SLASHParser#aggregate_element.
    def visitAggregate_element(
        self, ctx: SLASHParser.Aggregate_elementContext
    ) -> AggrElement:
        """Visits 'aggregate_element'.

        Handles the following rule(s):
            aggregate_element   :   terms COLON?
                                |   COLON? naf_literals?
                                |   terms COLON naf_literals

        Args:
            ctx: `SLASHParser.Aggregate_elementContext` to be visited.

        Returns:
            `AggrElement` instance.
        """

        # terms
        terms = (
            self.visitTerms(ctx.children[0])
            if isinstance(ctx.children[0], SLASHParser.TermsContext)
            else tuple()
        )

        # literals
        literals = (
            self.visitNaf_literals(ctx.children[-1])
            if isinstance(ctx.children[-1], SLASHParser.Naf_literalsContext)
            else tuple()
        )

        if not terms and not literals:
            return None
        else:
            return AggrElement(TermTuple(*terms), LiteralCollection(*literals))

    # Visit a parse tree produced by SLASHParser#aggregate_function.
    def visitAggregate_function(
        self, ctx: SLASHParser.Aggregate_functionContext
    ) -> AggrOp:
        """Visits 'aggregate_function'.

        Handles the following rule(s):
            aggregate_function  :   COUNT
                                |   MAX
                                |   MIN
                                |   SUM

        Args:
            ctx: `SLASHParser.Aggregate_functionContext` to be visited.

        Returns:
            `AggrOp` instance.
        """
        # get token
        token = ctx.children[0].getSymbol()

        return AggrOp(token.text)

    # Visit a parse tree produced by SLASHParser#naf_literals.
    def visitNaf_literals(
        self, ctx: SLASHParser.Naf_literalsContext
    ) -> Tuple["Literal", ...]:
        """Visits 'naf_literals'.

        Handles the following rule(s):
            naf_literals        :   naf_literal (COMMA naf_literals)?

        Args:
            ctx: `SLASHParser.Naf_literalsContext` to be visited.

        Returns:
            Tuple of `Literal` instances.
        """
        # naf_literal
        literals = tuple([self.visitNaf_literal(ctx.children[0])])

        # COMMA naf_literals
        if len(ctx.children) > 1:
            # append literals
            literals += self.visitNaf_literals(ctx.children[2])

        return literals

    # Visit a parse tree produced by SLASHParser#naf_literal.
    def visitNaf_literal(self, ctx: SLASHParser.Naf_literalContext) -> "Literal":
        """Visits 'naf_literal'.

        Handles the following rule(s):

            naf_literal         :   NAF? classical_literal
                                |   builtin_atom ;
        """
        # builtin_atom
        if isinstance(ctx.children[0], SLASHParser.Builtin_atomContext):
            return self.visitBuiltin_atom(ctx.children[0])
        # NAF? classical_literal
        else:
            literal = self.visitClassical_literal(ctx.children[-1])

            # NAF classical_literal
            if len(ctx.children) > 1:
                # set NaF to true
                literal = Naf(literal)

            return literal

    # Visit a parse tree produced by SLASHParser#classical_literal.
    def visitClassical_literal(
        self, ctx: SLASHParser.Classical_literalContext
    ) -> PredLiteral:
        """Visits 'classical_literal'.

        Handles the following rule(s):
            classical_literal   :   MINUS? ID (PAREN_OPEN terms? PAREN_CLOSE)?

        Args:
            ctx: `SLASHParser.Classical_literalContext` to be visited.

        Returns:
            `PredLiteral` instance.
        """
        n_children = len(ctx.children)

        # get first token
        token = ctx.children[0].getSymbol()
        token_type = SLASHParser.symbolicNames[token.type]

        # MINUS ID (true) or ID (false)
        minus = True if (token_type == "MINUS") else False

        # PAREN_OPEN terms PAREN_CLOSE
        if n_children - (minus + 1) > 2:
            # parse terms
            terms = self.visitTerms(ctx.children[minus + 2])
        else:
            # initialize empty term tuple
            terms = tuple()

        return Neg(PredLiteral(ctx.children[minus].getSymbol().text, *terms), minus)

    # Visit a parse tree produced by SLASHParser#builtin_atom.
    def visitBuiltin_atom(
        self, ctx: SLASHParser.Builtin_atomContext
    ) -> "BuiltinLiteral":
        """Visits 'builtin_atom'.

        Handles the following rule(s):
            builtin_atom        :   term relop term

        Args:
            ctx: `SLASHParser.Builtin_atomContext` to be visited.

        Returns:
            `BuiltinLiteral` instance.
        """
        comp_op = self.visitRelop(ctx.children[1])

        return op2rel[comp_op](
            self.visitTerm(ctx.children[0]), self.visitTerm(ctx.children[2])
        )

    # Visit a parse tree produced by SLASHParser#relop.
    def visitRelop(self, ctx: SLASHParser.RelopContext) -> RelOp:
        """Visits 'relop'.

        Handles the following rule(s):
            relop               :   EQUAL
                                |   UNEQUAL
                                |   LESS
                                |   GREATER
                                |   LESS_OR_EQ
                                |   GREATER_OR_EQ

        Args:
            ctx: `SLASHParser.RelOpContext` to be visited.

        Returns:
            `RelOp` instance.
        """
        # get token
        token = ctx.children[0].getSymbol()

        return RelOp(token.text)

    # Visit a parse tree produced by SLASHParser#terms.
    def visitTerms(self, ctx: SLASHParser.TermsContext) -> Tuple["Term", ...]:
        """Visits 'terms'.

        Handles the following rule(s):
            terms               :   term (COMMA terms)?

        Args:
            ctx: `SLASHParser.TermsContext` to be visited.

        Returns:
            Tuple of `Term` instances.
        """
        # term
        terms = tuple([self.visitTerm(ctx.children[0])])

        # COMMA terms
        if len(ctx.children) > 1:
            # append terms
            terms += self.visitTerms(ctx.children[2])

        return terms

    # Visit a parse tree produced by SLASHParser#term.
    def visitTerm(self, ctx: SLASHParser.TermContext) -> "Term":
        """Visits 'term'.

        Handles the following rule(s):
            term                :   ID
                                |   STRING
                                |   VARIABLE
                                |   ANONYMOUS_VARIABLE
                                |   PAREN_OPEN term PAREN_CLOSE
                                |   func_term
                                |   arith_term

        Args:
            ctx: `SLASHParser.TermContext` to be visited.

        Returns:
            `Term` instance.
        """
        # first child is a token
        if isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNode):
            # get token
            token = ctx.children[0].getSymbol()
            token_type = SLASHParser.symbolicNames[token.type]

            # ID
            if token_type == "ID":
                return SymbolicConstant(token.text)  # TODO: predicate or function ?!
            # STRING
            elif token_type == "STRING":
                return String(token.text[1:-1])
            # VARIABLE
            elif token_type == "VARIABLE":
                return self.var_table.create(token.text, register=False)
            # ANONYMOUS_VARIABLE
            elif token_type == "ANONYMOUS_VARIABLE":
                return self.var_table.create(register=False)
            # PAREN_OPEN term PAREN_CLOSE
            elif token_type == "PAREN_OPEN":
                return self.visitTerm(ctx.children[1])  # parse term
            else:
                # TODO: ???
                raise Exception(f"TODO: REMOVE RULE: TOKEN {token_type}.")
        # func_term
        elif isinstance(ctx.children[0], SLASHParser.Func_termContext):
            return self.visitFunc_term(ctx.children[0])
        # arith_term
        else:
            # parse arithmetic term
            arith_term = self.visitArith_term(ctx.children[0])

            # return (simplified arithmetic term)
            return arith_term.simplify() if self.simplify_arithmetic else arith_term

    # Visit a parse tree produced by SLASHParser#npp_declaration.
    def visitNpp_declaration(self, ctx: SLASHParser.Npp_declarationContext) -> NPP:
        """Visits 'npp_declaration'.

        Handles the following rule(s):
            npp_declaration     :   NPP PAREN_OPEN ID (PAREN_OPEN terms? PAREN_CLOSE)? SQUARE_OPEN terms SQUARE_CLOSE PAREN_CLOSE

        Args:
            ctx: `SLASHParser.TermContext` to be visited.

        Returns:
            `Term` instance.
        """  # noqa

        # get identifier
        name = ctx.children[2].getSymbol().text

        # get next token
        token_type = SLASHParser.symbolicNames[ctx.children[3].getSymbol().type]

        # PAREN_OPEN terms? PAREN_CLOSE
        terms = (
            self.visitTerms(ctx.children[4])
            if token_type == "PAREN_OPEN"
            and isinstance(ctx.children[4], SLASHParser.TermsContext)
            else TermTuple()
        )

        # COMMA SQUARE_OPEN terms? SQUARE_CLOSE
        outcomes = (
            self.visitTerms(ctx.children[-3])
            if isinstance(ctx.children[-3], SLASHParser.TermsContext)
            else TermTuple()
        )

        return NPP(name, terms, outcomes)

    # Visit a parse tree produced by SLASHParser#func_term.
    def visitFunc_term(self, ctx: SLASHParser.Func_termContext) -> "Functional":
        """Visits 'func_term'.

        Handles the following rule(s):
            func_term           :   ID PAREN_OPEN terms? PAREN_CLOSE

        Args:
            ctx: `SLASHParser.Func_termContext` to be visited.

        Returns:
            `Functional` instance.
        """

        # parse terms
        terms = tuple() if len(ctx.children) < 4 else self.visitTerms(ctx.children[2])

        return Functional(ctx.children[0].getSymbol().text, *terms)

    # Visit a parse tree produced by SLASHParser#arith_term.
    def visitArith_term(self, ctx: SLASHParser.Arith_termContext) -> "Term":
        """Visits 'arith_term'.

        Handles the following rule(s):
            arith_term          :   arith_sum

        Args:
            ctx: `SLASHParser.Arith_termContext` to be visited.

        Returns:
            `Term` instance.
        """
        # TODO: eliminate rule from grammar?
        return self.visitArith_sum(ctx.children[0])

    # Visit a parse tree produced by SLASHParser#arith_sum.
    def visitArith_sum(self, ctx: SLASHParser.Arith_sumContext) -> "Term":
        """Visits 'arith_sum'.

        Handles the following rule(s):
            arith_sum           :   arith_prod
                                |   arith_sum PLUS arith_prod
                                |   arith_sum MINUS arith_prod

        Args:
            ctx: `SLASHParser.Arith_sumContext` to be visited.

        Returns:
            `Term` instance.
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

    # Visit a parse tree produced by SLASHParser#arith_prod.
    def visitArith_prod(self, ctx: SLASHParser.Arith_prodContext) -> "Term":
        """Visits 'arith_prod'.

        Handles the following rule(s):
            arith_prod          :   arith_atom
                                |   arith_prod TIMES arith_atom
                                |   arith_prod DIV arith_atom

        Args:
            ctx: `SLASHParser.Arith_prodContext` to be visited.

        Returns:
            `Term` instance.
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

    # Visit a parse tree produced by SLASHParser#arith_atom.
    def visitArith_atom(self, ctx: SLASHParser.Arith_atomContext) -> "Term":
        """Visits 'arith_atom'.

        Handles the following rule(s):
            arith_atom          :   NUMBER
                                |   VARIABLE
                                |   MINUS arith_atom
                                |   PAREN_OPEN arith_sum PAREN_CLOSE

        Args:
            ctx: `SLASHParser.Arith_atomContext` to be visited.

        Returns:
            `Term` instance.
        """
        # TODO: what about anonymous variables ?

        # get first token
        token = ctx.children[0].getSymbol()
        token_type = SLASHParser.symbolicNames[token.type]

        # NUMBER
        if token_type == "NUMBER":
            return Number(int(token.text))
        # VARIABLE
        elif token_type == "VARIABLE":
            return self.var_table.create(token.text, register=False)
        # MINUS arith_atom
        elif token_type == "MINUS":
            return Minus(self.visitArith_atom(ctx.children[1]))
        # PAREN_OPEN arith_sum PAREN_CLOSE
        else:
            return self.visitArith_sum(ctx.children[1])
