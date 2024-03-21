from typing import TYPE_CHECKING, Any, List, Optional, Self, Tuple, Union

from lark import Token, Transformer

from ground_slash.program.literals import (
    AggrElement,
    AggrLiteral,
    BuiltinLiteral,
    Guard,
    Literal,
    LiteralCollection,
    Naf,
    Neg,
    PredLiteral,
)
from ground_slash.program.literals.aggregate import op2aggr
from ground_slash.program.literals.builtin import op2rel
from ground_slash.program.operators import AggrOp, ArithOp, RelOp
from ground_slash.program.query import Query
from ground_slash.program.statements import (
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
    Term,
    TermTuple,
)
from ground_slash.program.terms.arithmetic import op2arith
from ground_slash.program.variable_table import VariableTable

if TYPE_CHECKING:
    from lark import Tree


class EarleyTransformer(Transformer):
    """Builds a SLASH program from a Lark parse tree obtained using the Earley parser.

    Attributes:
        simplify_arithmetic:
        TODO
    """

    def __init__(self: Self, simplify_arithmetic: bool = True) -> None:
        """Initializes the transformer instance.

        Args:
            simplify_arithmetic: Boolean indicating whether or not to simplify
                arithmetic terms while building the program. Defaults to `True`.
        """
        self.simplify_arithmetic = simplify_arithmetic
        self.var_table = None

    def transform(
        self: Self, tree: "Tree"
    ) -> Tuple[Tuple[Statement, ...], Optional[PredLiteral]]:
        # initialize new variable table
        self.var_table = VariableTable()
        return super().transform(tree)

    def program(
        self: Self, args: List[Any]
    ) -> Tuple[Tuple[Statement, ...], Optional[PredLiteral]]:
        """Visits 'program' context.

        Handles the following rule(s):

            program             :   statements? query?

        Args:
            args: List of arguments.

        Returns:
            Tuple of a list of `Statement` instances and an optional 'PredLiteral' instance representing the query.
        """
        statements = tuple()
        query = None

        for child in args:
            # statements
            if isinstance(child, tuple):
                statements = child
            # query
            elif isinstance(child, Query):
                query = child

        return (statements, query)

    def statements(self: Self, args: List[Any]) -> Tuple["Statement", ...]:
        """Visits 'statements'.

        Handles the following rule(s):
            statements          :   statement+

        Args:
            args: List of arguments.

        Returns:
            Tuple of `Statement` instances.
        """
        return tuple(args)

    def query(self: Self, args: List[Any]) -> Query:
        """Visits 'query'.

        Handles the following rule(s):
            query               :   classical_literal QUERY_MARK

        Args:
            args: List of arguments.

        Returns:
            `Query` instance.
        """
        return Query(args[0])

    def statement(self: Self, args: List[Any]) -> "Statement":
        """Visits 'statement'.

        Handles the following rule(s):
            statement           :   CONS body? DOT
                                |   head (CONS body?)? DOT

        Args:
            args: List of arguments.

        Returns:
            `Statement` instance.
        """  # noqa
        # initialize empty variable table (for special counters)
        self.var_table = VariableTable()

        n_children = len(args)

        # first child is a token
        # CONS body? DOT (i.e., constraint)
        if isinstance(args[0], Token):
            # body
            if n_children > 2:
                statement = Constraint(*args[1])
            else:
                # TODO: empty constraint?
                raise Exception("Empty constraints not supported yet.")
        # head (CONS body?)? DOT
        else:
            # TODO: what about choice rule???
            head = args[0]
            body = args[2] if n_children >= 4 else tuple()

            if isinstance(head, Choice):
                statement = ChoiceRule(head, body)
            elif isinstance(head, NPP):
                statement = NPPRule(head, body)
            elif len(head) > 1:
                statement = DisjunctiveRule(head, body)
            else:
                statement = NormalRule(head[0], body)

        return statement

    def head(
        self: Self, args: List[Any]
    ) -> Union[Choice, Tuple[PredLiteral, ...], NPP]:
        """Visits 'head'.

        Handles the following rule(s):
            head                :   disjunction
                                |   choice
                                |   npp_declaration

        Args:
            args: List of arguments.

        Returns:
            `Choice` instance or tuple of `PredicateLiteral` instances.
        """
        # disjunction
        if isinstance(args[0], list):
            return args[0]
        # choice
        elif isinstance(args[0], Choice):
            return args[0]
        # npp_declaration
        else:
            return args[0]

    def body(self: Self, args: List[Any]) -> Tuple["Literal", ...]:
        """Visits 'body'.

        Handles the following rule(s):
            body                :   (naf_literal | NAF? aggregate) (COMMA body)?

        Args:
            args: List of arguments.

        Returns:
            Tuple of `Literal` instances.
        """
        # naf_literal
        # TODO: correct ???
        if isinstance(args[0], Literal):
            literals = tuple([args[0]])
        # NAF aggregate
        elif isinstance(args[0], Token):
            literals = tuple([Naf(args[1])])
        # aggregate
        else:
            literals = tuple([args[0]])

        # COMMA body
        if len(args) > 2:
            # append literals
            literals += args[-1]

        return tuple(literals)

    def disjunction(self: Self, args: List[Any]) -> List[PredLiteral]:
        """Visits 'disjunction'.

        Handles the following rule(s):
            disjunction         :   classical_literal (OR disjunction)?

        Args:
            args: List of arguments.

        Returns:
            List of `PredicateLiteral` instances.
        """
        # classical_literal
        literals = [args[0]]

        # OR disjunction
        if len(args) > 1:
            # append literals
            literals += args[2]

        return literals

    def choice(self: Self, args: List[Any]) -> Choice:
        """Visits 'choice'.

        Handles the following rule(s):
            choice              :   (term relop)? CURLY_OPEN choice_elements? CURLY_CLOSE (relop term)?

        Args:
            args: List of arguments.

        Returns:
            `Choice` instance.
        """  # noqa
        moving_index = 0
        lguard, rguard = None, None

        # term relop
        if isinstance(args[0], Term):
            lguard = Guard(
                args[1],
                args[0],
                False,
            )
            moving_index += 3  # should now point to 'choice_elements' of 'CURLY_CLOSE'
        else:
            moving_index += 1

        # CURLY_OPEN CURLY_CLOSE
        if isinstance(args[moving_index], Token):
            elements = tuple()
            moving_index += 1  # should now point to 'relop' or be out of bounds
        # CURLY_OPEN choice_elements CURLY_CLOSE
        else:
            elements = args[moving_index]
            moving_index += 2  # skip CURLY_OPEN as well; should now point to 'relop' or be out of bounds # noqa

        # relop term
        if moving_index < len(args) - 1:
            rguard = Guard(
                args[moving_index],
                args[moving_index + 1],
                True,
            )

        return Choice(elements, (lguard, rguard))

    def choice_elements(self: Self, args: List[Any]) -> Tuple[ChoiceElement, ...]:
        """Visits 'choice_elements'.

        Handles the following rule(s):
            choice_elements     :   choice_element (SEMICOLON choice_elements)?

        Args:
            args: List of arguments.

        Returns:
            Tuple of `ChoiceElement` instances.
        """
        # choice_element
        elements = tuple([args[0]])

        # SEMICOLON choice_elements
        if len(args) > 1:
            # append literals
            elements += args[2]

        return elements

    def choice_element(self: Self, args: List[Any]) -> ChoiceElement:
        """Visits 'choice_element'.

        Handles the following rule(s):
            choice_element      :   classical_literal (COLON naf_literals?)?

        Args:
            args: List of arguments.

        Returns:
            `ChoiceElement` instance.
        """
        # classical_literal
        atom = args[0]

        # COLON naf_literals
        if len(args) > 2:
            literals = args[2]
        # COLON?
        else:
            literals = tuple()

        return ChoiceElement(atom, literals)

    def aggregate(self: Self, args: List[Any]) -> "AggrLiteral":
        """Visits 'aggregate'.

        Handles the following rule(s):
            aggregate           :   (term relop)? aggregate_function CURLY_OPEN aggregate_elements? CURLY_CLOSE (relop term)?

        Args:
            args: List of arguments.

        Returns:
            `AggrLiteral` instance.
        """  # noqa
        moving_index = 0
        lguard, rguard = None, None

        # term relop
        if isinstance(args[0], Term):
            lguard = Guard(args[1], args[0], False)
            moving_index += 2  # should now point to 'aggregate_function'

        # aggregate_function
        func = op2aggr[args[moving_index]]()
        moving_index += 2  # skip CURLY_OPEN as well; should now point to 'aggregate_elements' or 'CURLY_CLOSE' # noqa

        # CURLY_OPEN CURLY_CLOSE
        if isinstance(args[moving_index], Token):
            elements = tuple()
            moving_index += 1  # should now point to 'relop' or be out of bounds
        # CURLY_OPEN choice_elements CURLY_CLOSE
        else:
            elements = args[moving_index]
            moving_index += 2  # skip CURLY_OPEN as well; should now point to 'relop' or be out of bounds # noqa

        # relop term
        if moving_index < len(args) - 1:
            rguard = Guard(
                args[moving_index],
                args[moving_index + 1],
                True,
            )

        return AggrLiteral(func, elements, (lguard, rguard))

    def aggregate_elements(self: Self, args: List[Any]) -> Tuple[AggrElement, ...]:
        """Visits 'aggregate_elements'.

        Handles the following rule(s):
            aggregate_elements  :   aggregate_element (SEMICOLON aggregate_elements)?

        Args:
            args: List of arguments.

        Returns:
            Tuple of `AggrElement` instances.
        """
        # aggregate_element
        element = args[0]
        elements = tuple([element]) if element is not None else tuple()

        # SEMICOLON aggregate_elements
        if len(args) > 1:
            # append literals
            elements += args[2]

        return elements

    def aggregate_element(self: Self, args: List[Any]) -> AggrElement:
        """Visits 'aggregate_element'.

        Handles the following rule(s):
            aggregate_element   :   terms COLON?
                                |   COLON? naf_literals?
                                |   terms COLON naf_literals

        Args:
            args: List of arguments.

        Returns:
            `AggrElement` instance.
        """

        # terms
        terms = args[0] if isinstance(args[0], TermTuple) else TermTuple()

        # literals
        literals = (
            args[-1] if isinstance(args[-1], LiteralCollection) else LiteralCollection()
        )

        if not terms and not literals:
            return None
        else:
            return AggrElement(TermTuple(*terms), literals)

    def aggregate_function(self: Self, args: List[Any]) -> AggrOp:
        """Visits 'aggregate_function'.

        Handles the following rule(s):
            aggregate_function  :   COUNT
                                |   MAX
                                |   MIN
                                |   SUM

        Args:
            args: List of arguments.

        Returns:
            `AggrOp` instance.
        """
        # get token
        token = args[0]

        return AggrOp(token.value)

    def naf_literals(self: Self, args: List[Any]) -> LiteralCollection:
        """Visits 'naf_literals'.

        Handles the following rule(s):
            naf_literals        :   naf_literal (COMMA naf_literals)?

        Args:
            args: List of arguments.

        Returns:
            Tuple of `Literal` instances.
        """
        # naf_literal
        literals = LiteralCollection(args[0])

        # COMMA naf_literals
        if len(args) > 1:
            # append literals
            literals += args[2]

        return literals

    def naf_literal(self: Self, args: List[Any]) -> "Literal":
        """Visits 'naf_literal'.

        Handles the following rule(s):

            naf_literal         :   NAF? classical_literal
                                |   builtin_atom ;

        Args:
            args: List of arguments.

        Returns:
            `Literal` instance.
        """
        # builtin_atom
        if isinstance(args[0], BuiltinLiteral):
            return args[0]
        # NAF? classical_literal
        else:
            literal = args[-1]

            # NAF classical_literal
            if len(args) > 1:
                # set NaF to true
                literal = Naf(literal)

            return literal

    def classical_literal(self: Self, args: List[Any]) -> PredLiteral:
        """Visits 'classical_literal'.

        Handles the following rule(s):
            classical_literal   :   MINUS? ID (PAREN_OPEN terms? PAREN_CLOSE)?

        Args:
            args: List of arguments.

        Returns:
            `PredLiteral` instance.
        """
        n_children = len(args)

        # get first token
        token = args[0]
        token_type = token.type

        # MINUS ID (true) or ID (false)
        minus = True if (token_type == "MINUS") else False

        # PAREN_OPEN terms PAREN_CLOSE
        if n_children - (minus + 1) > 2:
            # parse terms
            terms = args[minus + 2]
        else:
            # initialize empty term tuple
            terms = tuple()

        return Neg(PredLiteral(args[minus].value, *terms), minus)

    def builtin_atom(self: Self, args: List[Any]) -> "BuiltinLiteral":
        """Visits 'builtin_atom'.

        Handles the following rule(s):
            builtin_atom        :   term relop term

        Args:
            args: List of arguments.

        Returns:
            `BuiltinLiteral` instance.
        """
        comp_op = args[1]

        return op2rel[comp_op](args[0], args[2])

    def relop(self: Self, args: List[Any]) -> RelOp:
        """Visits 'relop'.

        Handles the following rule(s):
            relop               :   EQUAL
                                |   UNEQUAL
                                |   LESS
                                |   GREATER
                                |   LESS_OR_EQ
                                |   GREATER_OR_EQ

        Args:
            args: List of arguments.

        Returns:
            `RelOp` instance.
        """
        # get token
        token = args[0]

        return RelOp(token.value)

    def terms(self: Self, args: List[Any]) -> TermTuple:
        """Visits 'terms'.

        Handles the following rule(s):
            terms               :   term (COMMA terms)?

        Args:
            args: List of arguments.

        Returns:
            Tuple of `Term` instances.
        """
        # term
        terms = TermTuple(args[0])

        # COMMA terms
        if len(args) > 1:
            # append terms
            terms += args[2]

        return terms

    def term(self: Self, args: List[Any]) -> "Term":
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
            args: List of arguments.

        Returns:
            `Term` instance.
        """
        # first child is a token
        if isinstance(args[0], Token):
            # get token
            token = args[0]
            token_type = token.type

            # ID
            if token_type == "ID":
                return SymbolicConstant(token.value)  # TODO: predicate or function ?!
            # STRING
            elif token_type == "STRING":
                return String(token.value[1:-1])
            # VARIABLE
            elif token_type == "VARIABLE":
                return self.var_table.create(token.value, register=False)
            # ANONYMOUS_VARIABLE
            elif token_type == "ANONYMOUS_VARIABLE":
                return self.var_table.create(register=False)
            # PAREN_OPEN term PAREN_CLOSE
            elif token_type == "PAREN_OPEN":
                return args[1]  # parse term
            else:
                # TODO: ???
                raise Exception(f"TODO: REMOVE RULE: TOKEN {token_type}.")
        # func_term
        elif isinstance(args[0], Functional):
            return args[0]
        # arith_term
        else:
            # parse arithmetic term
            arith_term = args[0]

            # return (simplified arithmetic term)
            return arith_term.simplify() if self.simplify_arithmetic else arith_term

    def npp_declaration(self: Self, args: List[Any]) -> NPP:
        """Visits 'npp_declaration'.

        Handles the following rule(s):
            npp_declaration     :   NPP PAREN_OPEN ID (PAREN_OPEN terms? PAREN_CLOSE)? SQUARE_OPEN terms SQUARE_CLOSE PAREN_CLOSE

        Args:
            args: List of arguments.

        Returns:
            `Term` instance.
        """  # noqa

        # get identifier
        name = args[2].value

        # get next token
        token_type = args[3].type

        # PAREN_OPEN terms? PAREN_CLOSE
        terms = (
            args[4]
            if token_type == "PAREN_OPEN" and isinstance(args[4], TermTuple)
            else TermTuple()
        )

        # COMMA SQUARE_OPEN terms? SQUARE_CLOSE
        outcomes = args[-3] if isinstance(args[-3], TermTuple) else TermTuple()

        return NPP(name, terms, outcomes)

    def func_term(self: Self, args: List[Any]) -> "Functional":
        """Visits 'func_term'.

        Handles the following rule(s):
            func_term           :   ID PAREN_OPEN terms? PAREN_CLOSE

        Args:
            args: List of arguments.

        Returns:
            `Functional` instance.
        """

        # parse terms
        terms = tuple() if len(args) < 4 else args[2]

        return Functional(args[0].value, *terms)

    def arith_term(self: Self, args: List[Any]) -> "Term":
        """Visits 'arith_term'.

        Handles the following rule(s):
            arith_term          :   arith_sum

        Args:
            args: List of arguments.

        Returns:
            `Term` instance.
        """
        # TODO: eliminate rule from grammar?
        return args[0]

    def arith_sum(self: Self, args: List[Any]) -> "Term":
        """Visits 'arith_sum'.

        Handles the following rule(s):
            arith_sum           :   arith_prod
                                |   arith_sum PLUS arith_prod
                                |   arith_sum MINUS arith_prod

        Args:
            args: List of arguments.

        Returns:
            `Term` instance.
        """
        # arith_sum (PLUS | MINUS) arith_prod
        if len(args) > 1:
            # get operands and operator token
            loperand, op_token, roperand = args

            # PLUS | MINUS
            return op2arith[ArithOp(op_token.value)](loperand, roperand)
        # arith_prod
        else:
            return args[0]

    def arith_prod(self: Self, args: List[Any]) -> "Term":
        """Visits 'arith_prod'.

        Handles the following rule(s):
            arith_prod          :   arith_atom
                                |   arith_prod TIMES arith_atom
                                |   arith_prod DIV arith_atom

        Args:
            args: List of arguments.

        Returns:
            `Term` instance.
        """
        # arith_prod (TIMES | DIV) arith_atom
        if len(args) > 1:
            # get operands and operator token
            loperand, op_token, roperand = args

            # TIMES | DIV
            return op2arith[ArithOp(op_token.value)](loperand, roperand)
        # arith_atom
        else:
            return args[0]

    def arith_atom(self: Self, args: List[Any]) -> "Term":
        """Visits 'arith_atom'.

        Handles the following rule(s):
            arith_atom          :   NUMBER
                                |   VARIABLE
                                |   MINUS arith_atom
                                |   PAREN_OPEN arith_sum PAREN_CLOSE

        Args:
            args: List of arguments.

        Returns:
            `Term` instance.
        """
        # get first token
        token = args[0]
        token_type = token.type

        # NUMBER
        if token_type == "NUMBER":
            return Number(int(token.value))
        # VARIABLE
        elif token_type == "VARIABLE":
            return self.var_table.create(token.value, register=False)
        # MINUS arith_atom
        elif token_type == "MINUS":
            return Minus(args[1])
        # PAREN_OPEN arith_sum PAREN_CLOSE
        else:
            return args[1]
