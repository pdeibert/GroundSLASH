from copy import deepcopy
from functools import cached_property
from itertools import chain, combinations
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    Iterator,
    Optional,
    Set,
    Tuple,
    Union,
)

from aspy.program.expression import Expr
from aspy.program.literals import (
    AggrLiteral,
    ChoicePlaceholder,
    Guard,
    LiteralCollection,
)
from aspy.program.literals.builtin import GreaterEqual, op2rel
from aspy.program.operators import RelOp
from aspy.program.safety_characterization import SafetyTriplet
from aspy.program.terms import Number

from .normal import NormalRule
from .special import ChoiceBaseRule, ChoiceElemRule
from .statement import Statement

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.literals import AggrPlaceholder, Literal, PredLiteral
    from aspy.program.query import Query
    from aspy.program.substitution import Substitution
    from aspy.program.terms import Term, Variable
    from aspy.program.variable_table import VariableTable

    from .special import AggrBaseRule, AggrElemRule


def powerset(element_iterable: Iterable[Any]) -> Iterator[Tuple[Any, ...]]:
    """From https://docs.python.org/3/library/itertools.html#itertools.combinations recipes."""  # noqa
    elements = list(element_iterable)
    return chain.from_iterable(
        combinations(elements, n_elements) for n_elements in range(len(elements) + 1)
    )


