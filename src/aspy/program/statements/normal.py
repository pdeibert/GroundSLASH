from typing import Optional, Tuple, Union, Set, TYPE_CHECKING
from copy import deepcopy
from functools import cached_property

from aspy.program.symbol_table import CHAR_ALPHA, CHAR_EPS, CHAR_ETA
from aspy.program.literals import LiteralTuple, AggregateLiteral, PredicateLiteral, BuiltinLiteral

from .statement import Fact, Rule

if TYPE_CHECKING:
    from aspy.program.expression import Expr
    from aspy.program.substitution import Substitution
    from aspy.program.literals import PredicateLiteral, Literal
    from aspy.program.terms import Variable
    from aspy.program.safety_characterization import SafetyTriplet

    from .statement import Statement


class NormalFact(Fact):
    """Normal fact.

    Rule of form

        h :- .

    for a classical atom h. The symbol ':-' may be omitted.

    Semantically, any answer set must include h.
    """
    def __init__(self, atom: "PredicateLiteral") -> None:
        self.atom = atom
        self.ground = atom.ground

    def __str__(self) -> str:
        return f"{str(self.atom)}."

    @property
    def head(self) -> LiteralTuple:
        return LiteralTuple([self.atom])

    @property
    def body(self) -> LiteralTuple:
        return LiteralTuple()

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return self.atom.vars(global_only)

    def safety(self, rule: Optional["Statement"]=None, global_vars: Optional[Set["Variable"]]=None) -> "SafetyTriplet":
        raise Exception()

    @cached_property
    def safe(self) -> bool:
        return len(self.vars()) > 0

    def substitute(self, subst: "Substitution") -> "NormalFact":
        return NormalFact(self.atom.substitute(subst))

    """
    def rewrite(self) -> Tuple["NormalFact"]:
        return (deepcopy(self), )
    """

    def match(self, other: "Expr") -> Set["Substitution"]:
        raise Exception("Matching for normal facts not supported yet.")


class NormalRule(Rule):
    """Normal rule.

    Rule of form:

        h :- b_1, ..., b_n .

    for a classical atom h and literals b_1,...,b_n.

    Semantically, any answer set that includes b_1,...,b_n must also include h.
    """
    def __init__(self, head: "PredicateLiteral", body: Union[LiteralTuple, Tuple["Literal", ...]]) -> None:
        self.atom = head
        self.literals = body if isinstance(body, LiteralTuple) else LiteralTuple(body)
        self.ground = self.atom.ground and self.body.ground

    def __str__(self) -> str:
        return f"{str(self.atom)} :- {', '.join([str(literal) for literal in self.body])}."

    @property
    def head(self) -> LiteralTuple:
        return LiteralTuple([self.atom])

    @property
    def body(self) -> LiteralTuple:
        return self.literals

    @cached_property
    def safe(self) -> bool:
        global_vars = self.vars(global_only=True)
        body_safety = SafetyTriplet.closure(self.body.safety(global_vars=global_vars))

        return body_safety == SafetyTriplet(global_vars)

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return set().union(self.atom.vars(), *self.body.vars(global_only))

    def safety(self, rule: Optional["Statement"]=None, global_vars: Optional[Set["Variable"]]=None) -> "SafetyTriplet":
        raise Exception()

    def substitute(self, subst: "Substitution") -> "NormalRule":
        return NormalRule(self.atom.substitute(subst), self.literals.substitute(subst))

    def match(self, other: "Expr") -> Set["Substitution"]:
        raise Exception("Matching for normal rules not supported yet.")

    """
    def rewrite(self) -> Tuple["NormalRule"]:
        # TODO: What else to rewrite ??? (see mu-gringo) 
        # TODO: how does this translate to disjunctive or choice rules ????? same ?????

        rules = []

        non_aggr_literals = []
        aggr_literals = []
        replacement_literals = []

        for literal in self.body:
            if isinstance(literal, AggregateLiteral):
                aggr_literals.append(literal)
            else:
                non_aggr_literals.append(literal)

        
        for aggr in aggr_literals:
            vars = set()
            n = len(vars) # TODO: compute arity (number of global variables occurring in aggregate)

            # ----- create atom for aggregate occurrence -----
            alpha_symbol = self.sym_table.register(CHAR_ALPHA, n)
            replacement_literals.append(PredicateLiteral(alpha_symbol, vars, aggr.naf))

            # ----- epsilon rule -----
            eps_symbol = self.sym_table.register(CHAR_EPS, n)
            guard_literals = []

            # handle left guard
            if literal.lcomp is not None:
                op, term = aggr.lcomp

                # TODO: get value for empty set()
                val = None
                guard_literals.append(op.to_literal(term, val))
            if literal.rcomp is not None:
                op, term = aggr.rcomp

                # TODO: get value for empty set()
                val = None
                guard_literals.append(op.to_literal(val, term))
            # TODO: defaults? see mu-gringo!
            else:
                raise Exception()

            rules.append(
                NormalRule(
                    PredicateLiteral(eps_symbol, vars),
                    LiteralTuple(guard_literals + non_aggr_literals)
                )
            )

            # ----- eta rules -----
            for element in aggr.func.elements:
                eta_symbol = self.sym_table.register(CHAR_ETA, n + len(element.head))

                rules.append(
                    NormalRule(
                        PredicateLiteral(eta_symbol, element.head + vars),
                        LiteralTuple(element.body + non_aggr_literals)
                    )
                )
    
        # ----- replace original rule with modified rule -----
        rules.append(
            NormalRule(
                self.head,
                LiteralTuple(non_aggr_literals + replacement_literals)
            )
        )

        return rules

    def match(self):
        pass
    """