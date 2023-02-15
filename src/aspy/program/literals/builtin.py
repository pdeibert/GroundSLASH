from typing import Set, Tuple, Optional, Union, TYPE_CHECKING
from abc import ABC, abstractmethod
from functools import cached_property

from aspy.program.safety_characterization import SafetyTriplet, SafetyRule
from aspy.program.substitution import Substitution

from .literal import Literal

if TYPE_CHECKING:
    from aspy.program.expression import Expr
    from aspy.program.terms import Term, Variable
    from aspy.program.statements import Statement
    from aspy.program.query import Query


class BuiltinLiteral(Literal, ABC):
    """Abstract base class for all built-in literals."""
    def __init__(self, loperand: "Term", roperand: "Term") -> None:
        # built-in literals are always positive
        super().__init__(naf=False)

        self.loperand = loperand
        self.roperand = roperand

    @cached_property
    def ground(self) -> bool:
        return self.loperand.ground and self.roperand.ground

    def pos(self) -> Set["Literal"]:
        return set()

    def neg(self) -> Set["Literal"]:
        return set()

    def vars(self, global_only: bool=False) -> Set["Variable"]:
        return self.loperand.vars(global_only).union(self.roperand.vars(global_only))

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> SafetyTriplet:
        return SafetyTriplet(unsafe=self.vars())

    @property
    def operands(self) -> Tuple["Term","Term"]:
        return (self.loperand, self.roperand)

    @abstractmethod
    def eval(self) -> bool:
        pass


class Equal(BuiltinLiteral):
    """Represents an equality comparison between terms."""
    def __str__(self) -> str:
        return f"{str(self.loperand)}={str(self.roperand)}"

    def safety(self, rule: Optional[Union["Statement","Query"]]=None, global_vars: Optional[Set["Variable"]]=None) -> SafetyTriplet:
        # overrides inherited safety method

        # get variables in both terms
        lvars = self.loperand.vars()
        rvars = self.roperand.vars()

        rules = set([SafetyRule(var, lvars) for var in rvars] + [SafetyRule(var, rvars) for var in lvars])

        return SafetyTriplet(unsafe=self.vars(), rules=rules).normalize()

    def eval(self) -> bool:
        loperand = self.loperand.eval()
        roperand = self.roperand.eval()

        return loperand.precedes(roperand) and roperand.precedes(loperand)

    def match(self, other: "Expr") -> Set[Substitution]:
        """Tries to match the expression with another one."""
        if isinstance(other, Equal):

            subst = Substitution()

            # match terms
            for (self_operand, other_operand) in zip(self.operands, other.operands):
                matches = self_operand.match(other_operand)

            # no match found
            if len(matches) == 0:
                return set()

            # try to merge substitutions
            try:
                subst.merge(matches[0])
            except:
                return set()
        
            return set([subst])
        else:
            return set()

    def substitute(self, subst: Substitution) -> "Equal":
        # substitute operands recursively
        operands = (operand.substitute(subst) for operand in self.operands)

        return Equal(*operands)


class Unequal(BuiltinLiteral):
    """Represents an unequality comparison between terms."""
    def __str__(self) -> str:
        return f"{str(self.loperand)}!={str(self.roperand)}"

    def eval(self) -> bool:
        loperand = self.loperand.eval()
        roperand = self.roperand.eval()

        return not ( loperand.precedes(roperand) and roperand.precedes(loperand) )

    def match(self, other: "Expr") -> Set[Substitution]:
        """Tries to match the expression with another one."""
        if isinstance(other, Unequal):

            subst = Substitution()

            # match terms
            for (self_operand, other_operand) in zip(self.operands, other.operands):
                matches = self_operand.match(other_operand)

            # no match found
            if len(matches) == 0:
                return set()

            # try to merge substitutions
            try:
                subst.merge(matches[0])
            except:
                return set()
        
            return set([subst])
        else:
            return set()

    def substitute(self, subst: Substitution) -> "Unequal":
        # substitute operands recursively
        operands = (operand.substitute(subst) for operand in self.operands)

        return Unequal(*operands)


