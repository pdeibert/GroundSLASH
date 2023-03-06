from abc import ABC, abstractmethod
from functools import cached_property, reduce
from itertools import chain, combinations
from typing import TYPE_CHECKING, Any, Iterable, Iterator, Optional, Set, Tuple, Union

from aspy.program.expression import Expr
from aspy.program.literals.builtin import op2rel
from aspy.program.operators import AggrOp, RelOp
from aspy.program.safety_characterization import SafetyRule, SafetyTriplet
from aspy.program.terms import Infimum, Number, Supremum, TermTuple

from .guard import Guard
from .literal import Literal, LiteralTuple

if TYPE_CHECKING:  # pragma: no cover
    from aspy.program.query import Query
    from aspy.program.statements import Statement
    from aspy.program.substitution import Substitution
    from aspy.program.terms import Term, Variable
    from aspy.program.variable_table import VariableTable

    from .predicate import PredicateLiteral


def powerset(element_iterable: Iterable[Any]) -> Iterator[Tuple[Any, ...]]:
    """From https://docs.python.org/3/library/itertools.html#itertools.combinations recipes."""
    elements = list(element_iterable)
    return chain.from_iterable(combinations(elements, n_elements) for n_elements in range(len(elements) + 1))


class AggregateElement(Expr):
    """Represents an aggregate element."""

    def __init__(self, terms: Optional["TermTuple"] = None, literals: Optional["LiteralTuple"] = None) -> None:
        self.terms = terms if terms is not None else tuple()
        self.literals = literals if literals is not None else tuple()

    def __eq__(self, other: Expr) -> bool:
        return isinstance(other, AggregateElement) and self.terms == other.terms and self.literals == other.literals

    def __hash__(self) -> int:
        return hash(("aggr element", self.terms, self.literals))

    def __str__(self) -> str:
        return ",".join([str(term) for term in self.terms]) + (
            f":{','.join([str(literal) for literal in self.literals])}" if self.literals else ""
        )

    @property
    def head(self) -> "TermTuple":
        return self.terms

    @property
    def body(self) -> "LiteralTuple":
        return self.literals

    @cached_property
    def ground(self) -> bool:
        return all(term.ground for term in self.terms) and all(literal.ground for literal in self.literals)

    def pos_occ(self) -> Set["PredicateLiteral"]:
        return self.literals.pos_occ()

    def neg_occ(self) -> Set["PredicateLiteral"]:
        return self.literals.neg_occ()

    @property
    def weight(self) -> int:
        return self.terms.weight

    @property
    def pos_weight(self) -> int:
        return self.terms.pos_weight

    @property
    def neg_weight(self) -> int:
        return self.terms.neg_weight

    def satisfied(self, literals: Set["Literal"]) -> bool:
        # check if all condition literals are part of the specified set
        return all(literal in literals for literal in self.literals)

    def vars(self, global_only: bool = False) -> Set["Variable"]:
        return self.head.vars(global_only).union(self.body.vars(global_only))

    def safety(
        self, rule: Optional[Union["Statement", "Query"]] = None, global_vars: Optional[Set["Variable"]] = None
    ) -> SafetyTriplet:
        raise ValueError("Safety characterization for aggregate elements is undefined without context.")

    def substitute(self, subst: "Substitution") -> "AggregateElement":
        terms = TermTuple(*tuple(term.substitute(subst) for term in self.terms))
        literals = LiteralTuple(*tuple(literal.substitute(subst) for literal in self.literals))

        return AggregateElement(terms, literals)

    def match(self, other: Expr) -> Set["Substitution"]:
        raise Exception("Matching for aggregate elements not supported yet.")

    def replace_arith(self, var_table: "VariableTable") -> "AggregateElement":
        return AggregateElement(
            TermTuple(*self.terms.replace_arith(var_table)), LiteralTuple(*self.literals.replace_arith(var_table))
        )


