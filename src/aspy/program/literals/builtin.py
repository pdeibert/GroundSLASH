from abc import ABC, abstractmethod
from copy import deepcopy
from functools import cached_property
from typing import TYPE_CHECKING, Optional, Set, Tuple, Union

from aspy.program.operators import RelOp
from aspy.program.safety_characterization import SafetyRule, SafetyTriplet
from aspy.program.substitution import Substitution
from aspy.program.terms import ArithTerm, Number, TermTuple

from .literal import Literal

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.expression import Expr
    from aspy.program.query import Query
    from aspy.program.statements import Statement
    from aspy.program.terms import Term, Variable
    from aspy.program.variable_table import VariableTable


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

    def pos_occ(self) -> Set["Literal"]:
        return set()

    def neg_occ(self) -> Set["Literal"]:
        return set()

    def vars(self, global_only: bool = False) -> Set["Variable"]:
        return self.loperand.vars(global_only).union(self.roperand.vars(global_only))

    def safety(
        self, rule: Optional[Union["Statement", "Query"]] = None, global_vars: Optional[Set["Variable"]] = None
    ) -> SafetyTriplet:
        return SafetyTriplet(unsafe=self.vars())

    @property
    def operands(self) -> Tuple["Term", "Term"]:
        return (self.loperand, self.roperand)

    @abstractmethod  # pragma: no cover
    def eval(self) -> bool:
        pass

    def replace_arith(self, var_table: "VariableTable") -> "BuiltinLiteral":
        return type(self)(self.loperand.replace_arith(var_table), self.roperand.replace_arith(var_table))


class Equal(BuiltinLiteral):
    """Represents an equality comparison between terms."""

    def __str__(self) -> str:
        return f"{str(self.loperand)}={str(self.roperand)}"

    def __eq__(self, other: "Expr") -> bool:
        return isinstance(other, Equal) and self.loperand == other.loperand and self.roperand == other.roperand

    def __hash__(self) -> int:
        return hash(("equal", self.loperand, self.roperand))

    def safety(
        self, rule: Optional[Union["Statement", "Query"]] = None, global_vars: Optional[Set["Variable"]] = None
    ) -> SafetyTriplet:
        # overrides inherited safety method

        # get variables
        lvars = self.loperand.vars()
        rvars = self.roperand.vars()

        lsafety = self.loperand.safety()
        rsafety = self.roperand.safety()

        rules = {SafetyRule(var, lvars.copy()) for var in rsafety.safe}.union(
            {SafetyRule(var, rvars.copy()) for var in lsafety.safe}
        )

        return SafetyTriplet(unsafe=lvars.union(rvars), rules=rules).normalize()

    def eval(self) -> bool:
        if not (self.loperand.ground and self.roperand.ground):
            raise ValueError("Cannot evaluate built-in literal with non-ground terms")

        loperand = Number(self.loperand.eval()) if isinstance(self.loperand, ArithTerm) else self.loperand
        roperand = Number(self.roperand.eval()) if isinstance(self.roperand, ArithTerm) else self.roperand

        return loperand.precedes(roperand) and roperand.precedes(loperand)

    def match(self, other: "Expr") -> Optional[Substitution]:
        """Tries to match the expression with another one."""
        if isinstance(other, Equal):
            return TermTuple(*self.operands).match(TermTuple(*other.operands))

        return None

    def substitute(self, subst: Substitution) -> "Equal":
        if self.ground:
            return deepcopy(self)

        # substitute operands recursively
        operands = (operand.substitute(subst) for operand in self.operands)

        return Equal(*operands)


class Unequal(BuiltinLiteral):
    """Represents an unequality comparison between terms."""

    def __str__(self) -> str:
        return f"{str(self.loperand)}!={str(self.roperand)}"

    def __eq__(self, other: "Expr") -> bool:
        return isinstance(other, Unequal) and self.loperand == other.loperand and self.roperand == other.roperand

    def __hash__(self) -> int:
        return hash(("unequal", self.loperand, self.roperand))

    def eval(self) -> bool:
        if not (self.loperand.ground and self.roperand.ground):
            raise ValueError("Cannot evaluate built-in literal with non-ground terms")

        loperand = Number(self.loperand.eval()) if isinstance(self.loperand, ArithTerm) else self.loperand
        roperand = Number(self.roperand.eval()) if isinstance(self.roperand, ArithTerm) else self.roperand

        return not (loperand.precedes(roperand) and roperand.precedes(loperand))

    def match(self, other: "Expr") -> Set[Substitution]:
        """Tries to match the expression with another one."""
        if isinstance(other, Unequal):
            return TermTuple(*self.operands).match(TermTuple(*other.operands))

        return None

    def substitute(self, subst: Substitution) -> "Unequal":
        if self.ground:
            return deepcopy(self)

        # substitute operands recursively
        operands = (operand.substitute(subst) for operand in self.operands)

        return Unequal(*operands)


