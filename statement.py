from typing import Tuple, Dict
from abc import ABC, abstractmethod
from dataclasses import dataclass

from term import Term
from atom import ClassicalAtom
from aggregate import AggregateLiteral
from disjunction import Disjunction
from conjunction import Conjunction

from tables import VariableTable


# TODO: provide an substitute method assigning values to variables
# should raise error if not valid (e.g. string in arithmetical term)
# whenever we have a variable in a statement -> register
# how to substitute ?
# Maybe everything that can receive a variable -> hold off

# substitute_callback:


class Statement(ABC):
    """Abstract base class for all statements."""
    def __init__(self) -> None:
        # initialize variable table
        self.vars = VariableTable()

    @abstractmethod # TODO: must also be implemented by Disjunction, Conjunction and Elements
    def substitute(self, subst: Dict[str, Term]) -> "Statement":
        """substitutes the statement by replacing all variables with assigned terms."""
        pass

    def set_variable_table(self, var_table: VariableTable) -> None:
        self.vars = VariableTable


@dataclass
class Rule(Statement, ABC):
    head: Disjunction
    body: Conjunction
    """Abstract base class for all rules."""
# for rules:
#   issafe ?
#   istight ?


class Fact(Rule, ABC):
    """Abstract base class for all facts."""
    def __init__(self, head: Disjunction) -> None:
        super().__init__(head, Conjunction)


class NormalFact(Fact):
    """Normal fact."""
    def __init__(self, head: ClassicalAtom) -> None:
        super().__init__(tuple([head]))

    def substitute(self, subst: Dict[str, Term]) -> "NormalFact":
        return NormalFact(
            self.head.substitute(subst),
            self.body.substitute(subst)
        )

    def __repr__(self) -> str:
        return f"NormalFact[{repr(self.head)}]"

    def __str__(self) -> str:
        return f"{str(self.head)}."


class DisjunctiveFact(Fact):
    """Disjunctive fact.
    
    Rule of form:

        h_1 | ... | h_m :- .

    or simply

        h_1 | ... | h_m .
    
    for classical atoms h_1,...,h_m.
    """
    def __init__(self, head: Disjunction) -> None:
        super().__init__(head)

    def substitute(self, subst: Dict[str, Term]) -> "DisjunctiveFact":
        return DisjunctiveFact(
            self.head.substitute(subst),
            self.body.substitute(subst)
        )

    def __repr__(self) -> str:
        return f"DisjunctiveFact[{repr(self.head)}]"

    def __str__(self) -> str:
        return f"{str(self.head)}."


class ChoiceFact(Fact):
    """Choice fact."""
    def __init__(self, head: Disjunction, lb: int=0, ub: int=-1) -> None:
        super().__init__(head)

        if(ub == -1):
            ub = len(head)

        self.lb = lb
        self.ub = ub

    def substitute(self, subst: Dict[str, Term]) -> "ChoiceFact":
        return ChoiceFact(
            self.head.substitute(subst),
            self.body.substitute(subst),
            self.lb,
            self.ub
        )

    def __repr__(self) -> str:
        return f"ChoiceFact[{repr(self.head)}]"

    def __str__(self) -> str:
        return f"{{{','.join([str(literal) for literal in self.head.literals])}}}."


class NormalRule(Rule):
    """Normal rule.

    Rule of form:

        h :- b_1, ..., b_n .

    for a classical atom h and literals b_1,...,b_n.
    """
    def __init__(self, head: ClassicalAtom, body: Disjunction) -> None:
        super().__init__(Disjunction([head]), body)

    def substitute(self, subst: Dict[str, Term]) -> "NormalRule":
        return NormalRule(
            self.head.substitute(subst),
            self.body.substitute(subst)
        )

    def __repr__(self) -> str:
        return f"NormalRule[{repr(self.head)}]({repr(self.body)})"

    def __str__(self) -> str:
        return f"{str(self.head)} :- {str(self.body)}."


