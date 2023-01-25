from typing import Tuple, Iterable, Optional, Dict

from atom import ClassicalAtom, Literal
from term import Term


class Disjunction: # TODO: inherit from Expr ?
    def __init__(self, literals: Optional[Tuple[ClassicalAtom]]=None):
        if literals is None:
            literals = tuple()
        
        self.literals = literals

    def __len__(self) -> int:
        return len(self.literals)

    def __iter__(self) -> Iterable[Literal]:
        return iter(self.literals)

    def substitute(self, subst: Dict[str, Term]) -> "Disjunction":
        return Disjunction(
            tuple(literal.substitute(subst) for literal in self.literals)
        )

    def __repr__(self) -> str:
        return f"Disjunction({','.join([repr(literal) for literal in self.literals])})"

    def __str__(self) -> str:
        return '|'.join([str(literal) for literal in self.literals])


# TODO: neg(), pos() to return positive, negative literals?