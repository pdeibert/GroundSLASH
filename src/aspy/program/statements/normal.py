from typing import Tuple, Set, Dict, Optional, TYPE_CHECKING
from functools import cached_property
from collections import deque
from copy import deepcopy

from aspy.program.symbol_table import SymbolTable, SpecialChar
from aspy.program.variable_table import VariableTable
from aspy.program.literals import Equal, Naf, LiteralTuple, AggregateLiteral, PredicateLiteral, BuiltinLiteral, AlphaLiteral
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.substitution import AssignmentError

from .statement import Fact, Rule

if TYPE_CHECKING:
    from aspy.program.expression import Expr
    from aspy.program.substitution import Substitution
    from aspy.program.literals import PredicateLiteral, Literal, AlphaLiteral
    from aspy.program.terms import Variable
    from aspy.program import Program
    from .special import EpsRule, EtaRule

class NormalFact(Fact):
    """Normal fact.

    Rule of form

        h :- .

    for a classical atom h. The symbol ':-' may be omitted.

    Semantically, any answer set must include h.
    """
    def __init__(self, atom: "PredicateLiteral", **kwargs) -> None:
        super().__init__(**kwargs)

        self.atom = atom

    def __str__(self) -> str:
        return f"{str(self.atom)}."

    def __eq__(self, other: "Expr") -> bool:
        return isinstance(other, NormalFact) and self.atom == other.atom

    def __hash__(self) -> int:
        return hash( ("normal fact", self.atom) )

    @property
    def head(self) -> LiteralTuple:
        return LiteralTuple(self.atom)

    @property
    def body(self) -> LiteralTuple:
        return LiteralTuple()

    @cached_property
    def safe(self) -> bool:
        return len(self.vars()) == 0

    @cached_property
    def ground(self) -> bool:
        return self.atom.ground

    def substitute(self, subst: "Substitution") -> "NormalFact":
        if self.ground:
            return deepcopy(self)

        return NormalFact(self.atom.substitute(subst))

    def match(self, other: "Expr") -> Optional["Substitution"]:
        if not isinstance(other, NormalFact):
            return None

        # match head
        match = self.atom.match(other.atom)

        if match is None:
            return None

        return match

    def replace_arith(self) -> "NormalFact":
        return NormalFact(self.atom.replace_arith(self.var_table))


class NormalRule(Rule):
    """Normal rule.

    Rule of form:

        h :- b_1, ..., b_n .

    for a classical atom h and literals b_1,...,b_n.

    Semantically, any answer set that includes b_1,...,b_n must also include h.
    """
    def __init__(self, head: "PredicateLiteral", *body: "Literal", **kwargs) -> None:
        super().__init__(**kwargs)

        if len(body) == 0:
            raise ValueError(f"Body for {type(self)} may not be empty.")

        self.atom = head
        self.literals = LiteralTuple(*body)

    def __eq__(self, other: "Expr") -> bool:
        return isinstance(other, NormalRule) and self.atom == other.atom and self.literals == other.literals

    def __hash__(self) -> int:
        return hash( ("normal rule", self.atom, self.literals) )

    def __str__(self) -> str:
        return f"{str(self.atom)} :- {', '.join([str(literal) for literal in self.body])}."

    @property
    def head(self) -> LiteralTuple:
        return LiteralTuple(self.atom)

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
        return self.atom.ground and self.body.ground

    def substitute(self, subst: "Substitution") -> "NormalRule":
        if self.ground:
            return deepcopy(self)

        return NormalRule(self.atom.substitute(subst), *self.literals.substitute(subst))

    def match(self, other: "Expr") -> Optional["Substitution"]:
        # TODO: so far can only match body literals in order
        if not isinstance(other, NormalRule):
            return None

        # match head
        match = self.atom.match(other.atom)

        if match is None:
            return None
        subst = match

        # match body
        match = self.body.match(other.body)

        if match is None:
            return None

        # combine substitutions
        try:
            subst = subst + match
        except AssignmentError:
            return None

        return subst

    def replace_arith(self) -> "NormalRule":
        return NormalRule(self.atom.replace_arith(self.var_table), *self.literals.replace_arith(self.var_table))

    def rewrite(self):
        pass

    def rewrite_aggregates(self, aggr_counter: int, aggr_map: Dict[int, Tuple["AggregateLiteral", "AlphaLiteral", "EpsRule", Set["EtaRule"]]]) -> "NormalRule":
        if self.ground:
            return deepcopy(self)

        # global variables
        glob_vars = self.vars(global_only=True)

        # group literals
        non_aggr_literals = []
        aggr_literals = []

        for literal in self.body:
            (aggr_literals if isinstance(AggregateLiteral) else non_aggr_literals).append(literal)

        # mapping from original literals to alpha literals
        alpha_map = dict()
        # mapping from aggregate ID to corresponding alpha literal, epsilon rule and eta rules
        aggr_map = dict()

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
        alpha_rule = NormalRule(
            self.head,
            LiteralTuple(tuple(alpha_map[literal] if isinstance(literal, AggregateLiteral) else literal for literal in self.body)) # NOTE: restores original order of literals
        )

        return alpha_rule, aggr_map