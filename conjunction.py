from typing import Tuple, Iterable, Optional, Dict

from atom import ClassicalAtom, Literal, BuiltinAtom
from term import Term


class Conjunction: # TODO: inherit from Expr ?
    def __init__(self, literals: Optional[Tuple[Literal]]=None):
        if literals is None:
            literals = tuple()

        self.literals = literals

    def __len__(self) -> int:
        return len(self.literals)

    def __iter__(self) -> Iterable[Literal]:
        return iter(self.literals)

    def substitute(self, subst: Dict[str, Term]) -> "Conjunction":
        return Conjunction(
            tuple(literal.substitute(subst) for literal in self.literals)
        )

    def __repr__(self) -> str:
        return f"Conjunction({','.join([repr(literal) for literal in self.literals])})"

    def __str__(self) -> str:
        return ','.join([str(literal) for literal in self.literals])

    """
    def getPositive(self) -> "Conjunction":

        positive_literals = []

        for literal in self.literals:
            if isinstance(literal, BuiltinAtom) or (isinstance(literal, ClassicalAtom) and not literal.neg):
                positive_literals.append(literal)
        
        return Conjunction(tuple(positive_literals))

    def getNegative(self) -> "Conjunction":

        negative_literals = []

        for literal in self.literals:
            if isinstance(literal, ClassicalAtom) and literal.neg:
                negative_literals.append(literal)
        
        return Conjunction(tuple(negative_literals))
    """