class AggregateFunction(ABC):
    """Abstract base class for all aggregate functions."""

    def vars(self, global_only: bool = False, bound_only: bool = False) -> Set["Variable"]:
        return (
            set().union(*tuple(element.vars() for element in self.elements))
            if not (bound_only or global_only)
            else set()
        )  # TODO: does not quite follow the definition in ASP-Core-2?

    @abstractmethod  # pragma: no cover
    def eval(self, elements: Set["TermTuple"]) -> Number:
        pass

    @abstractmethod  # pragma: no cover
    def base(self) -> "Term":
        pass

    @abstractmethod  # pragma: no cover
    def propagate(self) -> bool:
        pass


class AggregateCount(AggregateFunction):
    """Represents a 'count' aggregate."""

    def __str__(self) -> str:
        return f"#count"

    def __eq__(self, other: Expr) -> bool:
        return isinstance(other, AggregateCount)

    def __hash__(self) -> int:
        return hash(("aggregate count"))

    def eval(self, elements: Set["TermTuple"]) -> Number:
        """Returns the number of satisfied aggregate elements."""
        return Number(len(elements))

    def base(self) -> Number:
        return Number(0)

    def propagate(
        self,
        guards: Tuple[Optional[Guard], Optional[Guard]],
        elements: Set["AggregateElement"],
        I: Set["Literal"],
        J: Set["Literal"],
    ) -> bool:

        # cache holding intermediate results (to avoid recomputation)
        propagation_cache = dict()
        # elements that are satisfied by I and J, respectively (initialize to None)
        I_elements = None
        J_elements = None

        def get_I_elements() -> Set["AggregateElement"]:
            nonlocal I_elements

            if I_elements is None:
                I_elements = {element for element in elements if element.satisfied(I)}
            return I_elements

        def get_J_elements() -> Set["AggregateElement"]:
            nonlocal J_elements

            if J_elements is None:
                J_elements = {element for element in elements if element.satisfied(J)}
            return J_elements

        def get_propagation_result(op: RelOp, bound: "Term", domain: Set["AggregateElement"]) -> bool:
            nonlocal propagation_cache

            if (op, bound) not in propagation_cache:
                propagation_cache[(op, bound)] = op2rel[op](
                    self.eval({element.terms for element in domain}), bound
                ).eval()
            return propagation_cache[(op, bound)]

        # running boolean tracking the current result of the propagation
        res = True

        for guard in guards:
            if guard is None:
                continue
            if res == False:
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
                res &= get_propagation_result(op, bound, get_I_elements())
            elif op == RelOp.EQUAL:
                # check upper and lower bound
                res &= get_propagation_result(RelOp.GREATER_OR_EQ, bound, get_J_elements()) and get_propagation_result(
                    RelOp.LESS_OR_EQ, bound, get_I_elements()
                )
            elif op == RelOp.UNEQUAL:
                # check upper or lower bound as well as whether or not J satisfies any elements that are not satisfied under I
                res &= get_propagation_result(RelOp.GREATER, bound, get_J_elements()) or get_propagation_result(
                    RelOp.LESS, bound, get_I_elements()
                )

        return res


