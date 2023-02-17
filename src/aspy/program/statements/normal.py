from typing import Tuple, Set, TYPE_CHECKING
from functools import cached_property
from collections import deque
from copy import deepcopy

from aspy.program.symbol_table import SymbolTable, SpecialChar
from aspy.program.variable_table import VariableTable
from aspy.program.literals import Naf, LiteralTuple, AggregateLiteral, PredicateLiteral, BuiltinLiteral
from aspy.program.terms import ArithVariable
from aspy.program.safety_characterization import SafetyTriplet

from .statement import Fact, Rule

if TYPE_CHECKING:
    from aspy.program.expression import Expr
    from aspy.program.substitution import Substitution
    from aspy.program.literals import PredicateLiteral, Literal
    from aspy.program.terms import Variable


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
        return NormalFact(self.atom.substitute(subst))

    def match(self, other: "Expr") -> Set["Substitution"]:
        raise Exception("Matching for normal facts not supported yet.")


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
            raise ValueError(f"Body for {type(NormalRule)} may not be empty.")

        self.atom = head
        self.literals = LiteralTuple(*body)

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
        return NormalRule(self.atom.substitute(subst), self.literals.substitute(subst))

    def match(self, other: "Expr") -> Set["Substitution"]:
        raise Exception("Matching for normal rules not supported yet.")

    def rewrite(self, sym_table: SymbolTable) -> Tuple["Rule"]:

        if self.ground:
            return deepcopy(self)

        # make a copy of the current variable table
        var_table = deepcopy(self.var_table)

        # first replace all non-ground arithmetic terms with new variables
        rule = NormalRule(self.atom.replace_arith(var_table), self.body.replace_arith(var_table))

        # TODO: better use for variable table?

        # global variables
        glob_vars = self.vars(global_only=True)

        # get arithmetic variables
        arith_vars = set(var for var in self.var_table.vars if isinstance(var, ArithVariable))

        # group literals
        non_aggr_literals = []
        aggr_literals = []

        for literal in self.body:
            (aggr_literals if isinstance(AggregateLiteral) else non_aggr_literals).append(literal)

        rules = deque()
        # map aggregate literals to replacement predicate literals
        aggr_map = dict()

        # TODO: rewrite all arithmetic terms first!!!
        # -> therefore iterate over all literals
        # TODO: how to check for arithmetic literals?
        for literal in self.body:
            pass

        # rewrite all aggregate literals
        for literal in aggr_literals:
            # rewrite all aggregate literal

            # get global variables occurring in aggregate
            # TODO: is outvars enough?
            aggr_glob_vars = glob_vars.intersection(literal.vars())

            n = len(aggr_glob_vars)

            # ----- create predicate literal for each aggregate occurrence -----
            alpha_symbol = sym_table.create(SpecialChar.ALPHA, n)
            # append to rewritten literals (not only at end???)
            new_literal = PredicateLiteral(alpha_symbol, vars)

            if literal.naf:
                new_literal = Naf(new_literal)

            aggr_map[literal].append(new_literal)

            # ----- epsilon rule -----
            eps_symbol = sym_table.create(SpecialChar.EPS, n)

            # process guards
            guard_literals = []
            # get base value (aggregate value for empty set of aggregate elements)
            base_val = literal.base()

            # handle left guard
            if literal.lcomp is not None:
                op, term = literal.lcomp

                # create
                guard_literals.append(op.ast(term, base_val))
            # handle right guard
            if literal.rcomp is not None:
                op, term = literal.rcomp

                guard_literals.append(op.ast(base_val, term))
            # TODO: defaults? see mu-gringo!
            else:
                raise Exception()

            rules.append(
                NormalRule(
                    PredicateLiteral(eps_symbol, vars),
                    LiteralTuple(tuple(guard_literals + non_aggr_literals))
                )
            )

            # ----- eta rules -----
            for element in literal.func.elements:
                m = len(element.head)
                eta_symbol = sym_table.create(SpecialChar.ETA, n+m)

                rules.append(
                    NormalRule(
                        PredicateLiteral(eta_symbol, element.head + vars),
                        LiteralTuple(element.body.literals + tuple(non_aggr_literals))
                    )
                )

            # ----- replace original rule with modified rule -----
            rules.insert(0,
                NormalRule(
                    self.head,
                    LiteralTuple(tuple(aggr_map[literal] if isinstance(literal) else literal for literal in self.body)) # TODO: also restores original order
                )
            )

        # TODO: What else to rewrite ??? (see mu-gringo) 
        # TODO: how does this translate to disjunctive or choice rules ????? same ?????

        return rules