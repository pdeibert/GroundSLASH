from copy import deepcopy
from functools import cached_property
from typing import TYPE_CHECKING, Any, Dict, Set, Tuple, Union

from aspy.program.literals import (
    AggrLiteral,
    AggrPlaceholder,
    LiteralCollection,
    PredLiteral,
)
from aspy.program.safety_characterization import SafetyTriplet

from .statement import Statement
from .constraint import Constraint

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.literals import Literal
    from aspy.program.literals.special import ChoicePlaceholder
    from aspy.program.substitution import Substitution

    from .choice import Choice, ChoiceRule
    from .special import AggrBaseRule, AggrElemRule


class NormalRule(Statement):
    """Normal rule.

    Rule of form:

        h :- b_1, ..., b_n .

    for a classical atom h and literals b_1,...,b_n.

    Semantically, any answer set that includes b_1,...,b_n must also include h.
    """

    deterministic: bool = True

    def __init__(self, atom: "PredLiteral", *body: "Literal", **kwargs) -> None:
        super().__init__(**kwargs)

        self.atom = atom
        self.literals = LiteralCollection(*body)

    def __eq__(self, other: "Any") -> bool:
        return (
            isinstance(other, NormalRule)
            and self.atom == other.atom
            and set(self.literals) == set(other.literals)
        )

    def __hash__(self) -> int:
        return hash(("normal rule", self.atom, self.literals))

    def __str__(self) -> str:
        return f"{str(self.atom)}{f' :- {str(self.body)}' if self.body else ''}."

    @property
    def head(self) -> LiteralCollection:
        return LiteralCollection(self.atom)

    @property
    def body(self) -> LiteralCollection:
        return self.literals

    @cached_property
    def safe(self) -> bool:
        return self.body.safety(self) == SafetyTriplet(self.global_vars())

    @cached_property
    def ground(self) -> bool:
        return self.atom.ground and self.body.ground

    def substitute(self, subst: "Substitution") -> "NormalRule":
        if self.ground:
            return deepcopy(self)

        return NormalRule(self.atom.substitute(subst), *self.literals.substitute(subst))

    def replace_arith(self) -> "NormalRule":
        return NormalRule(
            self.atom.replace_arith(self.var_table),
            *self.literals.replace_arith(self.var_table),
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
    ) -> "NormalRule":

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
        alpha_rule = NormalRule(
            self.atom,
            *tuple(
                alpha_map[literal] if isinstance(literal, AggrLiteral) else literal
                for literal in self.body
            ),  # NOTE: restores original order of literals
        )

        return alpha_rule

    def assemble_aggregates(
        self, assembling_map: Dict["AggrPlaceholder", "AggrLiteral"]
    ) -> "NormalRule":
        return NormalRule(
            self.atom,
            *tuple(
                literal if literal not in assembling_map else assembling_map[literal]
                for literal in self.body
            ),
        )

    def assemble_choices(
        self,
        assembling_map: Dict["ChoicePlaceholder", "Choice"],
    ) -> Union["NormalRule", "ChoiceRule"]:
        # local import to avoid circular imports
        from aspy.program.literals.special import ChoicePlaceholder

        from .choice import ChoiceRule

        # choice rule
        if isinstance(self.atom, ChoicePlaceholder):
            # satisfiable (instantiate choice rule)
            if self.atom in assembling_map:
                return ChoiceRule(assembling_map[self.atom], self.body)
            # unsatisfiable (instantiate constraint)
            else:
                return Constraint(*self.body)

        # non-choice rule (nothing to be done here)
        return deepcopy(self)
