from copy import deepcopy
from functools import cached_property
from typing import TYPE_CHECKING, Any, Dict, Optional, Set, Tuple, Union

import aspy
from aspy.program.literals import (
    AggrLiteral,
    AggrPlaceholder,
    LiteralCollection,
    PredLiteral,
)
from aspy.program.safety_characterization import SafetyTriplet

from .statement import Statement
from .normal import NormalRule

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.literals import Literal
    from aspy.program.statements import AggrBaseRule, AggrElemRule
    from aspy.program.substitution import Substitution


class DisjunctiveRule(Statement):
    """Disjunctive rule.

    Rule of form:

        h_1 | ... | h_m :- b_1,...,b_n .

    for classical atoms h_1,...,h_m and literals b_1,...,b_n.

    Semantically, any answer set that includes b_1,...,b_n must also include exactly one h_i.
    """  # noqa

    deterministic: bool = False

    def __init__(
        self,
        head: Union[LiteralCollection, Tuple["Literal", ...]],
        body: Optional[Union[LiteralCollection, Tuple["Literal", ...]]] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        if body is None:
            body = tuple()

        if len(head) < 2:
            raise ValueError(
                (
                    f"Head for {type(self)} requires at least two literals."
                    " Use {NormalRule} instead."
                )
            )

        if aspy.debug() and not all(
            isinstance(atom, PredLiteral) and not atom.naf for atom in head
        ):
            raise ValueError(
                (
                    f"Head literals for {type(self)} must all be"
                    " positive literals of type {PredLiteral}."
                )
            )

        self.atoms = (
            head if isinstance(head, LiteralCollection) else LiteralCollection(*head)
        )
        self.literals = (
            body if isinstance(body, LiteralCollection) else LiteralCollection(*body)
        )

    def __eq__(self, other: "Any") -> bool:
        return (
            isinstance(other, DisjunctiveRule)
            and set(self.atoms) == set(other.atoms)
            and set(self.literals) == set(other.literals)
        )

    def __hash__(self) -> int:
        return hash(
            ("disjunctive rule", frozenset(self.atoms), frozenset(self.literals))
        )

    def __str__(self) -> str:
        return f"{' | '.join([str(atom) for atom in self.head])}{f' :- {str(self.body)}' if self.body else ''}."  # noqa

    @property
    def head(self) -> LiteralCollection:
        return self.atoms

    @property
    def body(self) -> LiteralCollection:
        return self.literals

    @cached_property
    def safe(self) -> bool:
        return self.body.safety(self) == SafetyTriplet(self.global_vars())

    @cached_property
    def ground(self) -> bool:
        return self.head.ground and self.body.ground

    def substitute(
        self, subst: "Substitution"
    ) -> Union["DisjunctiveRule", "NormalRule"]:
        if self.ground:
            return deepcopy(self)

        subst_head = self.head.substitute(subst)

        if len(set(subst_head)) == 1:
            return NormalRule(*subst_head, *self.literals.substitute(subst))

        return DisjunctiveRule(subst_head, self.literals.substitute(subst))

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
    ) -> "DisjunctiveRule":

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
        alpha_rule = DisjunctiveRule(
            deepcopy(self.atoms),
            tuple(
                alpha_map[literal] if isinstance(literal, AggrLiteral) else literal
                for literal in self.body
            ),  # NOTE: restores original order of literals
        )

        return alpha_rule

    def assemble_aggregates(
        self, assembling_map: Dict["AggrPlaceholder", "AggrLiteral"]
    ) -> "DisjunctiveRule":
        return DisjunctiveRule(
            deepcopy(self.atoms),
            tuple(
                literal if literal not in assembling_map else assembling_map[literal]
                for literal in self.body
            ),
        )

    def replace_arith(self) -> "DisjunctiveRule":
        return DisjunctiveRule(
            self.head.replace_arith(self.var_table),
            self.body.replace_arith(self.var_table),
        )
