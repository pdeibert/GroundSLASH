from typing import Tuple, Optional, Union, List, Set, TYPE_CHECKING
from abc import ABC, abstractmethod
from functools import cached_property, reduce

from aspy.program.expression import Expr
from aspy.program.symbol_table import SpecialChar
from aspy.program.terms import Infimum, Supremum, Number, TermTuple
from aspy.program.safety_characterization import SafetyTriplet, SafetyRule
#from aspy.program.statements import EpsRule, EtaRule

from .guard import Guard
from .literal import Literal, LiteralTuple
from .special import AlphaLiteral

if TYPE_CHECKING:
    from aspy.program.terms import Term, Variable
    from aspy.program.substitution import Substitution
    from aspy.program.statements import Statement
    from aspy.program.query import Query
    from aspy.program.variable_table import VariableTable

    from .predicate import PredicateLiteral

# TODO: what if aggregate element has no terms ???


class AggregateElement(Expr):
    """Represents an aggregate element."""
    def __init__(self, terms: Optional["TermTuple"]=None, literals: Optional["LiteralTuple"]=None) -> None:
        self.terms = terms if terms is not None else tuple()
        self.literals = literals if literals is not None else tuple()

    def __eq__(self, other: Expr) -> bool:
        return isinstance(other, AggregateElement) and self.terms == other.terms and self.literals == other.literals

    def __hash__(self) -> int:
        return hash( ("aggr element", self.terms, self.literals) )

    def __str__(self) -> str:
        return ','.join([str(term) for term in self.terms]) + (f":{','.join([str(literal) for literal in self.literals])}" if self.literals else "")

    @property
    def head(self) -> "TermTuple":
        return self.terms

    @property
    def body(self) -> "LiteralTuple":
        return self.literals

    @cached_property
    def ground(self) -> bool:
        return all(term.ground for term in self.terms) and all(literal.ground for literal in self.literals)

    def pos_occ(self) -> Set["PredicateLiteral"]:
        return self.literals.pos_occ()

    def neg_occ(self) -> Set["PredicateLiteral"]:
        return self.literals.neg_occ()

    @cached_property
    def weight(self) -> int:
        if len(self.terms) > 0 and isinstance(self.terms[0], Number):
            return self.terms[0].val

        return 0

    def satisfied(self, literals: Set["Literal"]) -> bool:
        # check if all condition literals are part of the specified set
        return all(literal in literals for literal in self.literals)

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return self.head.vars(global_only).union(self.body.vars(global_only))

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> SafetyTriplet:
        raise ValueError("Safety characterization for aggregate elements is undefined without context.")

    def substitute(self, subst: "Substitution") -> "AggregateElement":
        terms = TermTuple(*tuple(term.substitute(subst) for term in self.terms))
        literals = LiteralTuple(*tuple(literal.substitute(subst) for literal in self.literals))

        return AggregateElement(terms, literals)

    def match(self, other: Expr) -> Set["Substitution"]:
        raise Exception("Matching for aggregate elements not supported yet.")

    def replace_arith(self, var_table: "VariableTable") -> "AggregateElement":
        return AggregateElement(TermTuple(*self.terms.replace_arith(var_table)), LiteralTuple(*self.literals.replace_arith(var_table)))


class Aggregate(Expr, ABC):
    """Abstract base class for all aggregates"""
    def __init__(self, *elements: AggregateElement) -> None:
        self.elements = tuple(elements)

    @cached_property
    def ground(self) -> bool:
        return all(element.ground for element in self.elements)

    def vars(self, global_only: bool=False, bound_only: bool=False) -> Set["Variable"]:
        return set().union(*tuple(element.vars() for element in self.elements)) if not (bound_only or global_only) else set()  # TODO: does not quite follow the definition in ASP-Core-2?

    @abstractmethod
    def eval(self) -> Number:
        pass

    @abstractmethod
    def base(self) -> "Term":
        pass

    def pos_occ(self) -> Set["PredicateLiteral"]:
        return set().union(*tuple(element.pos_occ() for element in self.elements))

    def neg_occ(self) -> Set["PredicateLiteral"]:
        return set().union(*tuple(element.neg_occ() for element in self.elements))

    def match(self, other: Expr) -> Set["Substitution"]:
        raise Exception("Matching for aggregates not supported yet.")

    def replace_arith(self, var_table: "VariableTable") -> "Aggregate":
        return type(self)( *tuple(element.replace_arith(var_table) for element in self.elements) )


