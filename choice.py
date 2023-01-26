from typing import Optional, Tuple

from comparison import CompOp
from atom import ClassicalAtom, NafLiteral
from term import Term
from expression import Expr


class ChoiceElement(Expr):
    """Choice element."""
    def __init__(self, atom: ClassicalAtom, literals: Optional[Tuple[NafLiteral]]=None) -> None:
        if literals is None:
            literals = tuple()

        self.atom = atom
        self.literals = literals

    def __repr__(self) -> str:
        return f"{repr(self.atom)}:{','.join([repr(literal) for literal in self.literals])}"

    def __str__(self) -> str:
        return f"{str(self.atom)}:{','.join([str(literal) for literal in self.literals])}"


class Choice(Expr):
    """Choice."""
    def __init__(self, literals: Optional[Tuple[ChoiceElement]]=None, lcomp: Optional[Tuple[CompOp, Term]]=None, rcomp: Optional[Tuple[CompOp, Term]]=None):
        if literals is None:
            literals = tuple()

        self.literals = literals
        self.lcomp = lcomp
        self.rcomp = rcomp

    def __repr__(self) -> str:
        return "Choice(" + (f"{repr(self.lcomp[1])} {repr(self.lcomp[0])}" if self.lcomp else "") + f"{{{';'.join([repr(literal) for literal in self.literals])}}}" + (f"{repr(self.lcomp[0])} {repr(self.lcomp[1])}" if self.lcomp else "") + ")"

    def __str__(self) -> str:
        return (f"{str(self.lcomp[1])} {str(self.lcomp[0])}" if self.lcomp else "") + f"{{{';'.join([str(literal) for literal in self.literals])}}}" + (f"{str(self.lcomp[0])} {str(self.lcomp[1])}" if self.lcomp else "")
    
    
"""
        # TODO: can they even be evaluated already?
        # TODO: clingo test!

        # process comparison operators and terms:
        if(lcomp is None and rcomp is None):
            # lower bound
            lcomp = (CompOp.GREATER_OR_EQ, Number(0))
            # upper bound
            rcomp = (CompOp.LESS_OR_EQ, Number(len(self.literals)))
        elif lcomp is None:
            rop, rterm = rcomp
            if rop in [CompOp.LESS, CompOp.LESS_OR_EQ]:
                # switch to the left
                lcomp = (-rop, rterm)
                # use default upper bound
                rcomp = (CompOp.GREATER_OR_EQ, Number(len(self.literals)))
            else:
                # move to right for convenience
                lcomp = rcomp
                rcomp = None
        elif rcomp is None:
            lop, lterm = lcomp
            if lop in [CompOp.GREATER, CompOp.GREATER_OR_EQ]:
                # switch to the right
                rcomp = (-lop, lterm)
                # use default lower bound
                lcomp = (CompOp.LESS_OR_EQ, Number(0))
        else:
            lop, lterm = lcomp
            rop, rterm = rcomp

            if(lop == CompOp.EQUAL or rop == CompOp.EQUAL):
                # lterm = {...} = rterm
                if lop == rop:
                    if lterm == rterm:
                        # only keep one for convenience
                        rcomp = None
                    else:
                        # TODO: not satisfiable
                        pass
                
                elif lop == CompOp.EQUAL:
                    pass
                else:
                    pass

            if lop == -rop:
                # lterm != {...} != rterm
                if lop == CompOp.UNEQUAL:
                    if lterm == rterm:
                        # only keep one for convenience
                        rcomp = None
                    else:
                        # keep both
                        pass
                # lterm = {...} = rterm
                elif lop == CompOp.EQUAL:
                    if lterm == rterm:
                        # only keep one for convenience
                        rcomp = None
                    else:
                        # TODO: not satisfiable
                        pass
                # lterm  < {...} >  rterm
                # lterm <= {...} >= rterm
                elif lop in [CompOp.LESS, CompOp.LESS_OR_EQ]:
                    # choose larger lower bound and drop other comparison for convenience
                    lcomp = (lop, max((lterm, rterm)))
                    rcomp = None
                # lterm  > {...} <  rterm
                # lterm >= {...} <= rterm
                else:
                    # choose smaller upper bound and drop other comparison for convenience
                    lcomp = (lop, min((lterm, rterm)))
                    rcomp = None
            elif lop == ~rop:
                # lterm  = {...} != rterm
                if lop == CompOp.EQUAL:
                    if lterm != rterm:
                        # just keep the equality constraint
                        rcomp = None
                    else:
                        # TODO: unsatisfiable
                        pass
                # lterm != {...} = rterm
                elif lop == CompOp.UNEQUAL:
                    if lterm != rterm:
                        # just keep the equality constraint
                        lcomp = (rop, rterm)
                    else:
                        # TODO: unsatisfiable
                        pass
                # lterm  < {...} >= rterm
                elif lop == CompOp.LESS:
                    # choose larger lower bound and drop other comparison for convenience
                    lcomp = (rop, max((lterm+1, rterm)))
                    rcomp = None
                # lterm <= {...} >  rterm
                elif lop == CompOp.LESS_OR_EQ:
                    # choose larger lower bound and drop other comparison for convenience
                    lcomp = (lop, max((lterm, rterm+1)))
                    rcomp = None
                # lterm > {...} <= rterm
                elif lop == CompOp.GREATER:
                    # choose smaller upper bound and drop other comparison for convenience
                    lcomp = (rop, min((lterm-1, rterm)))
                    rcomp = None
                # lterm >= {...} < rterm
                else:
                    # choose smaller upper bound and drop other comparison for convenience
                    lcomp = (lop, min((lterm, rterm-1)))
                    rcomp = None
"""