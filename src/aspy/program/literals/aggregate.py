from typing import Tuple, Optional, Union, Set, TYPE_CHECKING
from abc import ABC, abstractmethod
from functools import cached_property

from aspy.program.expression import Expr
from aspy.program.terms import Infimum, Supremum, Number
from aspy.program.safety_characterization import SafetyTriplet, SafetyRule

from .literal import Literal

if TYPE_CHECKING:
    from aspy.program.terms import Term, TermTuple, Variable
    from aspy.program.literals import LiteralTuple
    from aspy.program.substitution import Substitution
    from aspy.program.operators import RelOp
    from aspy.program.statements import Statement
    from aspy.program.query import Query

    from .predicate import PredicateLiteral


class AggregateElement(Expr):
    """Represents an aggregate element."""
    def __init__(self, terms: "TermTuple", literals: "LiteralTuple") -> None:
        self.terms = terms
        self.literals = literals
        
    def __str__(self) -> str:
        return ', '.join([str(term) for term in self.terms]) + (f"; {', '.join([str(literal) for literal in self.literals])}" if self.literals else "")

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
        return set().union(*tuple(literal.pos_occ() for literal in self.literals))

    def neg_occ(self) -> Set["PredicateLiteral"]:
        return set().union(*tuple(literal.neg_occ() for literal in self.literals))

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return set().union(*self.head.vars(global_only), *self.body.vars(global_only))

    def substitute(self, subst: "Substitution") -> "AggregateElement":
        raise Exception("Substitution for aggregate elements not supported yet.")

    def match(self, other: Expr) -> Set["Substitution"]:
        raise Exception("Matching for aggregate elements not supported yet.")


class Aggregate(Expr, ABC):
    """Abstract base class for all aggregates"""
    def __init__(self, elements: Tuple[AggregateElement, ...]) -> None:
        self.elements = elements

    @cached_property
    def ground(self) -> bool:
        return all(element.ground for element in self.elements)

    def vars(self, global_only: bool=False, bound_only: bool=False) -> Set["Variable"]:
        return set().union(*tuple(element.vars() for element in self.elements)) if not (bound_only or global_only) else set()  # TODO: does not quite follow the definition in ASP-Core-2?

    @abstractmethod
    def eval(self) -> Number:
        pass

    def pos_occ(self) -> Set["PredicateLiteral"]:
        return set().union(*tuple(element.pos_occ() for element in self.elements))

    def neg_occ(self) -> Set["PredicateLiteral"]:
        return set().union(*tuple(element.neg_occ() for element in self.elements))

    def match(self, other: Expr) -> Set["Substitution"]:
        raise Exception("Matching for aggregates not supported yet.")


class AggregateCount(Aggregate):
    """Represents a 'count' aggregate."""
    def __str__(self) -> str:
        return f"#count{{{';'.join([str(element) for element in self.elements])}}}"

    def eval(self) -> Number:
        return len(self.elements)

    def substitute(self, subst: "Substitution") -> "AggregateCount":
        # substitute elements recursively
        elements = (element.substitute(subst) for element in self.elements)

        return AggregateCount(elements)


class AggregateSum(Aggregate):
    """Represents a 'sum' aggregate."""
    def __str__(self) -> str:
        return f"#sum{{{';'.join([str(element) for element in self.elements])}}}"

    def eval(self) -> Number:
        # TODO: what if a tuple is empty ?
        # TODO: what if all tuples are empty or non have an integer as first element ?
        # TODO: evaluate recursively?
        raise Exception()
        #return Number(sum([tuple[0] for tuple in self.tuples if tuple and isinstance(tuple[0], Number)]))

    def substitute(self, subst: "Substitution") -> "AggregateSum":
        # substitute elements recursively
        elements = (element.substitute(subst) for element in self.elements)

        return AggregateSum(*elements)


class AggregateMin(Aggregate):
    """Represents a 'minimum' aggregate."""
    def __str__(self) -> str:
        return f"#min{{{';'.join([str(element) for element in self.elements])}}}"

    def eval(self) -> Number:
        if self.tuples:
            # TODO: what if a tuple is empty
            # TODO: what if all tuples are empty\
            # TODO: evaluate recursively?
            return min([tuple[0] for tuple in self.tuples if tuple and isinstance(tuple[0], Number)])
        else:
            return Infimum

    def substitute(self, subst: "Substitution") -> "AggregateMin":
        # substitute elements recursively
        elements = (element.substitute(subst) for element in self.elements)

        return AggregateMin(*elements)