class AggregateCount(Aggregate):
    """Represents a 'count' aggregate."""
    def __str__(self) -> str:
        return f"#count{{{';'.join([str(element) for element in self.elements])}}}"

    def __eq__(self, other: Expr) -> bool:
        return isinstance(other, AggregateCount) and self.elements == other.elements

    def __hash__(self) -> int:
        return hash( ("count", self.elements) )

    def eval(self) -> int:
        return Number(len(self.elements))

    def base(self) -> Number:
        return Number(0)

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> SafetyTriplet:
        raise ValueError("Safety characterization for aggregate is undefined without context.")

    def substitute(self, subst: "Substitution") -> "AggregateCount":
        # substitute elements recursively
        elements = tuple(element.substitute(subst) for element in self.elements)

        return AggregateCount(*elements)
 

class AggregateSum(Aggregate):
    """Represents a 'sum' aggregate."""
    def __str__(self) -> str:
        return f"#sum{{{';'.join([str(element) for element in self.elements])}}}"

    def __eq__(self, other: Expr) -> bool:
        return isinstance(other, AggregateSum) and self.elements == other.elements

    def __hash__(self) -> int:
        return hash( ("sum", self.elements) )

    def eval(self) -> Number:
        # empty tuple set
        if not self.elements:
            return self.base

        # non-empty set
        return Number(sum(element.weight for element in self.elements))

    def base(self) -> Number:
        # TODO: correct?
        return Number(0)

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> SafetyTriplet:
        raise ValueError("Safety characterization for aggregate is undefined without context.")

    def substitute(self, subst: "Substitution") -> "AggregateSum":
        # substitute elements recursively
        elements = (element.substitute(subst) for element in self.elements)

        return AggregateSum(*elements)


class AggregateMin(Aggregate):
    """Represents a 'minimum' aggregate."""
    def __str__(self) -> str:
        return f"#min{{{';'.join([str(element) for element in self.elements])}}}"

    def __eq__(self, other: Expr) -> bool:
        return isinstance(other, AggregateMin) and self.elements == other.elements

    def __hash__(self) -> int:
        return hash( ("min", self.elements) )

    def eval(self) -> Number:
        if self.elements:
            # TODO: what about elements with no terms?
            return reduce(lambda e1, e2: e2.terms[0] if not e1.terms[0].precedes(e2.terms[0]) else e1.terms[0], self.elements) # min
        else:
            return self.base()

    def base(self) -> Supremum:
        return Supremum

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> SafetyTriplet:
        raise ValueError("Safety characterization for aggregate is undefined without context.")

    def substitute(self, subst: "Substitution") -> "AggregateMin":
        # substitute elements recursively
        elements = (element.substitute(subst) for element in self.elements)

        return AggregateMin(*elements)


class AggregateMax(Aggregate):
    """Represents a 'maximum' aggregate."""
    def __str__(self) -> str:
        return f"#max{{{';'.join([str(element) for element in self.elements])}}}"

    def __eq__(self, other: Expr) -> bool:
        return isinstance(other, AggregateMax) and self.elements == other.elements

    def __hash__(self) -> int:
        return hash( ("max", self.elements) )

    def eval(self) -> Number:
        if self.elements:
            # TODO: what about elements with no terms?
            return reduce(lambda e1, e2: e2.terms[0] if not e2.terms[0].precedes(e1.terms[0]) else e1.terms[0], self.elements) # max
        else:
            return self.base()

    def base(self) -> Infimum:
        return Infimum

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> SafetyTriplet:
        raise ValueError("Safety characterization for aggregate is undefined without context.")

    def substitute(self, subst: "Substitution") -> "AggregateMax":
        # substitute elements recursively
        elements = (element.substitute(subst) for element in self.elements)

        return AggregateMax(*elements)


