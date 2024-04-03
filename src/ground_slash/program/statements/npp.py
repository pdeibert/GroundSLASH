from copy import deepcopy
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Self,
    Set,
    Tuple,
    Union,
)

from ground_slash.program.expression import Expr
from ground_slash.program.literals import (
    AggrLiteral,
    Guard,
    LiteralCollection,
    PredLiteral,
)
from ground_slash.program.operators import RelOp
from ground_slash.program.safety_characterization import SafetyTriplet
from ground_slash.program.substitution import Substitution
from ground_slash.program.terms import Number, Term, TermTuple

from .choice import Choice, ChoiceElement
from .statement import Statement

if TYPE_CHECKING:  # pragma: no cover
    from ground_slash.program.literals import AggrPlaceholder, Literal
    from ground_slash.program.query import Query
    from ground_slash.program.statements import AggrBaseRule, AggrElemRule
    from ground_slash.program.terms import Variable
    from ground_slash.program.variable_table import VariableTable


class NPP(Expr):
    """Neural-probabilistic predicate expression.

    Attributes:
        terms: `TermTuple` instance representing the deterministic arguments
            of the predicate.
        outcomes: `TermTuple` instance representing the possible outcomes of the neural-
            probabilistic predicate.
        atoms: `LiteralCollection` instance consisting of the possible predicate atoms represented
            by the NPP.
        ground: Boolean indicating whether or not the NPP expression is ground.
            The expression is considered ground if all guards and elements are ground.
    """  # noqa

    def __init__(
        self: Self,
        name: str,
        terms: Iterable[Term],
        outcomes: Iterable[Term],
    ) -> None:
        """Initializes the neural-probabilistic predicate expression instance.

        Args:
            name: String representing the identifier of the predicate.
            terms: Iterable of `Term` instances representing the deterministic arguments
                of the predicate.
            outcomes: Iterable of `Term` instances representing the possible outcomes of the neural-
                probabilistic predicate.
        """  # noqa
        self.name = name
        self.terms = terms if isinstance(terms, TermTuple) else TermTuple(*terms)
        self.outcomes = (
            outcomes if isinstance(outcomes, TermTuple) else TermTuple(*outcomes)
        )

    def __eq__(self: Self, other: "Any") -> bool:
        """Compares the npp expression to a given object.

        Considered equal if the given object is also an `NPP` instance with same
        terms and outcomes.

        Args:
            other: `Any` instance to be compared to.

        Returns:
            Boolean indicating whether or not the npp expression is considered equal
            to the given object.
        """
        return (
            isinstance(other, NPP)
            # NOTE: order of atoms matters (corresponds to order of NPP outputs)
            and self.terms == other.terms
            and self.outcomes == other.outcomes
        )

    def __hash__(self: Self) -> int:
        return hash(("npp", self.terms, self.outcomes))

    def __str__(self: Self) -> str:
        """Returns the string representation for the npp expression.

        Returns:
            String representing the npp expression.
        """  # noqa
        return f"#npp({self.name}({str(self.terms)}),[{str(self.outcomes)}])"

    @property
    def atoms(self: Self) -> LiteralCollection:
        return LiteralCollection(
            *tuple(
                PredLiteral(self.name, *self.terms, outcome)
                for outcome in self.outcomes
            )
        )

    @cached_property
    def ground(self: Self) -> bool:
        return self.atoms.ground

    def pos_occ(self: Self) -> "LiteralCollection":
        """Positive literal occurrences.

        Returns:
            Set of `Literal` instances that occur positively in the element.
        """
        return self.atoms

    def neg_occ(self: Self) -> "LiteralCollection":
        """Negative literal occurrences.

        Returns:
            Set of `Literal` instances that occur negatively in the element.
        """
        return LiteralCollection()

    def vars(self: Self) -> Set["Variable"]:
        """Returns the variables associated with the element.

        Returns:
            A (possibly empty) set of `Variable` instances.
        """
        return self.atoms.vars()

    def global_vars(
        self: Self, statement: Optional["Statement"] = None
    ) -> Set["Variable"]:
        """Returns the global variables associated with the expression.

        Args:
            statement: Optional `Statement` instance the NPP expression appears in.
                Usually irrelevant for NPP expressions. Defaults to `None`.

        Returns:
            A (possibly empty) set of `Variable` instances.
        """
        return self.vars()

    def safety(self: Self, statement: Optional["Statement"] = None) -> SafetyTriplet:
        """Returns the the safety characterizations for the NPP expression.

        Raises an exception, since safety characterization is undefined for NPP expressions
        without additional context.

        Args:
            statement: Optional `Statement` instance the term appears in.
                Irrelevant for NPP expressions. Defaults to `None`.

        Returns:
            `SafetyTriplet` instance.

        Raises:
            ValueError: Safety characterization is undefined for NPP expressions
            without additional context.
        """  # noqa
        raise ValueError(
            "Safety characterization for NPP expressions is undefined without context."  # noqa
        )

    def substitute(self: Self, subst: "Substitution") -> "NPP":
        """Applies a substitution to the NPP expression.

        Substitutes all literals recursively.

        Args:
            subst: `Substitution` instance.

        Returns:
            `NPP` instance with (possibly substituted) terms and outcomes.
        """
        return NPP(
            self.name,
            self.terms.substitute(subst),
            self.outcomes.substitute(subst),
        )

    def match(self: Self, other: "Expr") -> Set["Substitution"]:
        """Tries to match the NPP expression with another expression.

        Raises an exception, since matching for NPP expressions is undefined.

        Args:
            other: `Expr` instance to be matched to.

        Returns:
            Optional `Substitution` instance.
        """  # noqa
        raise Exception("Matching for NPP expressions is not defined.")

    def replace_arith(self: Self, var_table: "VariableTable") -> "NPP":
        """Replaces arithmetic terms appearing in the expression with arithmetic variables.

        Note: arithmetic terms are not replaced in-place.

        Args:
            var_table: `VariableTable` instance.

        Returns:
            `NPP` instance.
        """  # noqa
        return NPP(
            self.name,
            self.terms.replace_arith(var_table),
            self.outcomes.replace_arith(var_table),
        )

    def as_choice(self: Self) -> Choice:
        """TODO"""
        return Choice(
            tuple(ChoiceElement(atom) for atom in self.atoms),
            guards=(Guard(RelOp.EQUAL, Number(1), False), None),
        )

    def __len__(self: Self) -> int:
        return len(self.outcomes)


