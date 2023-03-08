from copy import deepcopy
from functools import cached_property
from typing import TYPE_CHECKING, Optional, Set, Tuple, Union

from aspy.program.terms import Number
from aspy.program.expression import Expr
from aspy.program.literals import Guard, LiteralTuple
from aspy.program.literals.builtin import op2rel, GreaterEqual
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.operators import RelOp

from .statement import Fact, Rule

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.literals import Literal, PredicateLiteral
    from aspy.program.query import Query
    from aspy.program.substitution import Substitution
    from aspy.program.terms import Variable
    from aspy.program.variable_table import VariableTable

    from .statement import Statement


class ChoiceElement(Expr):
    """Choice element."""

    def __init__(
        self,
        atom: "PredicateLiteral",
        literals: Optional[Union[Tuple["Literal", ...], "LiteralTuple"]] = None,
    ) -> None:
        if literals is None:
            literals = LiteralTuple()

        self.atom = atom
        self.literals = (
            literals if isinstance(literals, LiteralTuple) else LiteralTuple(*literals)
        )

    def __eq__(self, other: Expr) -> bool:
        return (
            isinstance(other, ChoiceElement)
            and self.atom == other.atom
            and self.literals == other.literals
        )

    def __hash__(self) -> int:
        return hash(("choice element", self.atom, self.literals))

    def __str__(self) -> str:
        return str(self.atom) + (
            f":{','.join([str(literal) for literal in self.literals])}"
            if self.literals
            else ""
        )

    @property
    def head(self) -> LiteralTuple:
        return LiteralTuple(self.atom)

    @property
    def body(self) -> LiteralTuple:
        return self.literals

    @cached_property
    def ground(self) -> bool:
        return self.atom.ground and self.literals.ground

    def pos_occ(self) -> Set["PredicateLiteral"]:
        return self.atom.pos_occ().union(self.literals.pos_occ())

    def neg_occ(self) -> Set["PredicateLiteral"]:
        return self.atom.neg_occ().union(self.literals.neg_occ())

    def vars(self) -> Set["Variable"]:
        return self.atom.vars().union(self.literals.vars())

    def global_vars(self, statement: Optional["Statement"] = None) -> Set["Variable"]:
        return self.vars()

    def safety(
        self, rule: Optional[Union["Statement", "Query"]] = None
    ) -> SafetyTriplet:
        raise ValueError(
            "Safety characterization for choice elements is undefined without context."  # noqa
        )

    def substitute(self, subst: "Substitution") -> "ChoiceElement":
        return ChoiceElement(
            self.atom.substitute(subst),
            self.literals.substitute(subst),
        )

    def match(self, other: Expr) -> Set["Substitution"]:
        raise Exception("Matching for choice elements is not defined.")

    def replace_arith(self, var_table: "VariableTable") -> "ChoiceElement":
        return ChoiceElement(
            self.atom.replace_arith(var_table),
            self.literals.replace_arith(var_table),
        )


class Choice(Expr):
    """Choice."""

    def __init__(
        self,
        elements: Tuple[ChoiceElement],
        guards: Optional[Union["Guard", Tuple["Guard", ...]]] = None,
    ):
        # initialize left and right guard to 'None'
        self.lguard, self.rguard = None, None

        if guards is None:
            guards = tuple()

        # single guard specified
        if isinstance(guards, Guard):
            # wrap in tuple
            guards = (guards,)
        # guard tuple specified
        elif isinstance(guards, Tuple) and len(guards) > 2:
            raise ValueError("Choice expression allows at most two guards.")

        # process guards
        for guard in guards:
            if guard is None:
                continue

            if guard.right:
                if self.rguard is not None:
                    raise ValueError(
                        "Multiple right guards specified for choice expression."
                    )
                self.rguard = guard
            else:
                if self.lguard is not None:
                    raise ValueError(
                        "Multiple left guards specified for choice expression."
                    )
                self.lguard = guard

        self.elements = elements

    def __eq__(self, other: Expr) -> bool:
        return (
            isinstance(other, Choice)
            and set(self.elements) == set(other.elements)
            and self.guards == other.guards
        )

    def __hash__(self) -> int:
        return hash(("choice", self.elements, self.guards))

    def __str__(self) -> str:
        elements_str = ";".join([str(literal) for literal in self.elements])
        lguard_str = f"{str(self.lguard)} " if self.lguard is not None else ""
        rguard_str = f" {str(self.rguard)}" if self.rguard is not None else ""

        return f"{lguard_str}{{{elements_str}}}{rguard_str}"

    @cached_property
    def ground(self) -> bool:
        return all(element.ground for element in self.elements)

    @property
    def guards(self) -> Tuple[Union["Guard", None], Union["Guard", None]]:
        return (self.lguard, self.rguard)

    def invars(self) -> Set["Variable"]:
        # TODO: correct ???
        return set().union(*tuple(element.vars() for element in self.elements))

    def outvars(self) -> Set["Variable"]:
        # TODO: correct ???
        return set().union(
            *tuple(guard.bound.vars() for guard in self.guards if guard is not None)
        )

    def vars(self) -> Set["Variable"]:
        return self.invars().union(self.outvars())

    def global_vars(self, statement: "Statement") -> Set["Variable"]:
        return self.vars().intersection(statement.global_vars())

    def pos_occ(self) -> Set["PredicateLiteral"]:
        return set().union(*tuple(element.pos_occ() for element in self.elements))

    def neg_occ(self) -> Set["PredicateLiteral"]:
        return set().union(*tuple(element.neg_occ() for element in self.elements))

    def eval(self) -> bool:
        if not self.ground:
            raise ValueError("Cannot evaluate non-ground choice expression.")

        n_atoms = Number(len({element.atom for element in self.elements}))

        res = True

        for guard in self.guards:
            if guard is None:
                continue

            op, bound, right = guard

            # move operator to right-hand side (for canonical processing)
            if not right:
                op = -op

            if op in {RelOp.GREATER, RelOp.GREATER_OR_EQ}:
                # make sure there are enough elements to potentially satisfy bound
                res &= op2rel[op](n_atoms, bound).eval()
            elif op in {RelOp.EQUAL}:
                # make sure there are enough elements to potentially satisfy bound
                # and that bound is not negative (i.e., unsatisfiable)
                res &= (bound.val >= 0) and GreaterEqual(n_atoms, bound).eval()
            elif op in {RelOp.UNEQUAL}:
                # only edge case '!= 0', but no elements (i.e., unsatisfiable)
                res &= (bound.val != 0) or n_atoms.val > 0
            else:
                # make sure that upper bound can be satisfied
                res &= op2rel[op](Number(0), bound).eval()

        return res

    def safety(
        self, rule: Optional[Union["Statement", "Query"]] = None
    ) -> SafetyTriplet:
        raise Exception("Safety characterization not defined for choice expressions.")

    def substitute(self, subst: "Substitution") -> "Choice":
        if self.ground:
            return deepcopy(self)

        # substitute elements recursively
        elements = (element.substitute(subst) for element in self.elements)

        # substitute guard terms recursively
        guards = tuple(
            guard.substitute(subst) if guard is not None else None
            for guard in self.guards
        )

        return Choice(elements, guards)

    def replace_arith(self, var_table: "VariableTable") -> "Choice":
        # replace guards
        guards = (
            None if guard is None else guard.replace_arith(var_table)
            for guard in self.guards
        )

        return Choice(
            tuple(element.replace_arith(var_table) for element in self.elements),
            guards,
        )