class AggregateSum(AggregateFunction):
    """Represents a 'sum' aggregate."""

    def __str__(self) -> str:
        return f"#sum"

    def __eq__(self, other: Expr) -> bool:
        return isinstance(other, AggregateSum)

    def __hash__(self) -> int:
        return hash(("aggregate sum"))

    def eval(self, elements: Set["TermTuple"], positive: bool = True, negative: bool = True) -> Number:

        # empty tuple set
        if not elements or (positive == negative == False):
            return self.base()

        # non-empty set
        return Number(
            sum(
                (element.pos_weight if positive else 0) + (element.neg_weight if negative else 0)
                for element in elements
            )
        )

    def base(self) -> Number:
        # TODO: correct?
        return Number(0)

    def propagate(
        self,
        guards: Tuple[Optional[Guard], Optional[Guard]],
        elements: Set["AggregateElement"],
        I: Set["Literal"],
        J: Set["Literal"],
    ) -> bool:

        # cache holding intermediate results (to avoid recomputation)
        propagation_cache = dict()
        # elements that are satisfied by I and J, respectively (initialize to None)
        I_elements = None
        J_elements = None

        def get_I_elements() -> Set["AggregateElement"]:
            nonlocal I_elements

            if I_elements is None:
                I_elements = {element for element in elements if element.satisfied(I)}
            return I_elements

        def get_J_elements() -> Set["AggregateElement"]:
            nonlocal J_elements

            if J_elements is None:
                J_elements = {element for element in elements if element.satisfied(J)}
            return J_elements

        def get_propagation_result(
            op: RelOp,
            bound: "Term",
            adjust: int,
            domain: Set["AggregateElement"],
            positive: bool = True,
            negative: bool = True,
        ) -> bool:
            nonlocal propagation_cache

            if (op, bound, adjust, positive, negative) not in propagation_cache:
                propagation_cache[(op, bound, adjust, positive, negative)] = op2rel[op](
                    Number(self.eval({element.terms for element in domain}, positive, negative).val + adjust), bound
                ).eval()
            return propagation_cache[(op, bound, adjust, positive, negative)]

        def propagate_subset(
            op, bound: "Term", I_elements: Set["AggregateElement"], J_elements: Set["AggregateElement"]
        ) -> bool:
            # compute baseline value
            J_terms = {element.terms for element in J_elements}
            baseline = self.eval(J_terms)
            # get all elements that would change the baseline value (to reduce number of possible subsets to test)
            candidate_terms = {
                element.terms for element in I_elements if (element not in J and element.weight != 0)
            } - J_terms

            # test all combinations of subsets of candidates
            return any(op2rel[op](bound, baseline + self.eval(X)).eval() for X in powerset(candidate_terms))

        # running boolean tracking the current result of the propagation
        res = True

        for guard in guards:
            if guard is None:
                continue
            if res == False:
                break

            op, bound, right = guard

            # move operator to right-hand side (for canonical processing)
            if not right:
                op = -op

            if op in {RelOp.GREATER, RelOp.GREATER_OR_EQ}:
                res &= get_propagation_result(
                    op,
                    bound,
                    sum(min(element.weight, 0) for element in get_I_elements()),
                    get_J_elements(),
                    negative=False,
                )
            elif op in {RelOp.LESS, RelOp.LESS_OR_EQ}:
                res &= get_propagation_result(
                    op,
                    bound,
                    sum(max(element.weight, 0) for element in get_I_elements()),
                    get_J_elements(),
                    positive=False,
                )
            elif op == RelOp.EQUAL:
                # check upper and lower bound
                res &= (
                    get_propagation_result(
                        RelOp.GREATER_OR_EQ,
                        bound,
                        sum(min(element.weight, 0) for element in get_I_elements()),
                        get_J_elements(),
                        negative=False,
                    )
                    and get_propagation_result(
                        RelOp.LESS_OR_EQ,
                        bound,
                        sum(max(element.weight, 0) for element in get_I_elements()),
                        get_J_elements(),
                        positive=False,
                    )
                    and propagate_subset(RelOp.EQUAL, bound, get_J_elements(), get_I_elements())
                )
            elif op == RelOp.UNEQUAL:
                # check upper or lower bound as well as whether or not J satisfies any elements that are not satisfied under I
                res &= (
                    get_propagation_result(
                        RelOp.GREATER,
                        bound,
                        sum(min(element.weight, 0) for element in get_I_elements()),
                        get_J_elements(),
                        negative=False,
                    )
                    or get_propagation_result(
                        RelOp.LESS,
                        bound,
                        sum(max(element.weight, 0) for element in get_I_elements()),
                        get_J_elements(),
                        positive=False,
                    )
                    or not propagate_subset(RelOp.EQUAL, bound, get_I_elements(), get_J_elements())
                )

        return res