class AggregateMax(Aggregate):
    """Represents a 'maximum' aggregate."""
    def __str__(self) -> str:
        return f"#max{{{';'.join([str(element) for element in self.elements])}}}"

    def eval(self):
        if self.tuples:
            # TODO: what if a tuple is empty
            # TODO: what if all tuples are empty
            # TODO: evaluate recursively?
            return max([tuple[0] for tuple in self.tuples if tuple and isinstance(tuple[0], Number)])
        else:
            return Supremum

    def substitute(self, subst: "Substitution") -> "AggregateMax":
        # substitute elements recursively
        elements = (element.substitute(subst) for element in self.elements)

        return AggregateMax(*elements)


class AggregateLiteral(Literal):
    """Represents an aggregate literal."""
    def __init__(self, func: Aggregate, lcomp: Optional[Tuple["RelOp", "Term"]]=None, rcomp: Optional[Tuple["RelOp", "Term"]]=None, naf: bool=False) -> None:
        super().__init__(naf)

        if(lcomp is None and rcomp is None):
            raise Exception("Aggregate requires either a left- or right-comparison.")

        self.func = func
        self.lcomp = lcomp
        self.rcomp = rcomp

    def __str__(self) -> str:
        return ("not " if self.neg else '') + f"{str(self.lcomp[1])} {str(self.lcomp[0])} {str(self.func)} {str(self.rcomp[0])} {str(self.rcomp[1])}"

    @cached_property
    def ground(self) -> bool:
        return self.func.ground and (self.lcomp[1] if not self.lcomp is None else True) and (self.rcomp[1] if not self.rcomp is None else True)

    def pos_occ(self) -> Set["PredicateLiteral"]:
        return self.func.pos_occ()

    def neg_occ(self) -> Set["PredicateLiteral"]:
        return self.func.neg_occ()

    def guards(self) -> Tuple[Tuple["RelOp", "Term"], Tuple["RelOp", "Term"]]:
        return (self.lcomp, self.rcomp)

    def invars(self) -> Set["Variable"]:
        return self.func.vars()

    def outvars(self) -> Set["Variable"]:
        return set().union(*tuple(guard[1].vars() for guard in self.guards() if not guard is None))

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return self.outvars() if global_only else self.invars().union(self.outvars())

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> SafetyTriplet:

        if global_vars is None:
            if rule is None:
                raise AttributeError("Computing safety characterization for 'AggregateLiteral' requires a reference to the encompassing rule or the set of global variables in it.")

            # get global variables from rule
            global_vars = rule.vars(global_only=True)

        # set of global variables that appear inside the aggregate
        global_invars = self.invars().intersection(global_vars)

        guard_safeties = []

        for comp in (self.lcomp, self.rcomp):
            # guard specified
            if(comp is None):
                lsafety = None
            elif(comp[0] != RelOp.EQUAL):
                lsafety = SafetyTriplet(unsafe=global_invars)
            else:
                # compute safety characterization w.r.t. left term guard
                guard_safeties.append(
                    SafetyTriplet(
                        unsafe=global_invars.union(comp[1].vars()), # global inner variables and variables in guard term
                        rules=set([SafetyRule(var, global_invars) for var in comp[1].safety().safe])
                    ).normalize()
                )

        # no guards specified
        if not guard_safeties:
            return SafetyTriplet(unsafe=global_vars)
        # on guard specified
        elif len(guard_safeties) == 1:
            return guard_safeties[0]
        # both guards specified
        else:
            return SafetyTriplet.closure(guard_safeties)

    def substitute(self, subst: "Substitution") -> "AggregateLiteral":
        # substitute guard terms recursively
        lcomp = (self.lcomp[0], self.lcomp[1].substitute(subst))
        rcomp = (self.rcomp[0], self.rcomp[1].substitute(subst))

        return AggregateLiteral(self.func, lcomp, rcomp, self.naf)

    def match(self, other: Expr) -> Set["Substitution"]:
        raise Exception("Matching for aggregate literals not supported yet.")