class DisjunctiveRule(Rule):
    """Disjunctive rule.
    
    Rule of form:

        h_1 | ... | h_m :- b_1,...,b_n .

    for classical atoms h_1,...,h_m and literals b_1,...,b_n.
    """
    def substitute(self, subst: Dict[str, Term]) -> "DisjunctiveRule":
        return DisjunctiveFact(
            self.head.substitute(subst),
            self.body.substitute(subst)
        )

    def __repr__(self) -> str:
        return f"DisjunctiveRule[{repr(self.head)}]({repr(self.body)})"

    def __str__(self) -> str:
        return f"{str(self.head)} :- {str(self.body)}."


class ChoiceRule(Rule):
    """Choice rule.

    Rule of form:

        t R { h_1 ; ... ; h_m } S u :- b_1,...,b_n .

    for classical atoms h_1,...,h_m, literals b_1,...,b_n, terms t,u and binary relation operators R,S.
    """
    def __init__(self, head: ClassicalAtom, body: Disjunction, lb=1, ub=-1) -> None:
        super().__init__(head, body)

        # TODO: generalize to two relation operators

        if(ub == -1):
            ub = len(head)

        self.lb = lb
        self.ub = ub

        # TODO: parse relation operators and check for validity ?
    
    def __repr__(self) -> str:
        return f"ChoiceRule[{repr(self.head)}]({repr(self.body)})"

    def __str__(self) -> str:
        return f"{{{','.join([str(literal) for literal in self.head.literals])}}} :- {str(self.body)}."

    def substitute(self, subst: Dict[str, Term]) -> "ChoiceFact":
        return ChoiceFact(
            self.head.substitute(subst),
            self.body.substitute(subst),
            self.lb,
            self.ub
        )

    def transform(self) -> Tuple[NormalRule, ...]:
        """TODO"""
        # Choice rule (0 <= and <= m) -> translated to 2m+1 normal rules
        # what about other bounds/relations ?
        pass


# TODO: cardinality rules? not part of standard (syntactic sugar?)
# TODO: weight rules? not part of standard (syntactic sugar?)

class Constraint(Rule): # TODO: not inherit from rule ?
    """Constraint.

    Rule of form:

        :- b_1,...,b_n .

    for literals b_1,...,b_n.
    """
    def __init__(self, body: Conjunction) -> None:
        super().__init__(Disjunction(), body)

    def __repr__(self) -> str:
        return f"Constraint({repr(self.body)})"

    def __str__(self) -> str:
        return f":- {str(self.body)}."

    def substitute(self, subst: Dict[str, Term]) -> "Constraint":
        return Constraint(
            self.body.substitute(subst)
        )

    def transform(self) -> Tuple[NormalRule]:
        # TODO
        raise Exception("Transformation of constraints not supported yet.")


class WeakConstraint(Rule): # TODO: not inherit from rule ?
    """Weak constraint.

    Rule of form:

        :~ b_1,...,b_n . [ w@l,t_1,...,t_m ]

    for literals b_1,...,b_n and terms w,l,t_1,...,t_m.
    '@ l' may be omitted if l=0.
    """
    def __init__(self, body: Conjunction, weight: Term, level: Term, terms: Tuple[Term, ...]) -> None: # TODO: type 'w_at_l'
        super().__init__(Disjunction(), body)
        self.weight = weight
        self.level = level
        self.terms = terms

    def __repr__(self) -> str:
        return f"WeakConstraint({repr(self.body)})"

    def __str__(self) -> str:
        return f":~ {str(self.body)}."

    def substitute(self, subst: Dict[str, Term]) -> "WeakConstraint":
        return WeakConstraint(
            self.body.substitute(subst),
            self.weight.substitute(subst),
            self.level.substitute(subst),
            self.terms.substitute(subst)
        )

    def transform(self) -> Tuple["WeakConstraint", ...]:
        """Handles any aggregates in the constraint body."""

        pos_aggr_ids = []
        neg_aggr_ids = []

        for i, term in enumerate(self.body):
            if isinstance(term, AggregateLiteral):
                if term.neg:
                    # TODO
                    pass
                else:
                    pass

                # TODO: check if aggregate is NOT
                # TODO: call transform on resulting weak constraints to handle additional aggregates!
                break
        
        raise Exception("Transformation of weak constraints is not supported yet.")


