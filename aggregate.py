from typing import Tuple, Optional, Dict
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from term import Term, Number, Infimum, Supremum
from comparison import CompOp


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
class AggregateFunction(ABC):
    tuples: Tuple[Tuple[Term, ...], ...] # tuple of tuples of terms

    @abstractmethod
    def __call__(self) -> Number:
        pass


class AggregateCount(AggregateFunction):
    @abstractmethod
    def __call__(self) -> Number:
        return len(self.tuples)

    def substitute(self, subst: Dict[str, Term]) -> "AggregateCount":
        return AggregateCount(
            tuple(
                tuple(
                    term.substitute(subst) for term in tup
                )
                for tup in self.tuples
            )
        )

    def __repr__(self) -> str:
        return f"AggregateCount({';'.join([','.join([repr(term) for term in tup]) for tup in self.tuples])})"

    def __str__(self) -> str:
        return f"#count{{{';'.join([','.join([repr(term) for term in tup]) for tup in self.tuples])}}}"


class AggregateSum(AggregateFunction):
    @abstractmethod
    def __call__(self) -> Number:
        # TODO: what if a tuple is empty ?
        # TODO: what if all tuples are empty or non have an integer as first element ?
        return Number(sum([tuple[0] for tuple in self.tuples if tuple and isinstance(tuple[0], Number)]))

    def substitute(self, subst: Dict[str, Term]) -> "AggregateSum":
        return AggregateCount(
            tuple(
                tuple(
                    term.substitute(subst) for term in tup
                )
                for tup in self.tuples
            )
        )

    def __repr__(self) -> str:
        return f"AggregateSum({';'.join([','.join([repr(term) for term in tup]) for tup in self.tuples])})"

    def __str__(self) -> str:
        return f"#sum{{{';'.join([','.join([repr(term) for term in tup]) for tup in self.tuples])}}}"


class AggregateMin(AggregateFunction):
    @abstractmethod
    def __call__(self) -> Number:
        if self.tuples:
            # TODO: what if a tuple is empty
            # TODO: what if all tuples are empty
            return min([tuple[0] for tuple in self.tuples if tuple and isinstance(tuple[0], Number)])
        else:
            return Infimum

    def substitute(self, subst: Dict[str, Term]) -> "AggregateMin":
        return AggregateCount(
            tuple(
                tuple(
                    term.substitute(subst) for term in tup
                )
                for tup in self.tuples
            )
        )

    def __repr__(self) -> str:
        return f"AggregateMin({';'.join([','.join([repr(term) for term in tup]) for tup in self.tuples])})"

    def __str__(self) -> str:
        return f"#min{{{';'.join([','.join([repr(term) for term in tup]) for tup in self.tuples])}}}"



class AggregateMax(AggregateFunction):
    @abstractmethod
    def __call__(self):
        if self.tuples:
            # TODO: what if a tuple is empty
            # TODO: what if all tuples are empty
            return max([tuple[0] for tuple in self.tuples if tuple and isinstance(tuple[0], Number)])
        else:
            return Supremum

    def substitute(self, subst: Dict[str, Term]) -> "AggregateMax":
        return AggregateCount(
            tuple(
                tuple(
                    term.substitute(subst) for term in tup
                )
                for tup in self.tuples
            )
        )

    def __repr__(self) -> str:
        return f"AggregateMax({';'.join([','.join([repr(term) for term in tup]) for tup in self.tuples])})"

    def __str__(self) -> str:
        return f"#max{{{';'.join([','.join([repr(term) for term in tup]) for tup in self.tuples])}}}"


class AggregateAtom: # TODO: inherit?
    def __init__(self, func: AggregateFunction, lcomp: Optional[Tuple[CompOp, Term]]=None, rcomp: Optional[Tuple[CompOp, Term]]=None) -> None:

        if(lcomp is None and rcomp is None):
            raise Exception("Aggregate requires either a left- or right-comparison.")

        self.func = func
        self.lcomp = lcomp
        self.rcomp = rcomp

    def substitute(self, subst: Dict[str, Term]) -> "AggregateAtom":
        return AggregateAtom(
            self.func.substitute(subst),
            (self.lcomp[0], self.lcomp[1].substitute(subst)),
            (self.rcomp[0], self.rcomp[1].substitute(subst))
        )

    def __repr__(self) -> str:
        return f"AggregateAtom({repr(self.lcomp[1])} {repr(self.lcomp[0])} {repr(self.func)} {repr(self.rcomp[0])} {repr(self.rcomp[1])})"

    def __str__(self) -> str:
        return f"{str(self.lcomp[1])} {str(self.lcomp[0])} {str(self.func)} {str(self.rcomp[0])} {str(self.rcomp[1])}"


@dataclass
class AggregateLiteral:
    atom: AggregateAtom
    neg: bool=False

    def substitute(self, subst: Dict[str, Term]) -> "AggregateLiteral":
        return AggregateLiteral(
            self.atom.substitute(subst),
            self.neg
        )

    def __repr__(self) -> str:
        return ("-" if self.neg else '') + repr(self.atom)

    def __str__(self) -> str:
        return ("not " if self.neg else '') + str(self.atom)