class Less(BuiltinLiteral):
    """Represents a less-than comparison between terms."""

    def __str__(self) -> str:
        return f"{str(self.loperand)}<{str(self.roperand)}"

    def __eq__(self, other: "Expr") -> bool:
        return isinstance(other, Less) and self.loperand == other.loperand and self.roperand == other.roperand

    def __hash__(self) -> int:
        return hash(("less", self.loperand, self.roperand))

    def eval(self) -> bool:
        if not (self.loperand.ground and self.roperand.ground):
            raise ValueError("Cannot evaluate built-in literal with non-ground terms")

        loperand = Number(self.loperand.eval()) if isinstance(self.loperand, ArithTerm) else self.loperand
        roperand = Number(self.roperand.eval()) if isinstance(self.roperand, ArithTerm) else self.roperand

        return loperand.precedes(roperand) and not roperand.precedes(loperand)

    def match(self, other: "Expr") -> Set[Substitution]:
        """Tries to match the expression with another one."""
        if isinstance(other, Less):
            return TermTuple(*self.operands).match(TermTuple(*other.operands))

        return None

    def substitute(self, subst: Substitution) -> "Less":
        if self.ground:
            return deepcopy(self)

        # substitute operands recursively
        operands = (operand.substitute(subst) for operand in self.operands)

        return Less(*operands)


class Greater(BuiltinLiteral):
    """Represents a greater-than comparison between terms."""

    def __str__(self) -> str:
        return f"{str(self.loperand)}>{str(self.roperand)}"

    def __eq__(self, other: "Expr") -> bool:
        return isinstance(other, Greater) and self.loperand == other.loperand and self.roperand == other.roperand

    def __hash__(self) -> int:
        return hash(("greater", self.loperand, self.roperand))

    def eval(self) -> bool:
        if not (self.loperand.ground and self.roperand.ground):
            raise ValueError("Cannot evaluate built-in literal with non-ground terms")

        loperand = Number(self.loperand.eval()) if isinstance(self.loperand, ArithTerm) else self.loperand
        roperand = Number(self.roperand.eval()) if isinstance(self.roperand, ArithTerm) else self.roperand

        return not loperand.precedes(roperand) and roperand.precedes(loperand)

    def match(self, other: "Expr") -> Set[Substitution]:
        """Tries to match the expression with another one."""
        if isinstance(other, Greater):
            return TermTuple(*self.operands).match(TermTuple(*other.operands))

        return None

    def substitute(self, subst: Substitution) -> "Greater":
        if self.ground:
            return deepcopy(self)

        # substitute operands recursively
        operands = (operand.substitute(subst) for operand in self.operands)

        return Greater(*operands)


class LessEqual(BuiltinLiteral):
    """Represents a less-or-equal-than comparison between terms."""

    def __str__(self) -> str:
        return f"{str(self.loperand)}<={str(self.roperand)}"

    def __eq__(self, other: "Expr") -> bool:
        return isinstance(other, LessEqual) and self.loperand == other.loperand and self.roperand == other.roperand

    def __hash__(self) -> int:
        return hash(("less equal", self.loperand, self.roperand))

    def eval(self) -> bool:
        if not (self.loperand.ground and self.roperand.ground):
            raise ValueError("Cannot evaluate built-in literal with non-ground terms")

        loperand = Number(self.loperand.eval()) if isinstance(self.loperand, ArithTerm) else self.loperand
        roperand = Number(self.roperand.eval()) if isinstance(self.roperand, ArithTerm) else self.roperand

        return loperand.precedes(roperand)

    def match(self, other: "Expr") -> Set[Substitution]:
        """Tries to match the expression with another one."""
        if isinstance(other, LessEqual):
            return TermTuple(*self.operands).match(TermTuple(*other.operands))

        return None

    def substitute(self, subst: Substitution) -> "LessEqual":
        if self.ground:
            return deepcopy(self)

        # substitute operands recursively
        operands = (operand.substitute(subst) for operand in self.operands)

        return LessEqual(*operands)


class GreaterEqual(BuiltinLiteral):
    """Represents a greater-or-equal-than comparison between terms."""

    def __str__(self) -> str:
        return f"{str(self.loperand)}>={str(self.roperand)}"

    def __eq__(self, other: "Expr") -> bool:
        return isinstance(other, GreaterEqual) and self.loperand == other.loperand and self.roperand == other.roperand

    def __hash__(self) -> int:
        return hash(("greater equal", self.loperand, self.roperand))

    def eval(self) -> bool:
        if not (self.loperand.ground and self.roperand.ground):
            raise ValueError("Cannot evaluate built-in literal with non-ground terms")

        loperand = Number(self.loperand.eval()) if isinstance(self.loperand, ArithTerm) else self.loperand
        roperand = Number(self.roperand.eval()) if isinstance(self.roperand, ArithTerm) else self.roperand

        return roperand.precedes(loperand)

    def match(self, other: "Expr") -> Set[Substitution]:
        """Tries to match the expression with another one."""
        if isinstance(other, GreaterEqual):
            return TermTuple(*self.operands).match(TermTuple(*other.operands))

        return None

    def substitute(self, subst: Substitution) -> "GreaterEqual":
        if self.ground:
            return deepcopy(self)

        # substitute operands recursively
        operands = (operand.substitute(subst) for operand in self.operands)

        return GreaterEqual(*operands)


# maps relational operators to their corresponding AST constructs
op2rel = {
    RelOp.EQUAL: Equal,
    RelOp.UNEQUAL: Unequal,
    RelOp.LESS: Less,
    RelOp.GREATER: Greater,
    RelOp.LESS_OR_EQ: LessEqual,
    RelOp.GREATER_OR_EQ: GreaterEqual,
}
