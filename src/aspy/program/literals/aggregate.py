from typing import Tuple, Optional, Set, Dict, TYPE_CHECKING
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from aspy.program.expression import Expr
from aspy.program.terms import Infimum, Supremum, Number
from aspy.program.safety import Safety, SafetyRule

from .literal import Literal

if TYPE_CHECKING:
    from aspy.program.expression import Substitution
    from aspy.program.terms import Term, Variable

    from .comparison import CompOp


class AggrOp(Enum):
    COUNT   = 0
    SUM     = 1
    MAX     = 2
    MIN     = 3

    def __repr__(self) -> str:
        return f"AggrOp({str(self)})"

    def __str__(self) -> str:
        if self == AggrOp.COUNT:
            return "#count"
        elif self == AggrOp.SUM:
            return "#sum"
        elif self == AggrOp.MAX:
            return "#max"
        else:
            return "#min"


@dataclass
class AggregateElement(Expr):
    terms: Tuple["Term", ...]
    literals: Tuple[Literal, ...]

    def __repr__(self) -> str:
        return f"AggregateElement({', '.join([repr(term) for term in self.terms])};{', '.join([repr(literal) for literal in self.literals])})"

    def __str__(self) -> str:
        return ', '.join([str(term) for term in self.terms]) + (f"; {', '.join([str(literal) for literal in self.literals])}" if self.literals else "")

    def head(self) -> Tuple["Term", ...]:
        return self.terms

    def body(self) -> Tuple[Literal, ...]:
        return self.literals

    def vars(self) -> Set["Variable"]:
        return self.head_vars.union(self.body_vars)

    def substitute(self, subst: Dict[str, "Term"]) -> "AggregateElement":
        return AggregateElement(tuple([term.substitute(subst) for term in self.terms]), tuple([literal.substitute(subst) for literal in self.literals]))

    def match(self, other: "Expr", subst: Optional["Substitution"]=None) -> "Substitution":
        """Tries to match the expression with another one."""
        pass


@dataclass
class AggregateFunction(Expr, ABC):
    elements: Tuple[AggregateElement, ...]

    def vars(self) -> Set["Variable"]:
        return set().union(*[element.vars() for element in self.elements])

    @abstractmethod
    def evaluate(self) -> Number:
        pass


class AggregateCount(AggregateFunction):
    def __repr__(self) -> str:
        return f"AggregateCount({';'.join([repr(element) for element in self.elements])})"

    def __str__(self) -> str:
        return f"#count{{{';'.join([str(element) for element in self.elements])}}}"

    def evaluate(self) -> Number:
        return len(self.elements)

    def substitute(self, subst: Dict[str, "Term"]) -> "AggregateCount":
        return AggregateCount(tuple([element.substitute(subst) for element in self.elements]))

    def match(self, other: "Expr", subst: Optional["Substitution"]=None) -> "Substitution":
        """Tries to match the expression with another one."""
        pass


class AggregateSum(AggregateFunction):
    def __repr__(self) -> str:
        return f"AggregateSum({';'.join([repr(element) for element in self.elements])})"

    def __str__(self) -> str:
        return f"#sum{{{';'.join([str(element) for element in self.elements])}}}"

    def evaluate(self) -> Number:
        # TODO: what if a tuple is empty ?
        # TODO: what if all tuples are empty or non have an integer as first element ?
        # TODO: evaluate recursively?
        raise Exception()
        #return Number(sum([tuple[0] for tuple in self.tuples if tuple and isinstance(tuple[0], Number)]))
    
    def substitute(self, subst: Dict[str, "Term"]) -> "AggregateSum":
        return AggregateSum(tuple([element.substitute(subst) for element in self.elements]))

    def match(self, other: "Expr", subst: Optional["Substitution"]=None) -> "Substitution":
        """Tries to match the expression with another one."""
        pass


class AggregateMin(AggregateFunction):
    def __repr__(self) -> str:
        return f"AggregateMin({';'.join([repr(element) for element in self.elements])})"

    def __str__(self) -> str:
        return f"#min{{{';'.join([str(element) for element in self.elements])}}}"

    def evaluate(self) -> Number:
        if self.tuples:
            # TODO: what if a tuple is empty
            # TODO: what if all tuples are empty\
            # TODO: evaluate recursively?
            return min([tuple[0] for tuple in self.tuples if tuple and isinstance(tuple[0], Number)])
        else:
            return Infimum

    def substitute(self, subst: Dict[str, "Term"]) -> "AggregateMin":
        return AggregateMin(tuple([element.substitute(subst) for element in self.elements]))

    def match(self, other: "Expr", subst: Optional["Substitution"]=None) -> "Substitution":
        """Tries to match the expression with another one."""
        pass