class AggregateMin(AggregateFunction):
    """Represents a 'minimum' aggregate."""

    def __str__(self) -> str:
        return f"#min"

    def __eq__(self, other: Expr) -> bool:
        return isinstance(other, AggregateMin)

    def __hash__(self) -> int:
        return hash(("aggregate min"))

    def eval(self, elements: Set["TermTuple"]) -> Number:
        # return minimum first term across all non-empty elements
        # NOTE: includes 'Supremum' in case all elements are empty
        return reduce(
            lambda t1, t2: t2 if not t1.precedes(t2) else t1,
            (self.base(), *tuple(element[0] for element in elements if element)),
        )

    def base(self) -> Supremum:
        return Supremum()

    def propagate(
        self,
        guards: Tuple[Optional[Guard], Optional[Guard]],
        elements: Set["AggregateElement"],
        I: Set["Literal"],
        J: Set["Literal"],
    ) -> bool:

        # cache holding intermediate results (to avoid recomputation)
        propagation_cache = dict()
        # elements that are satisfied by I and J, respectively (initialize to None)
        I_elements = None
        J_elements = None

        def get_I_elements() -> Set["AggregateElement"]:
            nonlocal I_elements

            if I_elements is None:
                I_elements = {element for element in elements if element.satisfied(I)}
            return I_elements

        def get_J_elements() -> Set["AggregateElement"]:
            nonlocal J_elements

            if J_elements is None:
                J_elements = {element for element in elements if element.satisfied(J)}
            return J_elements

        def get_propagation_result(op: RelOp, bound: "Term", domain: Set["AggregateElement"]) -> bool:
            nonlocal propagation_cache

            if (op, bound) not in propagation_cache:
                propagation_cache[(op, bound)] = op2rel[op](
                    self.eval({element.terms for element in domain}), bound
                ).eval()
            return propagation_cache[(op, bound)]

        def propagate_subset(
            op, bound, I_elements: Set["AggregateElement"], J_elements: Set["AggregateElement"]
        ) -> bool:
            # compute baseline value
            baseline = self.eval({element.terms for element in J})
            # get all elements that would change the baseline value (to reduce number of possible subsets to test)
            candidates = {
                element for element in I_elements if (element.terms and not element.terms[0].precedes(baseline))
            }

            # test all combinations of subsets of candidates
            for X in powerset(candidates):
                value = self.eval({element.terms for element in X})

                if op2rel[op](bound, (value if not baseline.precedes(value) else baseline)).eval():
                    return True

            return False

        # running boolean tracking the current result of the propagation
        res = True

        for guard in guards:
            if guard is None:
                continue
            if res == False:
                break

            op, bound, right = guard

            # move operator to right-hand side (for canonical processing)
            if not right:
                op = -op

            if op in {RelOp.LESS, RelOp.LESS_OR_EQ}:
                # check upper bound
                res &= get_propagation_result(op, bound, get_J_elements())
            elif op in {RelOp.GREATER, RelOp.GREATER_OR_EQ}:
                # check lower bound
                res &= get_propagation_result(op, bound, get_I_elements())
            elif op == RelOp.EQUAL:
                # check upper and lower bound
                res &= (
                    get_propagation_result(RelOp.GREATER_OR_EQ, bound, get_I_elements())
                    and get_propagation_result(RelOp.LESS_OR_EQ, bound, get_J_elements())
                    and propagate_subset(RelOp.EQUAL, bound, J_elements, I_elements)
                )
            elif op == RelOp.UNEQUAL:
                # check upper or lower bound as well as whether or not J satisfies any elements that are not satisfied under I
                res &= (
                    get_propagation_result(RelOp.GREATER, bound, get_I_elements())
                    or get_propagation_result(RelOp.LESS, bound, get_J_elements())
                    or not propagate_subset(RelOp.EQUAL, bound, I_elements, J_elements)
                )

        return res


