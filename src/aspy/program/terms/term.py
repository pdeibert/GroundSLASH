from abc import ABC, abstractmethod
from copy import deepcopy
from functools import cached_property
from typing import TYPE_CHECKING, Iterable, Optional, Set, Tuple, Union

import aspy
from aspy.program.expression import Expr
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.substitution import AssignmentError, Substitution
from aspy.program.symbol_table import SYM_CONST_RE, VARIABLE_RE

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.query import Query
    from aspy.program.statements import Statement
    from aspy.program.variable_table import VariableTable


class Term(Expr, ABC):
    """Abstract base class for all terms."""

    @abstractmethod  # pragma: no cover
    def __eq__(self, other: Expr) -> bool:
        pass

    @abstractmethod  # pragma: no cover
    def precedes(self, other: "Term") -> bool:
        """Defines the total ordering operator defined for terms in ASP-Core-2."""
        pass

    def vars(self, global_only: bool = False) -> Set["Variable"]:
        return set()

    def safety(
        self, rule: Optional[Union["Statement", "Query"]] = None, global_vars: Optional[Set["Variable"]] = None
    ) -> SafetyTriplet:
        return SafetyTriplet()

    def replace_arith(self, var_table: "VariableTable") -> "Term":
        return deepcopy(self)

    def substitute(self, subst: Substitution) -> "Expr":
        return deepcopy(self)

    def match(self, other: Expr) -> Optional[Substitution]:
        """Tries to match the expression with another one."""
        # empty substitution
        return Substitution() if self == other else None


class Infimum(Term):
    """Least element in the total ordering for terms."""

    ground: bool = True

    def __str__(self) -> str:
        return "#inf"

    def __eq__(self, other: Expr) -> str:
        return isinstance(other, Infimum)

    def __hash__(self) -> int:
        return hash(("inf",))

    def precedes(self, other: Term) -> bool:
        if not other.ground:
            raise ValueError("Cannot compare total ordering with non-ground arithmetic terms or variables")

        return True


class Supremum(Term):
    """Greatest element in the total ordering for terms."""

    ground: bool = True

    def __str__(self) -> str:
        return "#sup"

    def __eq__(self, other: Expr) -> str:
        return isinstance(other, Supremum)

    def __hash__(self) -> int:
        return hash(("sup",))

    def precedes(self, other: Term) -> bool:
        if not other.ground:
            raise ValueError("Cannot compare total ordering with non-ground arithmetic terms or variables")

        return True if isinstance(other, Supremum) else False


class Variable(Term):
    """Represents a variable."""

    ground: bool = False

    def __init__(self, val: str) -> None:
        # check if variable name is valid
        if aspy.debug() and not (isinstance(val, str) and VARIABLE_RE.fullmatch(val)):
            raise ValueError(f"Invalid value for {type(self)}: {val}")

        self.val = val

    def __str__(self) -> str:
        return self.val

    def __eq__(self, other: Expr) -> str:
        return isinstance(other, Variable) and other.val == self.val

    def __hash__(self) -> int:
        return hash(("var", self.val))

    def precedes(self, other: Term) -> bool:
        raise Exception("Total ordering is undefined for non-ground terms.")

    def vars(self, global_only: bool = False) -> Set["Variable"]:
        return {self}

    def safety(
        self, rule: Optional[Union["Statement", "Query"]] = None, global_vars: Optional[Set["Variable"]] = None
    ) -> SafetyTriplet:
        return SafetyTriplet({self})

    def simplify(self) -> "Number":
        """Used in arithmetical terms."""
        return Variable(self.val)

    def match(self, other: Expr) -> Optional[Substitution]:
        """Tries to match the expression with another one."""
        return Substitution({self: other}) if not self == other else Substitution()

    def substitute(self, subst: Substitution) -> Term:
        return subst[self]


class AnonVariable(Variable):
    """Represents an anonymous variable."""

    def __init__(self, id: int) -> None:

        # check if id is valid
        if aspy.debug() and id < 0:
            raise ValueError(f"Invalid value for {type(self)}: {id}")

        self.val = f"_{id}"
        self.id = id

    def safety(
        self, rule: Optional[Union["Statement", "Query"]] = None, global_vars: Optional[Set["Variable"]] = None
    ) -> SafetyTriplet:
        return SafetyTriplet()

    def __eq__(self, other: Expr) -> str:
        return isinstance(other, AnonVariable) and other.val == self.val and other.id == self.id

    def __hash__(self) -> int:
        return hash(("anon var", self.val))

    def simplify(self) -> "Number":
        """Used in arithmetical terms."""
        return AnonVariable(self.id)


