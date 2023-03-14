from copy import deepcopy
from functools import cached_property
from typing import TYPE_CHECKING, Dict, Set, Tuple, Union

from aspy.program.literals import (
    AggrLiteral,
    AggrPlaceholder,
    LiteralTuple,
    PredLiteral,
)
from aspy.program.safety_characterization import SafetyTriplet

from .constraint import Constraint
from .statement import Fact, Rule

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.expression import Expr
    from aspy.program.literals import Literal
    from aspy.program.literals.special import ChoicePlaceholder
    from aspy.program.substitution import Substitution

    from .choice import Choice, ChoiceFact, ChoiceRule
    from .special import AggrBaseRule, AggrElemRule


class NormalFact(Fact):
    """Normal fact.

    Rule of form

        h :- .

    for a classical atom h. The symbol ':-' may be omitted.

    Semantically, any answer set must include h.
    """

    deterministic: bool = True

    def __init__(self, atom: "PredLiteral", **kwargs) -> None:
        super().__init__(**kwargs)

        self.atom = atom

    def __str__(self) -> str:
        return f"{str(self.atom)}."

    def __eq__(self, other: "Expr") -> bool:
        return isinstance(other, NormalFact) and self.atom == other.atom

    def __hash__(self) -> int:
        return hash(("normal fact", self.atom))

    @property
    def head(self) -> LiteralTuple:
        return LiteralTuple(self.atom)

    @property
    def body(self) -> LiteralTuple:
        return LiteralTuple()

    @cached_property
    def safe(self) -> bool:
        return self.body.safety(self) == SafetyTriplet(self.global_vars())

    @cached_property
    def ground(self) -> bool:
        return self.atom.ground

    def substitute(self, subst: "Substitution") -> "NormalFact":
        if self.ground:
            return deepcopy(self)

        return NormalFact(self.atom.substitute(subst))

    def replace_arith(self) -> "NormalFact":
        return NormalFact(self.atom.replace_arith(self.var_table))

    def assemble_choices(
        self,
        assembling_map: Dict["ChoicePlaceholder", "Choice"],
    ) -> Union["NormalFact", "ChoiceFact"]:
        # local import to avoid circular imports
        from aspy.program.literals.special import ChoicePlaceholder

        from .choice import ChoiceFact

        # choice rule
        if isinstance(self.atom, ChoicePlaceholder):
            # satisfiable (instantiate choice rule)
            if self.atom in assembling_map:
                return ChoiceFact(assembling_map[self.atom])
            # unsatisfiable (instantiate constraint)
            else:
                return Constraint()

        # non-choice rule (nothing to be done here)
        return deepcopy(self)


class NormalRule(Rule):
    """Normal rule.

    Rule of form:

        h :- b_1, ..., b_n .

    for a classical atom h and literals b_1,...,b_n.

    Semantically, any answer set that includes b_1,...,b_n must also include h.
    """

    deterministic: bool = True

    def __init__(self, head: "PredLiteral", *body: "Literal", **kwargs) -> None:
        super().__init__(**kwargs)

        if len(body) == 0:
            raise ValueError(
                f"Body for {type(self)} may not be empty. Use {NormalFact} instead."
            )

        self.atom = head
        self.literals = LiteralTuple(*body)

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, NormalRule)
            and self.atom == other.atom
            and set(self.literals) == set(other.literals)
        )

    def __hash__(self) -> int:
        return hash(("normal rule", self.atom, self.literals))

    def __str__(self) -> str:
        return (
            f"{str(self.atom)} :- {', '.join([str(literal) for literal in self.body])}."
        )

    @property
    def head(self) -> LiteralTuple:
        return LiteralTuple(self.atom)

    @property
    def body(self) -> LiteralTuple:
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