class Less(BuiltinLiteral):
    """Represents a less-than comparison between terms."""
    def __str__(self) -> str:
        return f"{str(self.loperand)}<{str(self.roperand)}"

    def eval(self) -> bool:
        loperand = self.loperand.eval()
        roperand = self.roperand.eval()

        return loperand.precedes(roperand) and not roperand.precedes(loperand)

    def match(self, other: "Expr") -> Set[Substitution]:
        """Tries to match the expression with another one."""
        if isinstance(other, Less):

            subst = Substitution()

            # match terms
            for (self_operand, other_operand) in zip(self.operands, other.operands):
                matches = self_operand.match(other_operand)

            # no match found
            if len(matches) == 0:
                return set()

            # try to merge substitutions
            try:
                subst.merge(matches[0])
            except:
                return set()
        
            return set([subst])
        else:
            return set()

    def substitute(self, subst: Substitution) -> "Less":
        # substitute operands recursively
        operands = (operand.substitute(subst) for operand in self.operands)

        return Less(*operands)


class Greater(BuiltinLiteral):
    """Represents a greater-than comparison between terms."""
    def __str__(self) -> str:
        return f"{str(self.loperand)}>{str(self.roperand)}"

    def eval(self) -> bool:
        loperand = self.loperand.eval()
        roperand = self.roperand.eval()

        return not loperand.precedes(roperand) and roperand.precedes(loperand)

    def match(self, other: "Expr") -> Set[Substitution]:
        """Tries to match the expression with another one."""
        if isinstance(other, Greater):

            subst = Substitution()

            # match terms
            for (self_operand, other_operand) in zip(self.operands, other.operands):
                matches = self_operand.match(other_operand)

            # no match found
            if len(matches) == 0:
                return set()

            # try to merge substitutions
            try:
                subst.merge(matches[0])
            except:
                return set()
        
            return set([subst])
        else:
            return set()

    def substitute(self, subst: Substitution) -> "Greater":
        # substitute operands recursively
        operands = (operand.substitute(subst) for operand in self.operands)

        return Greater(*operands)


class LessEqual(BuiltinLiteral):
    """Represents a less-or-equal-than comparison between terms."""
    def __str__(self) -> str:
        return f"{str(self.loperand)}<={str(self.roperand)}"

    def eval(self) -> bool:
        loperand = self.loperand.eval()
        roperand = self.roperand.eval()

        return loperand.precedes(roperand)

    def match(self, other: "Expr") -> Set[Substitution]:
        """Tries to match the expression with another one."""
        if isinstance(other, LessEqual):

            subst = Substitution()

            # match terms
            for (self_operand, other_operand) in zip(self.operands, other.operands):
                matches = self_operand.match(other_operand)

            # no match found
            if len(matches) == 0:
                return set()

            # try to merge substitutions
            try:
                subst.merge(matches[0])
            except:
                return set()
        
            return set([subst])
        else:
            return set()

    def substitute(self, subst: Substitution) -> "LessEqual":
        # substitute operands recursively
        operands = (operand.substitute(subst) for operand in self.operands)

        return LessEqual(*operands)


class GreaterEqual(BuiltinLiteral):
    """Represents a greater-or-equal-than comparison between terms."""
    def __str__(self) -> str:
        return f"{str(self.loperand)}>={str(self.roperand)}"

    def eval(self) -> bool:
        loperand = self.loperand.eval()
        roperand = self.roperand.eval()

        return roperand.precedes(loperand)

    def match(self, other: "Expr") -> Set[Substitution]:
        """Tries to match the expression with another one."""
        if isinstance(other, GreaterEqual):

            subst = Substitution()

            # match terms
            for (self_operand, other_operand) in zip(self.operands, other.operands):
                matches = self_operand.match(other_operand)

            # no match found
            if len(matches) == 0:
                return set()

            # try to merge substitutions
            try:
                subst.merge(matches[0])
            except:
                return set()
        
            return set([subst])
        else:
            return set()

    def substitute(self, subst: Substitution) -> "GreaterEqual":
        # substitute operands recursively
        operands = (operand.substitute(subst) for operand in self.operands)

        return GreaterEqual(*operands)