class Number(Term):
    """Represents a number."""

    ground: bool = True

    def __init__(self, val: int) -> None:
        self.val = val

    def __add__(self, other) -> "Number":
        return Number(self.val + other.val)

    def __sub__(self, other) -> "Number":
        return Number(self.val - other.val)

    def __mul__(self, other) -> "Number":
        return Number(self.val * other.val)

    def __floordiv__(self, other) -> "Number":
        return Number(self.val // other.val)

    def __neg__(self) -> "Number":
        return Number(-self.val)

    def __abs__(self) -> "Number":
        return Number(abs(self.val))

    def __str__(self) -> str:
        return str(self.val)

    def __eq__(self, other: Expr) -> str:
        return isinstance(other, Number) and other.val == self.val

    def __hash__(self) -> int:
        return hash(("num", self.val))

    def precedes(self, other: Term) -> bool:
        if not other.ground:
            raise ValueError("Cannot compare total ordering with non-ground arithmetic terms or variables")

        if isinstance(other, Infimum):
            return False
        elif isinstance(other, Number):
            return self.val <= other.val
        else:
            return True

    def simplify(self) -> "Number":
        """Used in arithmetical terms."""
        return Number(self.val)

    def eval(self) -> int:
        return self.val


class SymbolicConstant(Term):
    """Represents a symbolic constant."""

    ground: bool = True

    def __init__(self, val: str) -> None:

        # check if symbolic constant name is valid
        if aspy.debug() and not SYM_CONST_RE.fullmatch(val):  # TODO: alpha, eta, eps?
            raise ValueError(f"Invalid value for {type(self)}: {val}")

        self.val = val

    def __str__(self) -> str:
        return self.val

    def __str__(self) -> str:
        return str(self.val)

    def __eq__(self, other: Expr) -> str:
        return isinstance(other, SymbolicConstant) and other.val == self.val

    def __hash__(self) -> int:
        return hash(("symbolic const", self.val))

    def precedes(self, other: Term) -> bool:
        if not other.ground:
            raise ValueError("Cannot compare total ordering with non-ground arithmetic terms or variables")

        if isinstance(other, (Infimum, Number)):
            return False
        elif isinstance(other, SymbolicConstant):
            return self.val <= other.val
        else:
            return True


class String(Term):
    """Represents a string."""

    ground: bool = True

    def __init__(self, val: str) -> None:
        self.val = val

    def __str__(self) -> str:
        return f'"{self.val}"'

    def __eq__(self, other: Expr) -> bool:
        return isinstance(other, String) and other.val == self.val

    def __hash__(self) -> int:
        return hash(("str", self.val))

    def precedes(self, other: Term) -> bool:
        if not other.ground:
            raise ValueError("Cannot compare total ordering with non-ground arithmetic terms or variables")

        if isinstance(other, (Infimum, Number, SymbolicConstant)):
            return False
        elif isinstance(other, String):
            return self.val <= other.val
        else:
            return True


class TermTuple():
    """Represents a collection of terms."""
    def __init__(self, *terms: Term) -> None:
        self.terms = terms

    def __len__(self) -> int:
        return len(self.terms)

    def __eq__(self, other: "TermTuple") -> bool:
        return isinstance(other, TermTuple) and len(self) == len(other) and all(t1 == t2 for t1, t2 in zip(self, other))

    def __hash__(self) -> int:
        return hash( ("term tuple", *self.terms) )

    def __iter__(self) -> Iterable[Term]:
        return iter(self.terms)

    def __add__(self, other: "TermTuple") -> "TermTuple":
        return TermTuple(*self.terms, *other.terms)

    def __getitem__(self, index: int) -> "Term":
        return self.terms[index]

    @cached_property
    def ground(self) -> bool:
        return all(term.ground for term in self.terms)

    def substitute(self, subst: "Substitution") -> "TermTuple":
        if self.ground:
            return deepcopy(self)

        # substitute terms recursively
        terms = (term.substitute(subst) for term in self)

        return TermTuple(*terms)

    def match(self, other: Expr) -> Optional[Substitution]:
        # raise Exception("Matching for term tuples is not supported yet.")

        if not (isinstance(other, TermTuple) and len(self) == len(other)):
            return None

        subst = Substitution()

        for term1, term2 in zip(self.terms, other.terms):
            match = term1.match(term2)

            if match is None:
                return None

            try:
                subst = subst + match
            except AssignmentError:
                return None

        return subst

    def vars(self, global_only: bool = False) -> Set["Variable"]:
        return set().union(*tuple(term.vars(global_only) for term in self.terms))

    def safety(
        self, rule: Optional[Union["Statement", "Query"]] = None, global_vars: Optional[Set["Variable"]] = None
    ) -> Tuple["SafetyTriplet", ...]:
        return tuple(term.safety(rule=rule, global_vars=global_vars) for term in self.terms)

    def replace_arith(self, var_table: "VariableTable") -> "TermTuple":
        return TermTuple(*tuple(term.replace_arith(var_table) for term in self.terms))

    @cached_property
    def weight(self) -> int:
        """Used in aggregates."""
        if len(self.terms) > 0 and isinstance(self.terms[0], Number):
            return self.terms[0].val

        return 0

    @cached_property
    def pos_weight(self) -> int:
        """Used in aggregates."""
        if len(self.terms) > 0 and isinstance(self.terms[0], Number):
            return max(self.terms[0].val, 0)

        return 0

    @cached_property
    def neg_weight(self) -> int:
        """Used in aggregates."""
        if len(self.terms) > 0 and isinstance(self.terms[0], Number):
            return min(self.terms[0].val, 0)

        return 0