class AggregateMax(AggregateFunction):
    """Represents a 'maximum' aggregate."""

    def __str__(self) -> str:
        return f"#max"

    def __eq__(self, other: Expr) -> bool:
        return isinstance(other, AggregateMax)

    def __hash__(self) -> int:
        return hash(("aggregate max"))

    def eval(self, elements: Set["TermTuple"]) -> Number:
        # return maximum first term across all non-empty elements
        # NOTE: includes 'Infimum' in case all elements are empty
        return reduce(
            lambda t1, t2: t2 if not t2.precedes(t1) else t1,
            (self.base(), *tuple(element[0] for element in elements if element)),
        )

    def base(self) -> Infimum:
        return Infimum()

    def propagate(
        self,
        guards: Tuple[Optional[Guard], Optional[Guard]],
        elements: Set["AggregateElement"],
        I: Set["Literal"],
        J: Set["Literal"],
    ) -> bool:

        # cache holding intermediate results (to avoid recomputation)
        propagation_cache = dict()
        # elements that are satisfied by I and J, respectively (initialize to None)
        I_elements = None
        J_elements = None

        def get_I_elements() -> Set["AggregateElement"]:
            nonlocal I_elements

            if I_elements is None:
                I_elements = {element for element in elements if element.satisfied(I)}
            return I_elements

        def get_J_elements() -> Set["AggregateElement"]:
            nonlocal J_elements

            if J_elements is None:
                J_elements = {element for element in elements if element.satisfied(J)}
            return J_elements

        def get_propagation_result(op: RelOp, bound: "Term", domain: Set["AggregateElement"]) -> bool:
            nonlocal propagation_cache

            if (op, bound) not in propagation_cache:
                propagation_cache[(op, bound)] = op2rel[op](
                    self.eval({element.terms for element in domain}), bound
                ).eval()
            return propagation_cache[(op, bound)]

        def propagate_subset(
            op, bound, I_elements: Set["AggregateElement"], J_elements: Set["AggregateElement"]
        ) -> bool:
            # compute baseline value
            baseline = self.eval({element.terms for element in J})
            # get all elements that would change the baseline value (to reduce number of possible subsets to test)
            candidates = {
                element for element in I_elements if (element.terms and not element.terms[0].precedes(baseline))
            }

            # test all combinations of subsets of candidates
            for X in powerset(candidates):
                value = self.eval({element.terms for element in X})

                if op2rel[op](bound, (value if not value.precedes(baseline) else baseline)).eval():
                    return True

            return False

        # running boolean tracking the current result of the propagation
        res = True

        for guard in guards:

            if guard is None:
                continue
            if res == False:
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
                res &= get_propagation_result(op, bound, get_I_elements())
            elif op == RelOp.EQUAL:
                # check upper and lower bound
                res &= (
                    get_propagation_result(RelOp.GREATER_OR_EQ, bound, get_J_elements())
                    and get_propagation_result(RelOp.LESS_OR_EQ, bound, get_I_elements())
                    and propagate_subset(RelOp.EQUAL, bound, J_elements, I_elements)
                )
            elif op == RelOp.UNEQUAL:
                # check upper or lower bound as well as whether or not J satisfies any elements that are not satisfied under I
                res &= (
                    get_propagation_result(RelOp.GREATER, bound, get_J_elements())
                    or get_propagation_result(RelOp.LESS, bound, get_I_elements())
                    or not propagate_subset(RelOp.EQUAL, bound, I_elements, J_elements)
                )

        return res