class ChoiceElement(Expr):
    """Choice element."""

    def __init__(
        self,
        atom: "PredLiteral",
        literals: Optional[Union[Tuple["Literal", ...], "LiteralCollection"]] = None,
    ) -> None:
        if literals is None:
            literals = LiteralCollection()

        self.atom = atom
        self.literals = (
            literals
            if isinstance(literals, LiteralCollection)
            else LiteralCollection(*literals)
        )

    def __eq__(self, other: "Any") -> bool:
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
    def head(self) -> LiteralCollection:
        return LiteralCollection(self.atom)

    @property
    def body(self) -> LiteralCollection:
        return self.literals

    @cached_property
    def ground(self) -> bool:
        return self.atom.ground and self.literals.ground

    def pos_occ(self) -> Set["PredLiteral"]:
        return self.atom.pos_occ().union(self.literals.pos_occ())

    def neg_occ(self) -> Set["PredLiteral"]:
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

    def match(self, other: "Expr") -> Set["Substitution"]:
        raise Exception("Matching for choice elements is not defined.")

    def replace_arith(self, var_table: "VariableTable") -> "ChoiceElement":
        return ChoiceElement(
            self.atom.replace_arith(var_table),
            self.literals.replace_arith(var_table),
        )

    def satisfied(self, literals: Set["Literal"]) -> bool:
        # check if all condition literals are part of the specified set
        return all(literal in literals for literal in self.literals)


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

    def __eq__(self, other: "Any") -> bool:
        return (
            isinstance(other, Choice)
            and set(self.elements) == set(other.elements)
            and self.guards == other.guards
        )

    def __hash__(self) -> int:
        return hash(("choice", frozenset(self.elements), self.guards))

    def __str__(self) -> str:
        elements_str = ";".join([str(literal) for literal in self.elements])
        lguard_str = f"{str(self.lguard)} " if self.lguard is not None else ""
        rguard_str = f" {str(self.rguard)}" if self.rguard is not None else ""

        return f"{lguard_str}{{{elements_str}}}{rguard_str}"

    def __iter__(self) -> Iterator[ChoiceElement]:
        return iter(self.elements)

    @property
    def head(self) -> LiteralCollection:
        return LiteralCollection(*tuple(element.atom for element in self.elements))

    @property
    def body(self) -> LiteralCollection:
        return LiteralCollection(
            *chain(*tuple(element.literals for element in self.elements))
        )

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
        # TODO: correct ?
        glob_body_vars = statement.body.global_vars()

        return self.outvars().union(self.invars().intersection(glob_body_vars))
        # return self.head.vars().union(self.outvars())
        # return self.vars().intersection(statement.global_vars())
        # return set().union(
        #    self.outvars(),
        #    self.head.global_vars(statement),
        #    self.body.global_vars(statement),
        # )

    def pos_occ(self) -> Set["PredLiteral"]:
        return set().union(*tuple(element.pos_occ() for element in self.elements))

    def neg_occ(self) -> Set["PredLiteral"]:
        return set().union(*tuple(element.neg_occ() for element in self.elements))

    @classmethod
    def eval(
        cls, elements: Set["Literal"], guards: Tuple[Optional[Guard], Optional[Guard]]
    ) -> bool:
        if not all(element.ground for element in elements):
            raise ValueError("Cannot evaluate non-ground choice expression.")

        n_atoms = Number(len(elements))

        res = True

        for guard in guards:
            if guard is None:
                continue

            op, bound, right = guard

            # move operator to right-hand side (for canonical processing)
            if not right:
                op = -op

            if op in {RelOp.GREATER, RelOp.GREATER_OR_EQ}:
                # make sure there are enough elements to potentially satisfy bound
                res &= op.eval(n_atoms, bound)
            elif op in {RelOp.EQUAL}:
                # make sure there are enough elements to potentially satisfy bound
                # and that bound is not negative (i.e., unsatisfiable)
                res &= (bound.val >= 0) and GreaterEqual(n_atoms, bound).eval()
            elif op in {RelOp.UNEQUAL}:
                # only edge case '!= 0', but no elements (i.e., unsatisfiable)
                res &= (bound.val != 0) or n_atoms.val > 0
            else:
                # make sure that upper bound can be satisfied
                res &= op.eval(Number(0), bound)

        return res

    def propagate(
        self,
        guards: Tuple[Optional[Guard], Optional[Guard]],
        elements: Set["ChoiceElement"],
        literals_I: Set["Literal"],
        literals_J: Set["Literal"],
    ) -> bool:

        # TODO: avoid creating objects???
        # TODO
        """
        TODO:
        AggrPlaceholder
        ChoicePlaceholder
        PropBaseLiteral
        PropElemLiteral

        PropBaseRule
        PropElemRule
                ref_id
                element: Union["AggrElement", "ChoiceElement"]

        to check if deterministic:
        check if bound true and if != bound false
        or bound false (deterministic as it is unsatisfiable)
                -> important: do NOT count consequent literals as possible!
                -> rewrite as constraint!

        example:
                1 >= 1 and not 1 != 1 (deterministic)
                2 >= 1 and 2 != 1 (not deterministic)

        """
        # cache holding intermediate results (to avoid recomputation)
        propagation_cache = dict()
        # elements that are satisfied by I and J, respectively (initialize to None)
        elements_I = None
        elements_J = None

        def get_I_elements() -> Set["ChoiceElement"]:
            nonlocal elements_I

            if elements_I is None:
                elements_I = {
                    element for element in elements if element.satisfied(literals_I)
                }
            return elements_I

        def get_J_elements() -> Set["ChoiceElement"]:
            nonlocal elements_J

            if elements_J is None:
                elements_J = {
                    element for element in elements if element.satisfied(literals_J)
                }
            return elements_J

        def get_propagation_result(
            op: RelOp, bound: "Term", domain: Set["ChoiceElement"]
        ) -> bool:
            nonlocal propagation_cache

            if (op, bound) not in propagation_cache:
                propagation_cache[(op, bound)] = op2rel[op](
                    Number(len({element.atom for element in domain})), bound
                ).eval()
            return propagation_cache[(op, bound)]

        def propagate_subset(
            op,
            bound,
            elements_I: Set["ChoiceElement"],
            elements_J: Set["ChoiceElement"],
        ) -> bool:
            # test all combinations of subsets of candidates
            # TODO: may be complete overkill (hence, inefficient!)
            for X in powerset(
                {element.atom for element in elements_I.union(elements_J)}
            ):
                if op.eval(bound, Number(len(X))):
                    return True

            return False

        # running boolean tracking the current result of the propagation
        res = True

        for guard in guards:
            if guard is None:
                continue
            if res is False:
                break

            op, bound, right = guard

            # move operator to right-hand side (for canonical processing)
            if not right:
                op = -op

            if op in {RelOp.GREATER, RelOp.GREATER_OR_EQ}:
                # check upper bound
                res &= get_propagation_result(op, bound, get_J_elements())
            elif op in {RelOp.LESS, RelOp.LESS_OR_EQ}:
                # check lower bound
                res &= get_propagation_result(op, bound, set())
            elif op == RelOp.EQUAL:
                # check upper bound (TODO: suffices?)
                res &= get_propagation_result(
                    RelOp.GREATER_OR_EQ, bound, get_J_elements()
                )
            elif op == RelOp.UNEQUAL:
                # check if any subset of elements satisfies bound
                res &= propagate_subset(op, bound, get_I_elements(), get_J_elements())

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