class AggregateMax(AggregateFunction):
    def __repr__(self) -> str:
        return f"AggregateMax({';'.join([repr(element) for element in self.elements])})"

    def __str__(self) -> str:
        return f"#max{{{';'.join([str(element) for element in self.elements])}}}"

    def evaluate(self):
        if self.tuples:
            # TODO: what if a tuple is empty
            # TODO: what if all tuples are empty
            # TODO: evaluate recursively?
            return max([tuple[0] for tuple in self.tuples if tuple and isinstance(tuple[0], Number)])
        else:
            return Supremum

    def substitute(self, subst: Dict[str, "Term"]) -> "AggregateMax":
        return AggregateMax(tuple([element.substitute(subst) for element in self.elements]))

    def match(self, other: Expr, subst: Optional["Substitution"]=None) -> "Substitution":
        """Tries to match the expression with another one."""
        pass


class AggregateLiteral(Literal):
    def __init__(self, func: AggregateFunction, lcomp: Optional[Tuple["CompOp", "Term"]]=None, rcomp: Optional[Tuple["CompOp", "Term"]]=None, naf: bool=False) -> None:
        super().__(naf)

        if(lcomp is None and rcomp is None):
            raise Exception("Aggregate requires either a left- or right-comparison.")

        self.func = func
        self.lcomp = lcomp
        self.rcomp = rcomp
        # TODO: rename comp to guards! (same for choice)

    def __repr__(self) -> str:
        literal_str = f"AggregateLiteral({repr(self.lcomp[1])} {repr(self.lcomp[0])} {repr(self.func)} {repr(self.rcomp[0])} {repr(self.rcomp[1])})"

        if self.naf:
            literal_str = f"Naf({literal_str})"

        return literal_str

    def __str__(self) -> str:
        return ("not " if self.neg else '') + f"{str(self.lcomp[1])} {str(self.lcomp[0])} {str(self.func)} {str(self.rcomp[0])} {str(self.rcomp[1])}"

    def invars(self) -> Set["Variable"]:
        return self.func.vars()

    def outvars(self) -> Set["Variable"]:
        vars = set()

        if not self.lcomp is None:
            vars.union(self.lcomp[1].vars())
        if not self.rcomp is None:
            vars.union(self.rcomp[1].vars())

        return vars()

    def safety(self, global_vars: Set["Variable"]) -> Safety:

        # set of global variables that appear inside the aggregate
        global_invars = self.invars().intersection(global_vars())
    
        # TODO: glob_r(self) = self.invars().intersection(glob(r)).union(self.outvars)

        # left guard specified
        if(self.lcomp is not None):
            if(self.lcomp[0] != CompOp.EQUAL):
                lsafety = Safety(set(),global_vars,set())
            else:
                # compute safety characterization of term guard
                term_safety = self.lcomp[1].safety()

                rules = set([SafetyRule(var, global_invars) for var in term_safety.safe])
                
                # variables appearing in left guard
                loutvars = self.lcomp[1].vars()

                lsafety = Safety(set(),global_vars.union(loutvars),rules).normalize()
        else:
            lsafety = None

        # right guard specified
        if(self.rcomp is not None):
            if(self.rcomp[0] != CompOp.EQUAL):
                rsafety = Safety(set(),global_vars,set())
            else:
                # compute safety characterization of term guard
                term_safety = self.rcomp[1].safety()

                rules = set([SafetyRule(var, global_invars) for var in term_safety.safe])
                
                # variables appearing in right guard
                routvars = self.rcomp[1].vars()

                rsafety = Safety(set(),global_vars.union(routvars),rules).normalize()
        else:
            rsafety = None

        if(lsafety is None):
            # aggregate has no guards
            if(rsafety is None):
                return Safety(set(),global_vars,set())
            # aggreagate has only right guard
            return rsafety
        else:
            # aggreagate has only left guard
            if(rsafety is None):
                return lsafety
            # aggregate has both left and right guards
            return Safety.closure( (lsafety, rsafety) )

    def substitute(self, subst: Dict[str, "Term"]) -> "AggregateLiteral":
        return AggregateLiteral(
            self.func.substitute(subst),
            (self.lcomp[0], self.lcomp[1].substitute(subst)),
            (self.rcomp[0], self.rcomp[1].substitute(subst)),
            self.naf
        )

    def match(self, other: Expr, subst: Optional["Substitution"]=None) -> "Substitution":
        """Tries to match the expression with another one."""
        raise Exception()


# TODO: evaluate for other terms, atoms, literals? 