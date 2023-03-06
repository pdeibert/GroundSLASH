from copy import deepcopy
from functools import cached_property
from typing import TYPE_CHECKING, Dict, Optional, Set, Tuple, Union

import aspy
from aspy.program.literals import (
    AggregateLiteral,
    AlphaLiteral,
    LiteralTuple,
    PredicateLiteral,
)
from aspy.program.safety_characterization import SafetyTriplet

from .normal import NormalFact, NormalRule
from .statement import Fact, Rule

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.expression import Expr
    from aspy.program.literals import Literal
    from aspy.program.statements import EpsRule, EtaRule, Statement
    from aspy.program.substitution import Substitution
    from aspy.program.terms import Variable


class DisjunctiveFact(Fact):
    """Disjunctive fact.

    Rule of form

        h_1 | ... | h_m :- .

    for classical atoms h_1,...,h_m. The symbol ':-' may be omitted.

    Semantically, any answer set must include exactly one classical atom h_i.
    """

    deterministic: bool = False

    def __init__(self, *atoms: PredicateLiteral, **kwargs) -> None:
        super().__init__(**kwargs)

        if len(atoms) < 2:
            raise ValueError(f"Head for {type(self)} requires at least two literals. Use {NormalFact} instead.")

        if aspy.debug() and not all(isinstance(atom, PredicateLiteral) and not atom.naf for atom in atoms):
            raise ValueError(
                f"Head literals for {type(self)} must all be positive literals of type {PredicateLiteral}."
            )

        self.atoms = LiteralTuple(*atoms)

    def __eq__(self, other: "Expr") -> bool:
        return isinstance(other, DisjunctiveFact) and self.atoms == other.atoms

    def __hash__(self) -> int:
        return hash(("disjunctive fact", self.atoms))

    def __str__(self) -> str:
        return f"{' | '.join([str(atom) for atom in self.head])}."

    @property
    def head(self) -> LiteralTuple:
        return self.atoms

    @property
    def body(self) -> LiteralTuple:
        return LiteralTuple()

    def safety(self, rule: Optional["Statement"], global_vars: Optional[Set["Variable"]] = None) -> "SafetyTriplet":
        raise Exception()

    @cached_property
    def safe(self) -> bool:
        return len(self.vars()) == 0

    @cached_property
    def ground(self) -> bool:
        return self.head.ground

    def substitute(self, subst: "Substitution") -> "DisjunctiveFact":
        if self.ground:
            return deepcopy(self)

        return DisjunctiveFact(*self.head.substitute(subst))


class DisjunctiveRule(Rule):
    """Disjunctive rule.

    Rule of form:

        h_1 | ... | h_m :- b_1,...,b_n .

    for classical atoms h_1,...,h_m and literals b_1,...,b_n.

    Semantically, any answer set that includes b_1,...,b_n must also include exactly one h_i.
    """

    deterministic: bool = False

    def __init__(
        self,
        head: Union[LiteralTuple, Tuple["Literal", ...]],
        body: Union[LiteralTuple, Tuple["Literal", ...]],
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        if len(head) < 2:
            raise ValueError(f"Head for {type(self)} requires at least two literals. Use {NormalRule} instead.")
        if len(body) == 0:
            raise ValueError(f"Body for {type(self)} may not be empty. Use {DisjunctiveFact} instead.")

        if aspy.debug() and not all(isinstance(atom, PredicateLiteral) and not atom.naf for atom in head):
            raise ValueError(
                f"Head literals for {type(self)} must all be positive literals of type {PredicateLiteral}."
            )

        self.atoms = head if isinstance(head, LiteralTuple) else LiteralTuple(*head)
        self.literals = body if isinstance(body, LiteralTuple) else LiteralTuple(*body)

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, DisjunctiveRule)
            and set(self.atoms) == set(other.atoms)
            and set(self.literals) == set(other.literals)
        )

    def __hash__(self) -> int:
        return hash(("disjunctive rule", frozenset(self.atoms), frozenset(self.literals)))

    def __str__(self) -> str:
        return (
            f"{' | '.join([str(atom) for atom in self.head])} :- {', '.join([str(literal) for literal in self.body])}."
        )

    @property
    def head(self) -> LiteralTuple:
        return self.atoms

    @property
    def body(self) -> LiteralTuple:
        return self.literals

    @cached_property
    def safe(self) -> bool:
        global_vars = self.vars(global_only=True)
        body_safety = SafetyTriplet.closure(*self.body.safety(global_vars=global_vars))

        return body_safety == SafetyTriplet(global_vars)

    @cached_property
    def ground(self) -> bool:
        return self.head.ground and self.body.ground

    def substitute(self, subst: "Substitution") -> "DisjunctiveRule":
        if self.ground:
            return deepcopy(self)

        return DisjunctiveRule(self.head.substitute(subst), self.literals.substitute(subst))

    def rewrite_aggregates(
        self,
        aggr_counter: int,
        aggr_map: Dict[int, Tuple["AggregateLiteral", "AlphaLiteral", "EpsRule", Set["EtaRule"]]],
    ) -> "DisjunctiveRule":

        # global variables
        glob_vars = self.vars(global_only=True)

        # group literals
        non_aggr_literals = []
        aggr_literals = []

        for literal in self.body:
            (aggr_literals if isinstance(literal, AggregateLiteral) else non_aggr_literals).append(literal)

        # mapping from original literals to alpha literals
        alpha_map = dict()

        # local import due to circular import
        from .rewrite import rewrite_aggregate

        for literal in aggr_literals:
            # rewrite aggregate literal
            alpha_literal, eps_rule, eta_rules = rewrite_aggregate(literal, aggr_counter, glob_vars, non_aggr_literals)

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
                alpha_map[literal] if isinstance(literal, AggregateLiteral) else literal for literal in self.body
            ),  # NOTE: restores original order of literals
        )

        return alpha_rule

    def assemble_aggregates(self, assembling_map: Dict["AlphaLiteral", "AggregateLiteral"]) -> "DisjunctiveRule":
        return DisjunctiveRule(
            deepcopy(self.atoms),
            tuple(literal if literal not in assembling_map else assembling_map[literal] for literal in self.body),
        )
