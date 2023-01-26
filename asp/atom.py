from typing import Tuple, Dict, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property

from .expression import Expr
from .term import Term
from .literal import Literal, NafLiteral


class Atom(Expr, ABC):
    """Abstract base class for all atoms."""
    pass


@dataclass
class PredicateAtom(Atom): # TODO: inherit from Expr ?
    """Predicate."""
    name: str
    terms: Tuple[Term, ...]

    def __init__(self, name: str, terms: Optional[Tuple[Term, ...]]=None) -> None:

        if terms is None:
            terms = tuple()

        self.name = name
        self.terms = terms

    def __repr__(self) -> str:
        return f"PredicateAtom[{self.name}]({','.join([repr(term) for term in self.terms])})"

    def __str__(self) -> str:
        return self.name + (f"({','.join([str(term) for term in self.terms])})" if self.terms else '')

    @cached_property
    def arity(self) -> int:
        return len(self.terms)

    def substitute(self, subst: Dict[str, Term]) -> "PredicateAtom":
        # TODO: root term?
        return PredicateAtom(
            self.name,
            tuple(term.substitute(subst) for term in self.terms)
        )


@dataclass
class ClassicalAtom(Atom, NafLiteral):
    """Classical atom."""
    atom: PredicateAtom
    cneg: bool=False

    def __repr__(self) -> str:
        return ('-' if self.cneg else '') + f"ClassicalAtom({repr(self.atom)})"

    def __str__(self) -> str:
        return ('-' if self.cneg else '') + str(self.atom)

    def __neg__(self) -> "ClassicalAtom":
        return ClassicalAtom(self.atom, ~self.neg)

    def __invert__(self) -> "ClassicalAtom":
        return -self

    def __abs__(self) -> "ClassicalAtom":
        return ClassicalAtom(self.atom)

    def substitute(self, subst: Dict[str, Term]) -> "ClassicalAtom":
        # TODO: root term?
        return ClassicalAtom(
            self.atom.substitute(subst),
            self.cneg
        )


@dataclass
class DefaultAtom(Atom, NafLiteral):
    """Default atom."""
    catom: ClassicalAtom
    dneg: bool=False

    @property
    def atom(self) -> PredicateAtom:
        return self.catom.atom

    @property
    def cneg(self) -> bool:
        return self.catom.cneg

    def __neg__(self) -> "DefaultAtom":
        return DefaultAtom(self.catom, ~self.neg)

    def __invert__(self) -> "DefaultAtom":
        return -self

    def __abs__(self) -> "DefaultAtom":
        return DefaultAtom(self.catom)

    def __repr__(self) -> str:
        return ('-' if self.dneg else '') + f"DefaultAtom({repr(self.catom)})"

    def __str__(self) -> str:
        return ('not ' if self.dneg else '') + str(self.catom)

    def substitute(self, subst: Dict[str, Term]) -> "DefaultAtom":
        # TODO: root term?
        return DefaultAtom(
            self.catom.substitute(subst),
            self.dneg
        )


@dataclass
class BuiltinAtom(Atom, NafLiteral, ABC):
    loperand: Term
    roperand: Term

    @abstractmethod
    def evaluate(self) -> bool:
        pass


class Equal(BuiltinAtom):
    def __repr__(self) -> str:
        return f"Equal({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}={str(self.roperand)}"

    def substitute(self, subst: Dict[str, Term]) -> "Equal":
        return Equal(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst)
        )

    def evaluate(self) -> bool:
        # TODO: evaluate recursively?
        return self.loperand == self.roperand    


class Unequal(BuiltinAtom):
    def __repr__(self) -> str:
        return f"Unequal({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}!={str(self.roperand)}"

    def substitute(self, subst: Dict[str, Term]) -> "Unequal":
        return Unequal(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst)
        )

    def evaluate(self) -> bool:
        # TODO: evaluate recursively?
        return self.loperand != self.roperand


class Less(BuiltinAtom):
    def __repr__(self) -> str:
        return f"Less({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}<{str(self.roperand)}"

    def substitute(self, subst: Dict[str, Term]) -> "Less":
        return Less(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst)
        )

    def evaluate(self) -> bool:
        # TODO: evaluate recursively?
        return self.loperand < self.roperand


class Greater(BuiltinAtom):
    def __repr__(self) -> str:
        return f"Greater({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}>{str(self.roperand)}"

    def substitute(self, subst: Dict[str, Term]) -> "Greater":
        return Greater(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst)
        )

    def evaluate(self) -> bool:
        # TODO: evaluate recursively?
        return self.loperand > self.roperand


class LessEqual(BuiltinAtom):
    def __repr__(self) -> str:
        return f"LessEqual({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}<={str(self.roperand)}"

    def substitute(self, subst: Dict[str, Term]) -> "LessEqual":
        return LessEqual(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst)
        )

    def evaluate(self) -> bool:
        # TODO: evaluate recursively?
        return self.loperand <= self.roperand


class GreaterEqual(BuiltinAtom):
    def __repr__(self) -> str:
        return f"GreaterEqual({repr(self.loperand)},{repr(self.roperand)})"

    def __str__(self) -> str:
        return f"{str(self.loperand)}>={str(self.roperand)}"

    def substitute(self, subst: Dict[str, Term]) -> "GreaterEqual":
        return GreaterEqual(
            self.loperand.substitute(subst),
            self.roperand.substitute(subst)
        )

    def evaluate(self) -> bool:
        # TODO: evaluate recursively?
        return self.loperand >= self.roperand