class AggregateLiteral(Literal):
    """Represents an aggregate literal."""
    def __init__(self, func: Aggregate, guards: Union[Guard, Tuple[Guard, ...]], naf: bool=False) -> None:
        super().__init__(naf)

        # initialize left and right guard to 'None'
        self.lguard, self.rguard = None, None

        # single guard specified
        if isinstance(guards, Guard):
            # wrap in tuple
            guards = (guards, )
        # guard tuple specified
        elif isinstance(guards, Tuple) and len(guards) not in {1,2}:
            raise ValueError("Aggregate requires at least one and at most two guards to be specified.")

        # process guards
        for guard in guards:
            if guard is None:
                continue

            if guard.right:
                if self.rguard is not None:
                    raise ValueError("Multiple right guards specified for aggregate.")
                self.rguard = guard
            else:
                if self.lguard is not None:
                    raise ValueError("Multiple right guards specified for aggregate.")
                self.lguard = guard

        self.func = func

    def __str__(self) -> str:
        return ("not " if self.naf else '') + f"{f'{str(self.lguard.bound)} {self.lguard.op} ' if self.lguard is not None else ''}{str(self.func)}{f' {str(self.rguard.op)} {str(self.rguard.bound)}' if self.rguard is not None else ''}"

    @cached_property
    def ground(self) -> bool:
        return self.func.ground and (self.lguard.bound.ground if self.lguard is not None else True) and (self.rguard.bound.ground if self.rguard is not None else True)

    def set_naf(self, value: bool=True) -> None:
        self.naf = value

    def pos_occ(self) -> Set["PredicateLiteral"]:
        return self.func.pos_occ()

    def neg_occ(self) -> Set["PredicateLiteral"]:
        return self.func.neg_occ()

    @property
    def guards(self) -> Tuple[Union[Guard, None], Union[Guard, None]]:
        return (self.lguard, self.rguard)

    def invars(self) -> Set["Variable"]:
        return self.func.vars()

    def outvars(self) -> Set["Variable"]:
        return set().union(*tuple(guard.bound.vars() for guard in self.guards if guard is not None))

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return self.outvars() if global_only else self.invars().union(self.outvars())

    def eval(self) -> bool:
        if not self.ground:
            raise ValueError("Cannot evaluate non-ground aggregate.")

        # evaluate aggregate function
        aggr_term = self.func.eval()

        # check guards
        return (self.lguard.op.eval(self.lguard.bound, aggr_term) if self.lguard is not None else True) and (self.rguard.op.eval(aggr_term, self.rguard.bound) if self.rguard is not None else True)

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> SafetyTriplet:

        if global_vars is None:
            if rule is None:
                raise AttributeError("Computing safety characterization for 'AggregateLiteral' requires a reference to the encompassing rule or the set of global variables in it.")

            # get global variables from rule
            global_vars = rule.vars(global_only=True)

        # set of global variables that appear inside the aggregate
        aggr_global_invars = self.invars().intersection(global_vars)
        aggr_global_vars = aggr_global_invars.union(self.outvars())

        guard_safeties = []

        for guard in self.guards:
            # guard not specified
            if(guard is None):
                continue
            elif(str(guard.op) != "="): # TODO: cannot compare to enum directly due to circular imports
                guard_safeties.append(SafetyTriplet(unsafe=aggr_global_vars))
            else:
                # compute safety characterization w.r.t. left term guard
                guard_safeties.append(
                    SafetyTriplet(
                        unsafe=aggr_global_vars, # global inner variables and variables in guard term
                        rules=set([SafetyRule(var, aggr_global_invars) for var in guard.bound.safety().safe])
                    ).normalize()
                )

        # TODO: can be simplified?
        if len(guard_safeties) == 1:
            return guard_safeties[0]
        # both guards specified
        else:
            return SafetyTriplet.closure(guard_safeties)

    def substitute(self, subst: "Substitution") -> "AggregateLiteral":
        # substitute guard terms recursively
        guards = tuple(guard.substitute(subst) if guard is not None else None for guard in self.guards)

        return AggregateLiteral(self.func.substitute(subst), guards, naf=self.naf)

    def match(self, other: Expr) -> Set["Substitution"]:
        raise Exception("Matching for aggregate literals not supported yet.")

    def replace_arith(self, var_table: "VariableTable") -> "AggregateLiteral":
        # replace guards
        guards = (None if guard is None else guard.replace_arith(var_table) for guard in self.guards())

        return AggregateLiteral(self.func.replace_arith(var_table), *guards, self.naf)