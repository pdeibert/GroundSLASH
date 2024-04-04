from typing import TYPE_CHECKING, List, Optional, Self, Tuple, Union

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
    ArithTerm,
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

    def __init__(self: Self, simplify_arithmetic: bool = True) -> None:
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
    def visitQuery(self: Self, ctx: SLASHParser.QueryContext) -> Query:
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
    def visitStatement(self: Self, ctx: SLASHParser.StatementContext) -> "Statement":
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
    def visitBody(self: Self, ctx: SLASHParser.BodyContext) -> Tuple["Literal", ...]:
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

    # Visit a parse tree produced by SLASHParser#npp_declaration.
    def visitNpp_declaration(
        self: Self, ctx: SLASHParser.Npp_declarationContext
    ) -> NPP:
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
    def visitChoice(self: Self, ctx: SLASHParser.ChoiceContext) -> Choice:
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
    def visitAggregate(self: Self, ctx: SLASHParser.AggregateContext) -> "AggrLiteral":
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
    def visitNaf_literal(self: Self, ctx: SLASHParser.Naf_literalContext) -> "Literal":
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
    def visitRelop(self: Self, ctx: SLASHParser.RelopContext) -> RelOp:
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
    def visitTerms(self: Self, ctx: SLASHParser.TermsContext) -> Tuple["Term", ...]:
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
    def visitTerm(self: Self, ctx: SLASHParser.TermContext) -> "Term":
        """Visits 'term'.

        Handles the following rule(s):
            term                :   term_sum

        Args:
            ctx: `SLASHParser.TermContext` to be visited.

        Returns:
            `Term` instance.
        """
        # term_sum
        term = self.visitTerm_sum(ctx.children[0])

        if isinstance(term, ArithTerm) and self.simplify_arithmetic:
            # simplify arithmetic term
            term = term.simplify()

        return term

    # Visit a parse tree produced by SLASHParser#term_sum.
    def visitTerm_sum(self: Self, ctx: SLASHParser.Term_sumContext) -> "Term":
        """Visits 'term_sum'.

        Handles the following rule(s):
            term_sum            :   term_sum PLUS term_prod
                                |   term_sum MINUS term_prod
                                |   term_prod

        Args:
            ctx: `SLASHParser.Term_sumContext` to be visited.

        Returns:
            `Term` instance.
        """
        # term_sum (PLUS | MINUS) term_prod
        if len(ctx.children) > 1:
            # get operator token
            token = ctx.children[1].getSymbol()

            loperand = self.visitTerm_sum(ctx.children[0])
            roperand = self.visitTerm_prod(ctx.children[2])

            # PLUS | MINUS
            return op2arith[ArithOp(token.text)](loperand, roperand)
        # term_prod
        else:
            return self.visitTerm_prod(ctx.children[0])

    # Visit a parse tree produced by SLASHParser#term_prod.
    def visitTerm_prod(self: Self, ctx: SLASHParser.Term_prodContext) -> "Term":
        """Visits 'term_prod'.

        Handles the following rule(s):
            term_prod           :   term_prod TIMES term_atom
                                |   term_prod TIMES term_atom
                                |   term_atom

        Args:
            ctx: `SLASHParser.Term_prodContext` to be visited.

        Returns:
            `Term` instance.
        """
        # term_prod (TIMES | DIV) term_atom
        if len(ctx.children) > 1:
            # get operator token
            token = ctx.children[1].getSymbol()

            loperand = self.visitTerm_prod(ctx.children[0])
            roperand = self.visitTerm_atom(ctx.children[2])

            # TIMES | DIV
            return op2arith[ArithOp(token.text)](loperand, roperand)
        # term_atom
        else:
            return self.visitTerm_atom(ctx.children[0])

    # Visit a parse tree produced by SLASHParser#Term_atom.
    def visitTerm_atom(self: Self, ctx: SLASHParser.Term_atomContext) -> "Term":
        """Visits 'term_atom'.

        Handles the following rule(s):
            term_atom           :   NUMBER
                                |   STRING
                                |   VARIABLE
                                |   ANONYMOUS_VARIABLE
                                |   PAREN_OPEN term PAREN_CLOSE
                                |   MINUS term_sum
                                |   symbolic_term

        Args:
            ctx: `SLASHParser.Term_atomContext` to be visited.

        Returns:
            `Term` instance.
        """
        # first child is a token
        if isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNode):
            # get token
            token = ctx.children[0].getSymbol()
            token_type = SLASHParser.symbolicNames[token.type]

            # NUMBER
            if token_type == "NUMBER":
                return Number(int(token.text))
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
                # TODO: is (term) really identical to term?
                return self.visitTerm(ctx.children[1])  # parse term
            # MINUS arith_atom
            elif token_type == "MINUS":
                term = self.visitTerm_sum(ctx.children[1])

                if not isinstance(term, (Number, ArithTerm)):
                    raise ValueError(
                        f"Invalid argument of type {type(term)} for arithmetic operation 'MINUS'."
                    )
                return Minus(term)
            else:
                # TODO
                raise Exception()
        # symbolic_term
        else:
            return self.visitSymbolic_term(ctx.children[0])

    # Visit a parse tree produced by SLASHParser#Symbolic_term.
    def visitSymbolic_term(
        self: Self, ctx: SLASHParser.Symbolic_termContext
    ) -> Union[SymbolicConstant, Functional]:
        """Visits 'symbolic_term'.

        Handles the following rule(s):
            symbolic_term       :   ID (PAREN_OPEN terms? PAREN_CLOSE)?

        Args:
            ctx: `SLASHParser.Symbolic_termContext` to be visited.

        Returns:
            `Term` instance.
        """
        symbolic_id = ctx.children[0].getSymbol().text

        # ID
        if len(ctx.children) == 1:
            # return symbolic constant
            return SymbolicConstant(symbolic_id)
        # ID PAREN_OPEN terms? PAREN_CLOSE
        else:
            if not isinstance(ctx.children[-2], antlr4.tree.Tree.TerminalNode):
                terms = self.visitTerms(ctx.children[-2])
            else:
                terms = tuple()

            # return functional term
            return Functional(symbolic_id, *terms)