@dataclass
class OptimizeElement: # TODO: inherit expression?
    """Optimization element for optimize statements.
    
    Expression of form:

        w @ l,t_1,...,t_m : b_1,...,b_n

    for terms w,l,t_1,...,t_m and literals b_1,...,b_n.
    '@ l' may be omitted if l=0.
    """
    weight: Term
    level: Term
    terms: Tuple[Term]
    literals: Conjunction # TODO: conjunction=tuple[literal]

    def __repr__(self) -> str:
        return f"OptimizeElement({repr(self.weight)}@{repr(self.level)},{','.join([repr(term) for term in self.terms])}:{','.join([repr(literal) for literal in self.literals])})"

    def __str__(self) -> str:
        return f"{str(self.weight)}@{str(self.level)},{','.join([str(term) for term in self.terms])}:{','.join([str(literal) for literal in self.literals])}"

    def substitute(self, subst: Dict[str, Term]) -> "OptimizeElement":
        return OptimizeElement(
            self.weight.substitute(subst),
            self.level.substitute(subst),
            self.terms.substitute(subst),
            self.literals.substitute(subst)
        )


@dataclass
class OptimizeStatement(Statement, ABC):
    """Abstract base class for all optimize statement."""
    elements: Tuple[OptimizeElement, ...]
    minimize: bool

    def transform(self) -> Tuple[WeakConstraint, ...]:
        """Transforms the optimize statement into (possibly multiple) weak constraints."""
        # transform each optimize element into a weak constraint
        return tuple(
            WeakConstraint(
                element.literals,
                element.weight,
                element.level,
                element.terms
            )
            for element in self.elements
        )


class MinimizeStatement(OptimizeStatement):
    """Minimize statement.

    Statement of the form:

        #minimize{w_1@l_1,t_{11},...,t_{1m}:b_{11},...,b_{1n};...;w_k@l_k,t_{k1},...,t_{km}:b_{k1},...,b_{kn}}

    for literals b_{11},...,b_{1n},...,b_{k1},...,b_{kn} and terms w_1,...,w_k,l_1,...,l_k,t_{11},...,t_{1m},t_{k1},...,t_{km}.

    Can alternatively be written as multiple weak constraints:

        :~ b_{11},...,b_{1n}. [w_1@l_1,t_{11},...,t_{1m}]
        ...
        :~ b_{k1},...,b_{kn}. [w_k@l_1,t_{k1},...,t_{km}]
    """
    def __init__(self, elements: Tuple[OptimizeElement, ...]) -> None:
        super().__init__(elements, True)

    def __repr__(self) -> str:
        return f"Minimize({','.join([repr(element) for element in self.elements])})"

    def __str__(self) -> str:
        return f"#minimize{{{';'.join([str(element) for element in self.elements])}}}"

    def substitute(self, subst: Dict[str, Term]) -> "MinimizeStatement":
        return OptimizeStatement(
            self.elements.substitute(subst)
        )


class MaximizeStatement(OptimizeStatement):
    """Maximize statement.

    Statement of the form:

        #maximize{w_1@l_1,t_{11},...,t_{1m}:b_{11},...,b_{1n};...;w_k@l_k,t_{k1},...,t_{km}:b_{k1},...,b_{kn}}

    for literals b_{11},...,b_{1n},...,b_{k1},...,b_{kn} and terms w_1,...,w_k,l_1,...,l_k,t_{11},...,t_{1m},t_{k1},...,t_{km}.

    Can alternatively be written as multiple weak constraints:

        :~ b_{11},...,b_{1n}. [-w_1@l_1,t_{11},...,t_{1m}]
        ...
        :~ b_{k1},...,b_{kn}. [-w_k@l_1,t_{k1},...,t_{km}]
    """
    def __init__(self, elements: Tuple[OptimizeElement, ...]) -> None:
        super().__init__(elements, False)

    def __repr__(self) -> str:
        return f"Maximize({','.join([repr(element) for element in self.elements])})"

    def __str__(self) -> str:
        return f"#maximize{{{';'.join([str(element) for element in self.elements])}}}"

    def substitute(self, subst: Dict[str, Term]) -> "MaximizeStatement":
        return MaximizeStatement(
            self.elements.substitute(subst)
        )