class ChoiceRule(Statement):
    """Choice rule.

    Rule of form:

        u_1 R_1 { h_1 ; ... ; h_m } R_2 u_2 :- b_1,...,b_n .

    for classical atoms h_1,...,h_m, literals b_1,...,b_n, terms u_1,u_2 and comparison operators R_1,R_2.

    Semantically, any answer set that includes b_1,...,b_n may also include any subset of {h_1,...,h_m} (including the empty set).
    """  # noqa

    def __init__(
        self,
        head: Choice,
        body: Optional[Union[LiteralCollection, Iterable["Literal"]]] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        if body is None:
            body = tuple()

        # TODO: correctly infer determinism after propagation/grounding?
        self.deterministic: bool = False

        self.choice = head
        self.literals = (
            body if isinstance(body, LiteralCollection) else LiteralCollection(*body)
        )

    def __eq__(self, other: "Any") -> bool:
        return (
            isinstance(other, ChoiceRule)
            and self.head == other.head
            and self.literals == other.literals
        )

    def __hash__(self) -> int:
        return hash(("choice rule", self.head, self.literals))

    def __str__(self) -> str:
        return f"{str(self.head)}{f' :- {str(self.body)}' if self.body else ''}."

    @property
    def head(self) -> Choice:
        # TODO: correct?
        return self.choice

    @property
    def body(self) -> LiteralCollection:
        return self.literals

    def consequents(self) -> "LiteralCollection":
        return self.choice.head

    def antecedents(self) -> "LiteralCollection":
        return LiteralCollection(*self.literals, *self.choice.body)

    @cached_property
    def safe(self) -> bool:

        outside_glob_vars = self.body.global_vars().union(self.choice.outvars())

        for element in self.choice:
            global_vars = outside_glob_vars.union(element.head.global_vars())

            if LiteralCollection(*self.body, *element.body).safety(
                self
            ) != SafetyTriplet(global_vars):
                return False

        return True

    @cached_property
    def ground(self) -> bool:
        return self.head.ground and self.body.ground

    def safety(self, rule: Optional["Statement"] = None) -> "SafetyTriplet":
        raise Exception("Safety characterization for choice rules not supported yet.")

    def substitute(self, subst: "Substitution") -> "ChoiceRule":
        if self.ground:
            return deepcopy(self)

        return ChoiceRule(self.head.substitute(subst), self.body.substitute(subst))

    def replace_arith(self) -> "ChoiceRule":
        return ChoiceRule(
            self.head.replace_arith(self.var_table),
            self.body.replace_arith(self.var_table),
        )

    def rewrite_aggregates(
        self,
        aggr_counter: int,
        aggr_map: Dict[
            int,
            Tuple[
                "AggrLiteral",
                "AggrPlaceholder",
                "AggrBaseRule",
                Set["AggrElemRule"],
            ],
        ],
    ) -> "ChoiceRule":

        # global variables
        glob_vars = self.global_vars()

        # group literals
        non_aggr_literals = []
        aggr_literals = []

        for literal in self.body:
            (
                aggr_literals if isinstance(literal, AggrLiteral) else non_aggr_literals
            ).append(literal)

        # mapping from original literals to alpha literals
        alpha_map = dict()

        # local import due to circular import
        from .rewrite import rewrite_aggregate

        for literal in aggr_literals:
            # rewrite aggregate literal
            alpha_literal, eps_rule, eta_rules = rewrite_aggregate(
                literal, aggr_counter, glob_vars, non_aggr_literals
            )

            # map original aggregate literal to new alpha literal
            alpha_map[literal] = alpha_literal

            # store aggregate information
            aggr_map[aggr_counter] = (literal, alpha_literal, eps_rule, eta_rules)

            # increase aggregate counter
            aggr_counter += 1

        # replace original rule with modified one
        alpha_rule = ChoiceRule(
            self.choice,
            tuple(
                alpha_map[literal] if isinstance(literal, AggrLiteral) else literal
                for literal in self.body
            ),  # NOTE: restores original order of literals
        )

        return alpha_rule

    def assemble_aggregates(
        self, assembling_map: Dict["AggrPlaceholder", "AggrLiteral"]
    ) -> "ChoiceRule":
        return ChoiceRule(
            self.choice,
            *tuple(
                literal if literal not in assembling_map else assembling_map[literal]
                for literal in self.body
            ),
        )

    def rewrite_choices(
        self,
        choice_counter: int,
        choice_map: Dict[
            int,
            Tuple[
                "Choice",
                "ChoicePlaceholder",
                "ChoiceBaseRule",
                Set["ChoiceElemRule"],
            ],
        ],
    ) -> "NormalRule":

        # global variables
        glob_vars = self.global_vars()  # TODO: correct ???

        # local import due to circular import
        from .rewrite import rewrite_choice

        chi_literal, eps_rule, eta_rules = rewrite_choice(
            self.choice, choice_counter, glob_vars, self.literals
        )

        # store choice information
        choice_map[choice_counter] = (self.choice, chi_literal, eps_rule, eta_rules)

        # replace original rule with modified one
        chi_rule = NormalRule(chi_literal, *self.literals)

        return chi_rule