class AggregateLiteral(Literal):
    """Represents an aggregate literal."""

    def __init__(
        self,
        func: AggregateFunction,
        elements: Tuple[AggregateElement, ...],
        guards: Union[Guard, Tuple[Guard, ...]],
        naf: bool = False,
    ) -> None:
        super().__init__(naf)

        # initialize left and right guard to 'None'
        self.lguard, self.rguard = None, None

        # single guard specified
        if isinstance(guards, Guard):
            # wrap in tuple
            guards = (guards,)
        # guard tuple specified
        elif isinstance(guards, Tuple) and len(guards) not in {1, 2}:
            raise ValueError("Aggregate requires at least one and at most two guards to be specified.")

        # process guards
        for guard in guards:
            if guard is None:
                continue

            if guard.right:
                if self.rguard is not None:
                    raise ValueError("Multiple right guards specified for aggregate.")
                self.rguard = guard
            else:
                if self.lguard is not None:
                    raise ValueError("Multiple right guards specified for aggregate.")
                self.lguard = guard

        self.func = func
        self.elements = elements

    def __str__(self) -> str:
        return (
            ("not " if self.naf else "")
            + f"{f'{str(self.lguard.bound)} {self.lguard.op} ' if self.lguard is not None else ''}{str(self.func)}{{{';'.join([str(element) for element in self.elements])}}}{f' {str(self.rguard.op)} {str(self.rguard.bound)}' if self.rguard is not None else ''}"
        )

    def __eq__(self, other: "Expr") -> bool:
        return (
            isinstance(other, AggregateLiteral)
            and self.func == other.func
            and set(self.elements) == set(other.elements)
            and self.guards == other.guards
        )

    def __hash__(self) -> int:
        return hash(("aggr literal", self.func, self.elements, self.guards))

    @cached_property
    def ground(self) -> bool:
        return (
            (self.lguard.bound.ground if self.lguard is not None else True)
            and (self.rguard.bound.ground if self.rguard is not None else True)
            and all(element.ground for element in self.elements)
        )

    def set_naf(self, value: bool = True) -> None:
        self.naf = value

    def pos_occ(self) -> Set["PredicateLiteral"]:
        return set().union(*tuple(element.pos_occ() for element in self.elements))

    def neg_occ(self) -> Set["PredicateLiteral"]:
        return set().union(*tuple(element.neg_occ() for element in self.elements))

    @property
    def guards(self) -> Tuple[Union[Guard, None], Union[Guard, None]]:
        return (self.lguard, self.rguard)

    def invars(self) -> Set["Variable"]:
        return set().union(
            *tuple(element.vars() for element in self.elements)
        )  # TODO: does not quite follow the definition in ASP-Core-2?

    def outvars(self) -> Set["Variable"]:
        return set().union(*tuple(guard.bound.vars() for guard in self.guards if guard is not None))

    def vars(self, global_only: bool = False) -> Set["Variable"]:
        return self.outvars() if global_only else self.invars().union(self.outvars())

    def eval(self) -> bool:
        if not self.ground:
            raise ValueError("Cannot evaluate non-ground aggregate.")

        # evaluate aggregate function
        aggr_term = self.func.eval({element.terms for element in self.elements})

        # check guards
        return (op2rel[self.lguard.op](self.lguard.bound, aggr_term).eval() if self.lguard is not None else True) and (
            op2rel[self.rguard.op](aggr_term, self.rguard.bound).eval() if self.rguard is not None else True
        )

    def safety(
        self, rule: Optional[Union["Statement", "Query"]] = None, global_vars: Optional[Set["Variable"]] = None
    ) -> SafetyTriplet:

        if global_vars is None:
            if rule is None:
                raise AttributeError(
                    "Computing safety characterization for 'AggregateLiteral' requires a reference to the encompassing rule or the set of global variables in it."
                )

            # get global variables from rule
            global_vars = rule.vars(global_only=True)

        # set of global variables that appear inside the aggregate
        aggr_global_invars = self.invars().intersection(global_vars)
        aggr_global_vars = aggr_global_invars.union(self.outvars())

        guard_safeties = []

        for guard in self.guards:
            # guard not specified
            if guard is None:
                continue
            elif str(guard.op) != "=":  # TODO: cannot compare to enum directly due to circular imports
                guard_safeties.append(SafetyTriplet(unsafe=aggr_global_vars))
            else:
                # compute safety characterization w.r.t. left term guard
                guard_safeties.append(
                    SafetyTriplet(
                        unsafe=aggr_global_vars,  # global inner variables and variables in guard term
                        rules=set([SafetyRule(var, aggr_global_invars) for var in guard.bound.safety().safe]),
                    ).normalize()
                )

        # TODO: can be simplified?
        if len(guard_safeties) == 1:
            return guard_safeties[0]
        # both guards specified
        else:
            return SafetyTriplet.closure(guard_safeties)

    def substitute(self, subst: "Substitution") -> "AggregateLiteral":
        # substitute guard terms recursively
        guards = tuple(guard.substitute(subst) if guard is not None else None for guard in self.guards)

        return AggregateLiteral(
            self.func, tuple(element.substitute(subst) for element in self.elements), guards, naf=self.naf
        )

    def match(self, other: Expr) -> Set["Substitution"]:
        raise Exception("Matching for aggregate literals not supported yet.")

    def replace_arith(self, var_table: "VariableTable") -> "AggregateLiteral":
        # replace guards
        guards = (None if guard is None else guard.replace_arith(var_table) for guard in self.guards)

        return AggregateLiteral(
            self.func, tuple(element.replace_arith(var_table) for element in self.elements), guards, self.naf
        )


# maps aggregate operators/functions to their corresponding AST constructs
op2aggr = {AggrOp.COUNT: AggregateCount, AggrOp.SUM: AggregateSum, AggrOp.MIN: AggregateMin, AggrOp.MAX: AggregateMax}
