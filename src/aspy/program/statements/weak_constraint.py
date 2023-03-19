from copy import deepcopy
from functools import cached_property
from typing import TYPE_CHECKING, Dict, Iterable, Optional, Set, Tuple

from aspy.program.expression import Expr
from aspy.program.literals import (
    AggrLiteral,
    AggrPlaceholder,
    Literal,
    LiteralCollection,
)
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.statements import AggrBaseRule, AggrElemRule
from aspy.program.terms import TermTuple
from aspy.program.variable_table import VariableTable

from .statement import Statement

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

    from aspy.program.substitution import Substitution
    from aspy.program.terms import Term, Variable


class WeightAtLevel(Expr):
    """TODO"""

    def __init__(
        self, weight: "Term", level: "Term", terms: Optional[Iterable["Term"]] = None
    ) -> None:
        if terms is None:
            terms = tuple()

        self.weight = weight
        self.level = level
        self.terms = TermTuple(*terms) if not isinstance(terms, TermTuple) else terms

    def __str__(self) -> str:
        return f"{str(self.weight)}@{str(self.level)}, {str(self.terms)}"

    def __eq__(self, other: "Any") -> bool:
        return (
            isinstance(other, WeightAtLevel)
            and self.weight == other.weight
            and self.level == other.level
            and self.terms == other.terms
        )

    def __hash__(self) -> int:
        return hash(("weight at level", self.weight, self.level, self.terms))

    @cached_property
    def ground(self) -> bool:
        return (
            self.weight.ground
            and self.level.ground
            and all(term.ground for term in self.terms)
        )

    def vars(self) -> Set["Variable"]:
        """Returns the variables associated with the expression.

        Returns:
            (Possibly empty) set of 'Variable' instances as union of the variables of all terms.
        """  # noqa
        return set().union(
            self.weight.vars(),
            self.level.vars(),
            self.terms.vars(),
        )

    def global_vars(self, statement: Optional["Statement"] = None) -> Set["Variable"]:
        """Returns the global variables associated with the expression.

        Args:
            statement: Optional `Statement` or `Query` instance the term appears in.
                Irrelevant for this expression. Defaults to `None`.

        Returns:
            (Possibly empty) set of 'Variable' instances as union of the (global) variables of all terms.
        """  # noqa
        return set().union(
            self.weight.global_vars(),
            self.level.global_vars(),
            self.terms.global_vars(),
        )

    def safety(self, rule: Optional["Statement"]) -> "SafetyTriplet":
        raise Exception(
            "Safety characterization for weight at level not supported yet."
        )

    def substitute(self, subst: "Substitution") -> "WeightAtLevel":
        if self.ground:
            return deepcopy(self)

        return WeightAtLevel(
            self.weight.substitute(subst),
            self.level.substitute(subst),
            self.terms.substitute(subst),
        )

    def replace_arith(self, var_table: "VariableTable") -> "TermTuple":
        """Replaces arithmetic terms appearing in the term tuple with arithmetic variables.

        Note: arithmetic terms are not replaced in-place.

        Args:
            var_table: `VariableTable` instance.

        Returns:
            `TermTuple` instance.
        """  # noqa
        return WeightAtLevel(
            self.weight.replace_arith(var_table),
            self.level.replace_arith(var_table),
            self.terms.replace_arith(var_table),
        )


class WeakConstraint(Statement):
    """Weak constraint.

    Statement of form:

        :~ b_1,...,b_n . [ w@l,t_1,...,t_m ]

    for literals b_1,...,b_n and terms w,l,t_1,...,t_m.
    '@ l' may be omitted if l=0.

    Attributes:
        head:
        body:
        literals
        weight_at_level
    """

    deterministic: bool = True  # TODO: correct?

    def __init__(
        self,
        literals: Iterable["Literal"],
        weight_at_level: "WeightAtLevel",
    ) -> None:
        super().__init__()

        self.literals = (
            LiteralCollection(*literals)
            if not isinstance(literals, LiteralCollection)
            else literals
        )
        self.weight_at_level = weight_at_level

    def __eq__(self, other: "Any") -> bool:
        return (
            isinstance(other, WeakConstraint)
            and self.literals == other.literals
            and self.weight_at_level == other.weight_at_level
        )

    def __hash__(self) -> int:
        return hash(("weak constraint", self.literals, self.weight_at_level))

    def __str__(self) -> str:
        return f":~ {str(self.body)}. [{str(self.weight_at_level)}]"

    def __init_var_table(self) -> None:

        # initialize variable table
        self.__var_table = VariableTable(
            self.literals.vars().union(self.weight_at_level.vars())
        )

        # mark global variables
        self.__var_table.update(
            {
                var: True
                for var in self.head.global_vars(self).union(
                    self.weight_at_level.global_vars()
                )
            }
        )

    @property
    def head(self) -> LiteralCollection:
        return LiteralCollection()

    @property
    def body(self) -> LiteralCollection:
        return self.literals

    @cached_property
    def safe(self) -> bool:
        return self.body.safety(self) == SafetyTriplet(self.global_vars())

    @cached_property
    def ground(self) -> bool:
        return self.weight_at_level.ground and all(
            literal.ground for literal in self.literals
        )

    @cached_property
    def contains_aggregates(self) -> bool:
        return any(isinstance(literal, AggrLiteral) for literal in self.literals)

    def substitute(self, subst: "Substitution") -> "WeakConstraint":
        if self.ground:
            return deepcopy(self)

        return WeakConstraint(
            self.literals.substitute(subst),
            self.weight_at_level.substitute(subst),
        )

    def rewrite_aggregates(
        self,
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
    ) -> "WeakConstraint":

        # global variables
        glob_vars = self.global_vars(self)

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
        alpha_rule = WeakConstraint(
            tuple(
                alpha_map[literal] if isinstance(literal, AggrLiteral) else literal
                for literal in self.body
            ),  # NOTE: restores original order of literals
            self.weight_at_level,
        )

        return alpha_rule

    def assemble_aggregates(
        self, assembling_map: Dict["AggrPlaceholder", "AggrLiteral"]
    ) -> "WeakConstraint":
        return WeakConstraint(
            tuple(
                literal if literal not in assembling_map else assembling_map[literal]
                for literal in self.body
            ),
            self.weight_at_level,
        )

    def replace_arith(self, var_table: "VariableTable") -> "TermTuple":
        """Replaces arithmetic terms appearing in the term tuple with arithmetic variables.

        Note: arithmetic terms are not replaced in-place.

        Args:
            var_table: `VariableTable` instance.

        Returns:
            `TermTuple` instance.
        """  # noqa
        return WeakConstraint(
            self.literals.replace_arith(var_table),
            self.weight_at_level.replace_arith(var_table),
        )