class NPPRule(Statement):
    r"""NPP rule.

    Statement of form:
        #npp(:math:`h`(:math:`t_1`,:math:`\dots`,:math:`t_m`), [:math:`o_1`,:math:`\dots`,:math:`o_k`]) :- :math:`b_1,\dots,b_n`

    where:
        :math:`t_1,\dots,t_m` are the deterministic argument terms with :math:`m\ge0`.
        :math:`o_1,\dots,o_k` are the possible outcome terms of the neural-probabilistic predicate with :math:`k\ge0`.
        :math:`b_1,\dots,b_n` are literals with :math:`n\ge0`.

    Semantically, any answer set that includes :math:`b_1,\dots,b_n` must include exactly one of the predicate atoms
    of :math:`h`(:math:`t_1`,:math:`\dots`,:math:`t_m`,:math:`o_i`) with :math:`i\in\{0,\dots,k\}`.

    Attributes:
        npp: TODO
        literals: TODO
        head: TODO
        body: TODO
        var_table: `VariableTable` instance for the statement.
        safe: Boolean indicating whether or not the statement is considered safe.
        ground: Boolean indicating whether or not the statement is ground.
        deterministic: Boolean indicating whether or not the consequent of the rule is
            deterministic. Always `False` for NPP rules.
        contains_aggregates: Boolean indicating whether or not the statement contains
            aggregate expressions.
    """  # noqa

    def __init__(
        self: Self,
        head: NPP,
        body: Optional[Iterable["Literal"]] = None,
        *args,
        **kwargs,
    ) -> None:
        """Initializes the NPP rule instance.

        Args:
            head: `NPP` instance.
            body: Optional iterable over `Literal` instances.
                Defaults to None.
        """
        super().__init__(*args, **kwargs)

        if body is None:
            body = tuple()

        self.deterministic: bool = False

        self.npp = head
        self.literals = (
            body if isinstance(body, LiteralCollection) else LiteralCollection(*body)
        )

        self.output_key = PredLiteral(head.name, head.terms)
        self.inputs_keys = self.literals

    def __eq__(self: Self, other: "Any") -> bool:
        """Compares the statement to a given object.

        Considered equal if the given object is also an `NPPRule` instance with same NPP expression and
        body literals.

        Args:
            other: `Any` instance to be compared to.

        Returns:
            Boolean indicating whether or not the statement is considered equal to the given object.
        """  # noqa
        return (
            isinstance(other, NPPRule)
            and self.head == other.head
            and self.literals == other.literals
        )

    def __hash__(self: Self) -> int:
        return hash(("npp rule", self.head, self.literals))

    def __str__(self: Self) -> str:
        """Returns the string representation for the statement.

        Returns:
            String representing the statement.
        """
        return f"{str(self.head)}{f' :- {str(self.body)}' if self.body else ''}."

    @property
    def head(self: Self) -> NPP:
        return self.npp

    @property
    def body(self: Self) -> LiteralCollection:
        return self.literals

    @cached_property
    def safe(self: Self) -> bool:
        # TODO
        if LiteralCollection(*self.npp.vars()).safety(self) != SafetyTriplet(
            self.body.global_vars()
        ):
            return False

        return True

    @cached_property
    def ground(self: Self) -> bool:
        return self.head.ground and self.body.ground

    def consequents(self: Self) -> "LiteralCollection":
        """Returns the consequents of the statement.

        Returns:
            `LiteralCollection` instance.
        """
        return self.npp.atoms

    def antecedents(self: Self) -> "LiteralCollection":
        """Returns the antecedents of the statement.

        Returns:
            `LiteralCollection` instance.
        """
        return self.literals

    def safety(
        self: Self, statement: Optional[Union["Statement", "Query"]] = None
    ) -> "SafetyTriplet":
        raise Exception("Safety characterization for npp rules not supported yet.")

    def substitute(self: Self, subst: "Substitution") -> "NPPRule":
        """Applies a substitution to the statement.

        Substitutes the NPP expression and all literals recursively.

        Args:
            subst: `Substitution` instance.

        Returns:
            `NPPRule` instance with (possibly substituted) NPP expression and literals.
        """
        if self.ground:
            return deepcopy(self)

        return NPPRule(self.head.substitute(subst), self.body.substitute(subst))

    def replace_arith(self: Self) -> "NPPRule":
        """Replaces arithmetic terms appearing in the statement with arithmetic variables.

        Note: arithmetic terms are not replaced in-place.

        Args:
            var_table: `VariableTable` instance.

        Returns:
            `NPPRule` instance.
        """  # noqa
        return NPPRule(
            self.head.replace_arith(self.var_table),
            self.body.replace_arith(self.var_table),
        )

    def rewrite_aggregates(
        self: Self,
        aggr_counter: int,
        aggr_map: Dict[
            int,
            Tuple[
                "AggrLiteral",
                "AggrPlaceholder",
                "AggrBaseRule",
                Set["AggrElemRule"],
            ],
        ],
    ) -> "NPPRule":
        """Rewrites aggregates expressions inside the statement.

        Args:
            aggr_counter: Integer representing the current count of rewritten aggregates
                in the Program. Used as unique ids for placeholder literals.
            aggr_map: Dictionary mapping integer aggregate ids to tuples consisting of
                the original `AggrLiteral` instance replaced, the `AggrPlaceholder`
                instance replacing it in the original statement, an `AggrBaseRule`
                instance and a set of `AggrElemRule` instances representing rules for
                propagation. Pre-existing content in the dictionary is irrelevant for
                the method, the dictionary is simply updated in-place.

        Returns:
            `NPPRule` instance representing the rewritten original statement without
            any aggregate expressions.
        """

        # global variables
        glob_vars = self.global_vars()

        # group literals
        non_aggr_literals = []
        aggr_literals = []

        for literal in self.body:
            (
                aggr_literals if isinstance(literal, AggrLiteral) else non_aggr_literals
            ).append(literal)

        # mapping from original literals to alpha literals
        alpha_map = dict()

        # local import due to circular import
        from .rewrite import rewrite_aggregate

        for literal in aggr_literals:
            # rewrite aggregate literal
            alpha_literal, eps_rule, eta_rules = rewrite_aggregate(
                literal, aggr_counter, glob_vars, non_aggr_literals
            )

            # map original aggregate literal to new alpha literal
            alpha_map[literal] = alpha_literal

            # store aggregate information
            aggr_map[aggr_counter] = (literal, alpha_literal, eps_rule, eta_rules)

            # increase aggregate counter
            aggr_counter += 1

        # replace original rule with modified one
        alpha_rule = NPPRule(
            self.npp,
            tuple(
                alpha_map[literal] if isinstance(literal, AggrLiteral) else literal
                for literal in self.body
            ),  # NOTE: restores original order of literals
        )

        return alpha_rule

    def assemble_aggregates(
        self: Self, assembling_map: Dict["AggrPlaceholder", "AggrLiteral"]
    ) -> "NPPRule":
        """Reassembles rewritten aggregates expressions inside the statement.

        Args:
            assembling_map: Dictionary mapping `AggrPlaceholder` instances to
                `AggrLiteral` instances to be replaced with.

        Returns:
            `NPPRule` instance representing the reassembled original statement.
        """
        return NPPRule(
            self.npp,
            tuple(
                literal if literal not in assembling_map else assembling_map[literal]
                for literal in self.body
            ),
        )

    @cached_property
    def is_fact(self: Self) -> bool:
        return bool(self.literals)

    def powerset(
        self: Self,
    ) -> List[Tuple[int, ...]]:
        """TODO"""

        # return all possible outcomes once
        return [(i,) for i in range(len(self.npp))]