class ChoiceFact(Fact):
    """Choice fact.

    Rule of form

        u_1 R_1 { h_1,...,h_m } R_2 u_2 :- .

    for classical atoms h_1,...,h_m, terms u_1,u_2 and comparison operators R_1,R_2.
    The symbol ':-' may be omitted.

    TODO: R_1, R_2 may be omitted
    TODO: u_1,R_1 u_2,R_2 may be omitted.

    Semantically, any answer set may include any subset of {h_1,...,h_m} (including the empty set).
    """  # noqa

    def __init__(self, head: Choice, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.choice = head

    def __eq__(self, other: Expr) -> bool:
        return isinstance(other, ChoiceFact) and self.head == other.head

    def __hash__(self) -> int:
        return hash(("choice fact", self.head))

    def __str__(self) -> str:
        return f"{{{','.join([str(literal) for literal in self.head.elements])}}}."

    @property
    def body(self) -> LiteralTuple:
        return LiteralTuple()

    @property
    def extended_body(self) -> LiteralTuple:
        return self.choice.literals

    @cached_property
    def safe(self) -> bool:
        return len(self.vars()) > 0

    @cached_property
    def ground(self) -> bool:
        return self.head.ground

    def safety(self, rule: Optional["Statement"]) -> "SafetyTriplet":
        raise Exception("Safety characterization for choice facts not supported yet.")

    def substitute(self, subst: "Substitution") -> "ChoiceFact":
        if self.ground:
            return deepcopy(self)

        return ChoiceFact(self.head.substitute(subst))


class ChoiceRule(Rule):
    """Choice rule.

    Rule of form:

        u_1 R_1 { h_1 ; ... ; h_m } R_2 u_2 :- b_1,...,b_n .

    for classical atoms h_1,...,h_m, literals b_1,...,b_n, terms u_1,u_2 and comparison operators R_1,R_2.

    Semantically, any answer set that includes b_1,...,b_n may also include any subset of {h_1,...,h_m} (including the empty set).
    """  # noqa

    def __init__(self, head: Choice, body: LiteralTuple, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.choice = head
        self.literals = body

    def __eq__(self, other: Expr) -> bool:
        return (
            isinstance(other, ChoiceRule)
            and self.head == other.head
            and self.literals == other.literals
        )

    def __hash__(self) -> int:
        return hash(("choice rule", self.head, self.literals))

    def __str__(self) -> str:
        return (
            f"{str(self.head)} :- {', '.join([str(literal) for literal in self.body])}."
        )

    @property
    def head(self) -> Choice:
        # TODO: correct?
        return self.choice

    @property
    def body(self) -> LiteralTuple:
        return self.literals

    @property
    def extended_body(self) -> LiteralTuple:
        return LiteralTuple(*self.literals, *self.choice.literals)

    @cached_property
    def safe(self) -> bool:
        raise Exception()

        global_vars = self.global_vars(self)
        body_safety = SafetyTriplet.closure(self.body.safety(self))

        return body_safety == SafetyTriplet(global_vars)

    @cached_property
    def ground(self) -> bool:
        return self.head.ground and self.body.ground

    def safety(self, rule: Optional["Statement"]) -> "SafetyTriplet":
        raise Exception("Safety characterization for choice rules not supported yet.")

    def substitute(self, subst: "Substitution") -> "ChoiceRule":
        if self.ground:
            return deepcopy(self)

        return ChoiceRule(self.head.substitute(subst), self.body.substitute(subst))
